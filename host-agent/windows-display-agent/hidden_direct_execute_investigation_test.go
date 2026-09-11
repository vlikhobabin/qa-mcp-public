package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func investigationHash(character byte) string {
	return strings.Repeat(string(character), 64)
}

func validInvestigationReceipt() hiddenDirectInvestigationReceipt {
	return hiddenDirectInvestigationReceipt{
		Schema:          hiddenDirectInvestigationSchema,
		RunKind:         "s4-diagnostic",
		ArgvSHA256:      investigationHash('a'),
		EnvironmentHash: investigationHash('b'),
		FixtureSHA256:   investigationHash('c'),
		Samples: []hiddenDirectInvestigationSample{
			{OffsetMilliseconds: 0, Stage: "launch", ProcessPID: 101, ProcessAlive: true, ProcessInJob: true, DesktopHash: investigationHash('d')},
			{OffsetMilliseconds: 250, Stage: "listener_ready", ProcessPID: 101, ListenerPID: 102, ProcessAlive: true, ProcessInJob: true, ListenerReady: true, DesktopHash: investigationHash('d')},
			{OffsetMilliseconds: 500, Stage: "main_window", ProcessPID: 101, ListenerPID: 102, ProcessAlive: true, ProcessInJob: true, ListenerReady: true, DesktopHash: investigationHash('d'), TopLevelWindowCount: 1, AllowlistedClasses: []string{"V8TopLevelFrameSDI"}, OwnerRelation: "root"},
		},
		Terminal: hiddenDirectInvestigationTerminal{Status: "main_admitted", MainAdmitted: true},
		Cleanup:  hiddenDirectInvestigationCleanup{Complete: true, OwnedTaskCount: 0, OwnedStageCount: 0, OwnedProcessCount: 0, OwnedDesktopCount: 0, OwnedTPortCount: 0, ProtectedStateUnchanged: true},
	}
}

func TestHiddenDirectInvestigationReceiptAcceptsBoundedStructuralEvidence(t *testing.T) {
	receipt := validInvestigationReceipt()
	if err := validateHiddenDirectInvestigationReceipt(receipt); err != nil {
		t.Fatalf("valid investigation receipt rejected: %v", err)
	}
	data, err := json.Marshal(receipt)
	if err != nil {
		t.Fatal(err)
	}
	for _, forbidden := range []string{"caption", "credential", "password", "raw_path", "screenshot", "ui_text", "connection_string"} {
		if strings.Contains(strings.ToLower(string(data)), forbidden) {
			t.Fatalf("privacy-forbidden field reached receipt: %s", forbidden)
		}
	}
}

func TestHiddenDirectInvestigationReceiptRejectsHostileRows(t *testing.T) {
	tests := map[string]func(*hiddenDirectInvestigationReceipt){
		"raw path field via invalid run kind": func(value *hiddenDirectInvestigationReceipt) { value.RunKind = `C:\\private\\run.epf` },
		"oversized samples": func(value *hiddenDirectInvestigationReceipt) {
			value.Samples = make([]hiddenDirectInvestigationSample, hiddenDirectInvestigationSampleLimit+1)
		},
		"non-monotonic samples": func(value *hiddenDirectInvestigationReceipt) { value.Samples[2].OffsetMilliseconds = 100 },
		"unknown stage":         func(value *hiddenDirectInvestigationReceipt) { value.Samples[1].Stage = "retry_as_success" },
		"enumeration error admitted": func(value *hiddenDirectInvestigationReceipt) {
			value.Samples[1].EnumerationError = "ERROR_INVALID_DATA"
		},
		"main admitted without main class": func(value *hiddenDirectInvestigationReceipt) {
			value.Samples[2].AllowlistedClasses = nil
		},
		"main admitted with wrong owner": func(value *hiddenDirectInvestigationReceipt) {
			value.Samples[2].OwnerRelation = "owned"
		},
		"main admitted with dead process": func(value *hiddenDirectInvestigationReceipt) {
			value.Samples[2].ProcessAlive = false
		},
		"main admitted with process outside job": func(value *hiddenDirectInvestigationReceipt) {
			value.Samples[2].ProcessInJob = false
		},
		"main admitted before listener readiness": func(value *hiddenDirectInvestigationReceipt) {
			value.Samples[2].ListenerReady = false
		},
		"main admitted outside main window stage": func(value *hiddenDirectInvestigationReceipt) {
			value.Samples[2].Stage = "window_inventory"
		},
		"main admitted with zero structural windows": func(value *hiddenDirectInvestigationReceipt) {
			value.Samples[2].TopLevelWindowCount = 0
		},
		"missing terminal outcome": func(value *hiddenDirectInvestigationReceipt) {
			value.Terminal = hiddenDirectInvestigationTerminal{}
		},
		"incomplete cleanup":      func(value *hiddenDirectInvestigationReceipt) { value.Cleanup.Complete = false },
		"owned residue":           func(value *hiddenDirectInvestigationReceipt) { value.Cleanup.OwnedDesktopCount = 1 },
		"protected state changed": func(value *hiddenDirectInvestigationReceipt) { value.Cleanup.ProtectedStateUnchanged = false },
	}
	for name, mutate := range tests {
		t.Run(name, func(t *testing.T) {
			value := validInvestigationReceipt()
			mutate(&value)
			if validateHiddenDirectInvestigationReceipt(value) == nil {
				t.Fatal("hostile investigation receipt accepted")
			}
		})
	}
}

func TestHiddenDirectInvestigationDecisionIsExclusiveAndResumable(t *testing.T) {
	valid := hiddenDirectInvestigationDecision{Kind: "replacement-card", EvidenceSHA256: investigationHash('e'), SuccessorCard: "oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle"}
	if err := validateHiddenDirectInvestigationDecision(valid); err != nil {
		t.Fatalf("valid decision rejected: %v", err)
	}
	for _, invalid := range []hiddenDirectInvestigationDecision{
		{},
		{Kind: "retry-until-success", EvidenceSHA256: investigationHash('e'), ResumeCondition: "retry"},
		{Kind: "not-verifiable", EvidenceSHA256: investigationHash('e')},
		{Kind: "replacement-card", EvidenceSHA256: investigationHash('e')},
		{Kind: "runbook-correction", EvidenceSHA256: investigationHash('e'), ResumeCondition: "unexpected second decision"},
	} {
		if validateHiddenDirectInvestigationDecision(invalid) == nil {
			t.Fatalf("invalid decision accepted: %#v", invalid)
		}
	}
}

func TestHiddenDirectInvestigationHasNoProductionCaller(t *testing.T) {
	entries, err := os.ReadDir(".")
	if err != nil {
		t.Fatal(err)
	}
	for _, entry := range entries {
		if entry.IsDir() || !strings.HasSuffix(entry.Name(), ".go") || strings.HasSuffix(entry.Name(), "_test.go") {
			continue
		}
		data, readErr := os.ReadFile(filepath.Clean(entry.Name()))
		if readErr != nil {
			t.Fatal(readErr)
		}
		for _, symbol := range []string{"hiddenDirectInvestigationReceipt", "validateHiddenDirectInvestigationReceipt", "hiddenDirectInvestigationDecision"} {
			if strings.Contains(string(data), symbol) {
				t.Fatalf("test-only investigation symbol %s has production caller in %s", symbol, entry.Name())
			}
		}
	}
}
