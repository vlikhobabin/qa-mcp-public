package main

import (
	"errors"
	"strings"
)

const (
	hiddenDirectInvestigationSchema      = "qa-mcp.hidden-direct-execute-investigation.v1"
	hiddenDirectInvestigationSampleLimit = 64
)

type hiddenDirectInvestigationSample struct {
	OffsetMilliseconds  uint32   `json:"offset_ms"`
	Stage               string   `json:"stage"`
	ProcessPID          uint32   `json:"process_pid"`
	ListenerPID         uint32   `json:"listener_pid,omitempty"`
	ProcessAlive        bool     `json:"process_alive"`
	ProcessInJob        bool     `json:"process_in_job"`
	ListenerReady       bool     `json:"listener_ready"`
	DesktopHash         string   `json:"desktop_hash"`
	TopLevelWindowCount uint16   `json:"top_level_window_count"`
	AllowlistedClasses  []string `json:"allowlisted_classes,omitempty"`
	OwnerRelation       string   `json:"owner_relation,omitempty"`
	EnumerationError    string   `json:"enumeration_error,omitempty"`
}

type hiddenDirectInvestigationTerminal struct {
	Status        string `json:"status"`
	MainAdmitted  bool   `json:"main_admitted"`
	ProcessExited bool   `json:"process_exited"`
	ExitCodeKnown bool   `json:"exit_code_known"`
	ExitCode      int32  `json:"exit_code,omitempty"`
}

type hiddenDirectInvestigationCleanup struct {
	Complete                bool   `json:"complete"`
	OwnedTaskCount          uint16 `json:"owned_task_count"`
	OwnedStageCount         uint16 `json:"owned_stage_count"`
	OwnedProcessCount       uint16 `json:"owned_process_count"`
	OwnedDesktopCount       uint16 `json:"owned_desktop_count"`
	OwnedTPortCount         uint16 `json:"owned_tport_count"`
	ProtectedStateUnchanged bool   `json:"protected_state_unchanged"`
}

type hiddenDirectInvestigationReceipt struct {
	Schema          string                            `json:"schema"`
	RunKind         string                            `json:"run_kind"`
	ArgvSHA256      string                            `json:"argv_sha256"`
	EnvironmentHash string                            `json:"environment_sha256"`
	FixtureSHA256   string                            `json:"fixture_sha256"`
	Samples         []hiddenDirectInvestigationSample `json:"samples"`
	Terminal        hiddenDirectInvestigationTerminal `json:"terminal"`
	Cleanup         hiddenDirectInvestigationCleanup  `json:"cleanup"`
}

type hiddenDirectInvestigationDecision struct {
	Kind            string `json:"kind"`
	EvidenceSHA256  string `json:"evidence_sha256"`
	ResumeCondition string `json:"resume_condition,omitempty"`
	SuccessorCard   string `json:"successor_card,omitempty"`
}

func hiddenDirectInvestigationHashValid(value string) bool {
	if len(value) != 64 || strings.ToLower(value) != value {
		return false
	}
	for _, character := range value {
		if !strings.ContainsRune("0123456789abcdef", character) {
			return false
		}
	}
	return true
}

func validateHiddenDirectInvestigationReceipt(value hiddenDirectInvestigationReceipt) error {
	allowedRunKinds := map[string]bool{"s3-control": true, "s4-diagnostic": true, "s4-uninstrumented": true}
	if value.Schema != hiddenDirectInvestigationSchema || !allowedRunKinds[value.RunKind] ||
		!hiddenDirectInvestigationHashValid(value.ArgvSHA256) ||
		!hiddenDirectInvestigationHashValid(value.EnvironmentHash) ||
		!hiddenDirectInvestigationHashValid(value.FixtureSHA256) ||
		len(value.Samples) == 0 || len(value.Samples) > hiddenDirectInvestigationSampleLimit {
		return errors.New("investigation receipt identity is invalid")
	}
	allowedStages := map[string]bool{"launch": true, "listener_ready": true, "window_inventory": true, "main_window": true, "child_exit": true, "cleanup": true}
	allowedClasses := map[string]bool{"V8TopLevelFrameSDI": true, "V8TopLevelFrameSDIsec": true, "V8ConfirmationWindowTaxi": true}
	allowedOwners := map[string]bool{"": true, "root": true, "owned": true}
	enumerationFailed := false
	mainStructurallyAdmitted := false
	for index, sample := range value.Samples {
		if (index > 0 && sample.OffsetMilliseconds <= value.Samples[index-1].OffsetMilliseconds) ||
			!allowedStages[sample.Stage] || sample.ProcessPID == 0 ||
			!hiddenDirectInvestigationHashValid(sample.DesktopHash) ||
			sample.TopLevelWindowCount > 128 || len(sample.AllowlistedClasses) > 3 ||
			!allowedOwners[sample.OwnerRelation] ||
			(sample.EnumerationError != "" && sample.EnumerationError != "ERROR_INVALID_DATA" && sample.EnumerationError != "ERROR_OTHER") {
			return errors.New("investigation sample is invalid")
		}
		for _, className := range sample.AllowlistedClasses {
			if !allowedClasses[className] {
				return errors.New("investigation window class is not allowlisted")
			}
		}
		if sample.ListenerReady && sample.ListenerPID == 0 {
			return errors.New("listener identity is missing")
		}
		if sample.Stage == "main_window" && sample.ProcessAlive && sample.ProcessInJob &&
			sample.ListenerReady && sample.TopLevelWindowCount > 0 && sample.OwnerRelation == "root" {
			for _, className := range sample.AllowlistedClasses {
				if className == "V8TopLevelFrameSDI" {
					mainStructurallyAdmitted = true
					break
				}
			}
		}
		enumerationFailed = enumerationFailed || sample.EnumerationError != ""
	}
	terminalValid := (value.Terminal.Status == "main_admitted" && value.Terminal.MainAdmitted && !value.Terminal.ProcessExited) ||
		(value.Terminal.Status == "process_exited" && !value.Terminal.MainAdmitted && value.Terminal.ProcessExited && value.Terminal.ExitCodeKnown) ||
		(value.Terminal.Status == "main_not_ready" && !value.Terminal.MainAdmitted && !value.Terminal.ProcessExited && !value.Terminal.ExitCodeKnown)
	if !terminalValid || (value.Terminal.MainAdmitted && !mainStructurallyAdmitted) ||
		(enumerationFailed && value.Terminal.MainAdmitted) {
		return errors.New("investigation terminal state is invalid")
	}
	if !value.Cleanup.Complete || !value.Cleanup.ProtectedStateUnchanged ||
		value.Cleanup.OwnedTaskCount != 0 || value.Cleanup.OwnedStageCount != 0 ||
		value.Cleanup.OwnedProcessCount != 0 || value.Cleanup.OwnedDesktopCount != 0 ||
		value.Cleanup.OwnedTPortCount != 0 {
		return errors.New("investigation cleanup is incomplete")
	}
	return nil
}

func validateHiddenDirectInvestigationDecision(value hiddenDirectInvestigationDecision) error {
	if !hiddenDirectInvestigationHashValid(value.EvidenceSHA256) {
		return errors.New("investigation decision evidence is invalid")
	}
	switch value.Kind {
	case "runbook-correction":
		if value.ResumeCondition != "" || value.SuccessorCard != "" {
			return errors.New("runbook decision is not exclusive")
		}
	case "replacement-card":
		if strings.TrimSpace(value.SuccessorCard) == "" || value.ResumeCondition != "" {
			return errors.New("replacement decision is incomplete")
		}
	case "not-verifiable":
		if strings.TrimSpace(value.ResumeCondition) == "" || value.SuccessorCard != "" {
			return errors.New("not-verifiable decision is incomplete")
		}
	default:
		return errors.New("investigation decision kind is invalid")
	}
	return nil
}
