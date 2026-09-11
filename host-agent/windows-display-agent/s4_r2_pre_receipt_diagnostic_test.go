package main

import (
	"bytes"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"io"
	"strings"
	"testing"
)

const (
	s4R2DiagnosticSchema = "qa-mcp.s4-r2-pre-receipt-diagnostic.v1"
	s4R1CheckpointSchema = "qa-mcp.s4-pre-receipt-diagnostic.v1"
)

type s4R2DiagnosticStage string
type s4R2DiagnosticFailure string

const (
	s4R2DiagnosticSetup        s4R2DiagnosticStage = "diagnostic_setup"
	s4R2ArgvValidation         s4R2DiagnosticStage = "argv_validation"
	s4R2ChildLaunch            s4R2DiagnosticStage = "child_launch"
	s4R2ListenerReadiness      s4R2DiagnosticStage = "listener_readiness"
	s4R2ProcessExit            s4R2DiagnosticStage = "process_exit"
	s4R2DesktopWindowInventory s4R2DiagnosticStage = "desktop_window_inventory"
	s4R2MainAdmission          s4R2DiagnosticStage = "main_admission"
	s4R2PassiveUIASampling     s4R2DiagnosticStage = "passive_uia_sampling"

	s4R2FailureDiagnosticSetup       s4R2DiagnosticFailure = "diagnostic_setup_failed"
	s4R2FailureArgvValidation        s4R2DiagnosticFailure = "argv_validation_failed"
	s4R2FailureChildLaunch           s4R2DiagnosticFailure = "child_launch_failed"
	s4R2FailureListenerTransfer      s4R2DiagnosticFailure = "listener_transfer_failed"
	s4R2FailureExitWithoutCheckpoint s4R2DiagnosticFailure = "candidate_exited_without_checkpoint"
	s4R2FailureWindowInventory       s4R2DiagnosticFailure = "window_inventory_failed"
	s4R2FailureMainAdmission         s4R2DiagnosticFailure = "main_admission_failed"
	s4R2FailurePassiveUIA            s4R2DiagnosticFailure = "passive_uia_failed"
)

var s4R2FailureByStage = map[s4R2DiagnosticStage]s4R2DiagnosticFailure{
	s4R2DiagnosticSetup:        s4R2FailureDiagnosticSetup,
	s4R2ArgvValidation:         s4R2FailureArgvValidation,
	s4R2ChildLaunch:            s4R2FailureChildLaunch,
	s4R2ListenerReadiness:      s4R2FailureListenerTransfer,
	s4R2ProcessExit:            s4R2FailureExitWithoutCheckpoint,
	s4R2DesktopWindowInventory: s4R2FailureWindowInventory,
	s4R2MainAdmission:          s4R2FailureMainAdmission,
	s4R2PassiveUIASampling:     s4R2FailurePassiveUIA,
}

type s4R2DiagnosticIdentity struct {
	CandidateSHA256 string
	PlatformSHA256  string
	TargetSHA256    string
	FixtureSHA256   string
	ArgvSHA256      string
}

type s4R2Diagnostic struct {
	Schema            string                `json:"schema"`
	Stage             s4R2DiagnosticStage   `json:"stage"`
	Outcome           string                `json:"outcome"`
	FailureCode       s4R2DiagnosticFailure `json:"failure_code"`
	CandidateSHA256   string                `json:"candidate_sha256"`
	PlatformSHA256    string                `json:"platform_sha256"`
	TargetSHA256      string                `json:"target_sha256"`
	FixtureSHA256     string                `json:"fixture_sha256"`
	ArgvSHA256        string                `json:"argv_sha256"`
	CheckpointSHA256  string                `json:"checkpoint_sha256"`
	ExitCode          int                   `json:"exit_code"`
	CandidateExited   bool                  `json:"candidate_exited"`
	ListenerReady     bool                  `json:"listener_ready"`
	PositiveReceipt   bool                  `json:"positive_receipt"`
	ActionCount       uint64                `json:"action_count"`
	RawUIRetained     bool                  `json:"raw_ui_retained"`
	RawOutputRetained bool                  `json:"raw_output_retained"`
	RetryCount        uint64                `json:"retry_count"`
}

type s4R1PreReceiptCheckpoint struct {
	Schema        string `json:"schema"`
	Stage         string `json:"stage"`
	Status        string `json:"status"`
	FailureCode   string `json:"failure_code"`
	ActionCount   uint64 `json:"action_count"`
	RawUIRetained bool   `json:"raw_ui_retained"`
}

func s4R2Hash(value []byte) string {
	digest := sha256.Sum256(value)
	return hex.EncodeToString(digest[:])
}

func s4R2ValidHash(value string) bool {
	if len(value) != sha256.Size*2 || strings.ToLower(value) != value {
		return false
	}
	decoded, err := hex.DecodeString(value)
	return err == nil && len(decoded) == sha256.Size
}

func newS4R2Failure(identity s4R2DiagnosticIdentity, stage s4R2DiagnosticStage, failure s4R2DiagnosticFailure, exitCode int, exited, listener bool, checkpoint []byte) (s4R2Diagnostic, error) {
	value := s4R2Diagnostic{
		Schema: s4R2DiagnosticSchema, Stage: stage, Outcome: "failed", FailureCode: failure,
		CandidateSHA256: identity.CandidateSHA256, PlatformSHA256: identity.PlatformSHA256,
		TargetSHA256: identity.TargetSHA256, FixtureSHA256: identity.FixtureSHA256,
		ArgvSHA256: identity.ArgvSHA256, CheckpointSHA256: s4R2Hash(checkpoint), ExitCode: exitCode,
		CandidateExited: exited, ListenerReady: listener,
	}
	return value, validateS4R2Diagnostic(value)
}

func decodeS4R1Checkpoint(encoded []byte) (s4R1PreReceiptCheckpoint, error) {
	decoder := json.NewDecoder(bytes.NewReader(encoded))
	decoder.DisallowUnknownFields()
	var value s4R1PreReceiptCheckpoint
	if len(encoded) == 0 || decoder.Decode(&value) != nil || decoder.Decode(&struct{}{}) != io.EOF {
		return s4R1PreReceiptCheckpoint{}, errors.New("checkpoint is malformed")
	}
	expected := map[string]string{
		"controller_start": "controller_start_failed", "worker_start": "worker_start_failed",
		"controller_transfer": "controller_transfer_failed", "first_window_inventory": "first_window_inventory_failed",
		"main_window_admission": "main_window_not_ready", "first_uia_sample": "first_uia_not_ready",
		"second_window_inventory": "second_window_inventory_failed", "main_window_readmission": "main_window_readmission_failed",
		"second_uia_sample": "second_uia_not_ready", "marker_derivation": "marker_derivation_failed",
		"observation_admission": "observation_rejected",
	}
	if value.Schema != s4R1CheckpointSchema || value.Status != "failed" || expected[value.Stage] == "" || value.FailureCode != expected[value.Stage] || value.ActionCount != 0 || value.RawUIRetained {
		return s4R1PreReceiptCheckpoint{}, errors.New("checkpoint is invalid")
	}
	return value, nil
}

func classifyS4R2CandidateExit(identity s4R2DiagnosticIdentity, checkpoint []byte, exitCode int) (s4R2Diagnostic, error) {
	if len(checkpoint) == 0 {
		return newS4R2Failure(identity, s4R2ProcessExit, s4R2FailureExitWithoutCheckpoint, exitCode, true, false, checkpoint)
	}
	parsed, err := decodeS4R1Checkpoint(checkpoint)
	if err != nil {
		return s4R2Diagnostic{}, err
	}
	stage, failure, listener := s4R2ChildLaunch, s4R2FailureChildLaunch, false
	switch parsed.Stage {
	case "controller_transfer":
		stage, failure, listener = s4R2ListenerReadiness, s4R2FailureListenerTransfer, true
	case "first_window_inventory", "second_window_inventory":
		stage, failure, listener = s4R2DesktopWindowInventory, s4R2FailureWindowInventory, true
	case "main_window_admission", "main_window_readmission":
		stage, failure, listener = s4R2MainAdmission, s4R2FailureMainAdmission, true
	case "first_uia_sample", "second_uia_sample", "marker_derivation", "observation_admission":
		stage, failure, listener = s4R2PassiveUIASampling, s4R2FailurePassiveUIA, true
	}
	return newS4R2Failure(identity, stage, failure, exitCode, true, listener, checkpoint)
}

func validateS4R2Diagnostic(value s4R2Diagnostic) error {
	expected, known := s4R2FailureByStage[value.Stage]
	if value.Schema != s4R2DiagnosticSchema || value.Outcome != "failed" || !known || value.FailureCode != expected ||
		!s4R2ValidHash(value.CandidateSHA256) || !s4R2ValidHash(value.PlatformSHA256) || !s4R2ValidHash(value.TargetSHA256) ||
		!s4R2ValidHash(value.FixtureSHA256) || !s4R2ValidHash(value.ArgvSHA256) || !s4R2ValidHash(value.CheckpointSHA256) ||
		value.ActionCount != 0 || value.RawUIRetained || value.RawOutputRetained || value.RetryCount != 0 || value.PositiveReceipt {
		return errors.New("S4-R2 diagnostic is invalid")
	}
	if value.Stage != s4R2DiagnosticSetup && value.Stage != s4R2ArgvValidation && value.Stage != s4R2ChildLaunch && !value.CandidateExited {
		return errors.New("S4-R2 final stage requires candidate exit")
	}
	if (value.Stage == s4R2ListenerReadiness || value.Stage == s4R2DesktopWindowInventory || value.Stage == s4R2MainAdmission || value.Stage == s4R2PassiveUIASampling) && !value.ListenerReady {
		return errors.New("S4-R2 post-listener stage lacks readiness")
	}
	return nil
}

func encodeS4R2Diagnostic(value s4R2Diagnostic) ([]byte, error) {
	if err := validateS4R2Diagnostic(value); err != nil {
		return nil, err
	}
	return json.Marshal(value)
}

const s4R2TestHash = "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"

func s4R2TestIdentity() s4R2DiagnosticIdentity {
	return s4R2DiagnosticIdentity{
		CandidateSHA256: s4R2TestHash,
		PlatformSHA256:  s4R2TestHash,
		TargetSHA256:    s4R2TestHash,
		FixtureSHA256:   s4R2TestHash,
		ArgvSHA256:      s4R2TestHash,
	}
}

func TestS4R2DiagnosticMapsEveryPreReceiptBoundary(t *testing.T) {
	tests := []struct {
		name       string
		checkpoint string
		stage      s4R2DiagnosticStage
		failure    s4R2DiagnosticFailure
		listener   bool
	}{
		{"controller launch", `{"schema":"qa-mcp.s4-pre-receipt-diagnostic.v1","stage":"controller_start","status":"failed","failure_code":"controller_start_failed","action_count":0,"raw_ui_retained":false}`, s4R2ChildLaunch, s4R2FailureChildLaunch, false},
		{"worker launch", `{"schema":"qa-mcp.s4-pre-receipt-diagnostic.v1","stage":"worker_start","status":"failed","failure_code":"worker_start_failed","action_count":0,"raw_ui_retained":false}`, s4R2ChildLaunch, s4R2FailureChildLaunch, false},
		{"listener ready", `{"schema":"qa-mcp.s4-pre-receipt-diagnostic.v1","stage":"controller_transfer","status":"failed","failure_code":"controller_transfer_failed","action_count":0,"raw_ui_retained":false}`, s4R2ListenerReadiness, s4R2FailureListenerTransfer, true},
		{"desktop inventory", `{"schema":"qa-mcp.s4-pre-receipt-diagnostic.v1","stage":"first_window_inventory","status":"failed","failure_code":"first_window_inventory_failed","action_count":0,"raw_ui_retained":false}`, s4R2DesktopWindowInventory, s4R2FailureWindowInventory, true},
		{"main admission", `{"schema":"qa-mcp.s4-pre-receipt-diagnostic.v1","stage":"main_window_admission","status":"failed","failure_code":"main_window_not_ready","action_count":0,"raw_ui_retained":false}`, s4R2MainAdmission, s4R2FailureMainAdmission, true},
		{"passive UIA", `{"schema":"qa-mcp.s4-pre-receipt-diagnostic.v1","stage":"first_uia_sample","status":"failed","failure_code":"first_uia_not_ready","action_count":0,"raw_ui_retained":false}`, s4R2PassiveUIASampling, s4R2FailurePassiveUIA, true},
		{"marker derivation", `{"schema":"qa-mcp.s4-pre-receipt-diagnostic.v1","stage":"marker_derivation","status":"failed","failure_code":"marker_derivation_failed","action_count":0,"raw_ui_retained":false}`, s4R2PassiveUIASampling, s4R2FailurePassiveUIA, true},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			value, err := classifyS4R2CandidateExit(s4R2TestIdentity(), []byte(test.checkpoint), 1)
			if err != nil || value.Stage != test.stage || value.FailureCode != test.failure || value.ListenerReady != test.listener {
				t.Fatalf("checkpoint classification mismatch: %#v %v", value, err)
			}
			if validateS4R2Diagnostic(value) != nil {
				t.Fatalf("classified diagnostic is invalid: %#v", value)
			}
		})
	}
}

func TestS4R2DiagnosticTreatsMissingCheckpointAsProcessExit(t *testing.T) {
	value, err := classifyS4R2CandidateExit(s4R2TestIdentity(), nil, -1073741819)
	if err != nil || value.Stage != s4R2ProcessExit || value.FailureCode != s4R2FailureExitWithoutCheckpoint || !value.CandidateExited || value.PositiveReceipt || value.RetryCount != 0 {
		t.Fatalf("missing checkpoint was not a closed exit classification: %#v %v", value, err)
	}
}

func TestS4R2DiagnosticRejectsHostileState(t *testing.T) {
	base, err := classifyS4R2CandidateExit(s4R2TestIdentity(), nil, 1)
	if err != nil {
		t.Fatal(err)
	}
	tests := map[string]func(*s4R2Diagnostic){
		"unknown stage":    func(value *s4R2Diagnostic) { value.Stage = "unknown" },
		"wrong failure":    func(value *s4R2Diagnostic) { value.FailureCode = s4R2FailurePassiveUIA },
		"malformed hash":   func(value *s4R2Diagnostic) { value.ArgvSHA256 = "raw argv" },
		"positive receipt": func(value *s4R2Diagnostic) { value.PositiveReceipt = true },
		"action":           func(value *s4R2Diagnostic) { value.ActionCount = 1 },
		"raw ui":           func(value *s4R2Diagnostic) { value.RawUIRetained = true },
		"raw output":       func(value *s4R2Diagnostic) { value.RawOutputRetained = true },
		"retry":            func(value *s4R2Diagnostic) { value.RetryCount = 1 },
		"not exited":       func(value *s4R2Diagnostic) { value.CandidateExited = false },
		"listener contradiction": func(value *s4R2Diagnostic) {
			value.Stage = s4R2MainAdmission
			value.FailureCode = s4R2FailureMainAdmission
			value.ListenerReady = false
		},
	}
	for name, mutate := range tests {
		t.Run(name, func(t *testing.T) {
			current := base
			mutate(&current)
			if validateS4R2Diagnostic(current) == nil {
				t.Fatalf("hostile diagnostic admitted: %#v", current)
			}
		})
	}
}

func TestS4R2DiagnosticSerializationIsPrivacySafe(t *testing.T) {
	value, err := classifyS4R2CandidateExit(s4R2TestIdentity(), nil, 1)
	if err != nil {
		t.Fatal(err)
	}
	encoded, err := encodeS4R2Diagnostic(value)
	if err != nil {
		t.Fatal(err)
	}
	var fields map[string]json.RawMessage
	if json.Unmarshal(encoded, &fields) != nil {
		t.Fatal("diagnostic is not JSON")
	}
	for _, forbidden := range []string{"argv", "path", "ui_text", "caption", "credential", "password", "raw_output", "environment"} {
		if _, present := fields[forbidden]; present || strings.Contains(strings.ToLower(string(encoded)), `c:\\`) {
			t.Fatalf("diagnostic exposed forbidden surface %q: %s", forbidden, encoded)
		}
	}
	if len(fields) != 18 {
		t.Fatalf("diagnostic field surface changed: %v", fields)
	}
}

func TestS4R2DiagnosticRejectsMalformedOrInProgressCheckpoint(t *testing.T) {
	for name, checkpoint := range map[string]string{
		"malformed":         `{`,
		"in progress":       `{"schema":"qa-mcp.s4-pre-receipt-diagnostic.v1","stage":"main_window_admission","status":"in_progress","failure_code":"","action_count":0,"raw_ui_retained":false}`,
		"raw ui":            `{"schema":"qa-mcp.s4-pre-receipt-diagnostic.v1","stage":"main_window_admission","status":"failed","failure_code":"main_window_not_ready","action_count":0,"raw_ui_retained":true}`,
		"action":            `{"schema":"qa-mcp.s4-pre-receipt-diagnostic.v1","stage":"main_window_admission","status":"failed","failure_code":"main_window_not_ready","action_count":1,"raw_ui_retained":false}`,
		"added cause field": `{"schema":"qa-mcp.s4-pre-receipt-diagnostic.v1","stage":"first_window_inventory","status":"failed","failure_code":"first_window_inventory_failed","cause":"pre_fence_child_exited","action_count":0,"raw_ui_retained":false}`,
	} {
		t.Run(name, func(t *testing.T) {
			if _, err := classifyS4R2CandidateExit(s4R2TestIdentity(), []byte(checkpoint), 1); err == nil {
				t.Fatal("hostile checkpoint admitted")
			}
		})
	}
}
