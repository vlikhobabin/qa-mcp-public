package main

import (
	"errors"
	"fmt"
	"sort"
	"strings"
)

const (
	hiddenPromptS5Schema         = "qa-mcp.hidden-prompt-admission-action.v1"
	hiddenPromptS5Confirmed      = "exact_prompt_confirmed_post_state_observed"
	hiddenPromptS5Class          = "V8TopLevelFrameSDIsec"
	hiddenPromptS5ActionPathHash = "2b6dd675bc3690a7d39c8d61adccb37aee8615934da718c8263f1b4d5286fe5f"
)

type hiddenPromptS5Control struct {
	PID                                                       uint32
	ControlTypeHash, PathHash, GeometryHash, RootGeometryHash string
	Enabled, ReadOnly, Offscreen, Invoke, Value               bool
	Bottom                                                    bool
	HorizontalRank, HorizontalPeerCount                       int
}

type hiddenPromptS5Snapshot struct {
	Main, Prompt                  hiddenWindowIdentity
	StableSamples, CandidateCount int
	NewAfterLaunch                bool
	PatternHash                   string
	Controls                      []hiddenPromptS5Control
}

type hiddenPromptS5Ledger struct {
	Attempts, FocusCalls, KeyMessages uint64
}

type hiddenPromptS5InventoryDiagnostic struct {
	Code             string `json:"code"`
	Complete         bool   `json:"complete"`
	HashesValid      bool   `json:"hashes_valid"`
	RowCount         int    `json:"row_count"`
	ExactPIDCount    int    `json:"exact_pid_count"`
	TargetMatchCount int    `json:"target_match_count"`
}

type hiddenPromptS5PostState struct {
	PromptWindows       []hiddenWindowIdentity
	Observation         hiddenDirectObservationReceipt
	OperatorWindowCount int
}

type hiddenPromptS5Receipt struct {
	Schema, Status, MainIdentityHash, PromptIdentityHash string
	PatternHash, TopologyHash, ActionPathHash            string
	RootGeometryHash, ActionGeometryHash                 string
	ControlCount, InvokeCount, ValueCount                int
	ActionAttempts, FocusCalls, KeyMessages              uint64
	PromptClosed, RawUIRetained                          bool
}

func hiddenPromptS5Topology(rows []hiddenPromptS5Control, pid uint32) (string, hiddenPromptS5Control, int, int, error) {
	if len(rows) == 0 || len(rows) > 128 || pid == 0 {
		return "", hiddenPromptS5Control{}, 0, 0, errors.New("prompt control inventory is unbounded")
	}
	encoded := make([]string, 0, len(rows))
	buttonHash, targets, invokes, values := hiddenWindowHash("ControlType.Button"), make([]hiddenPromptS5Control, 0, 1), 0, 0
	for _, row := range rows {
		if row.PID == pid && row.Enabled && !row.Offscreen {
			if row.Invoke {
				invokes++
			}
			if row.Value {
				values++
			}
		}
		if row.ControlTypeHash == buttonHash && row.PathHash == hiddenPromptS5ActionPathHash && row.Bottom && row.HorizontalRank == 0 && row.HorizontalPeerCount == 2 {
			targets = append(targets, row)
		}
		encoded = append(encoded, fmt.Sprintf("%s|%s|%s|%s|%t|%t|%t|%t|%t|%t|%d|%d", row.ControlTypeHash, row.PathHash,
			row.GeometryHash, row.RootGeometryHash, row.Enabled, row.ReadOnly, row.Offscreen, row.Invoke, row.Value, row.Bottom, row.HorizontalRank, row.HorizontalPeerCount))
	}
	if len(targets) != 1 {
		return "", hiddenPromptS5Control{}, invokes, values, errors.New("prompt action topology is ambiguous")
	}
	action := targets[0]
	if action.PID != pid || !validHiddenWindowHash(action.ControlTypeHash) || !validHiddenWindowHash(action.PathHash) ||
		!validHiddenWindowHash(action.GeometryHash) || !validHiddenWindowHash(action.RootGeometryHash) ||
		!action.Enabled || action.ReadOnly || action.Offscreen || !action.Invoke {
		return "", hiddenPromptS5Control{}, invokes, values, errors.New("prompt action identity is foreign or malformed")
	}
	sort.Strings(encoded)
	return hiddenWindowHash(strings.Join(encoded, "\n")), action, invokes, values, nil
}

func admitHiddenPromptS5Snapshot(original hiddenWindowIdentity, baseline map[uintptr]struct{}, value hiddenPromptS5Snapshot, inJob func(uint32) bool) (string, hiddenPromptS5Control, int, int, error) {
	if baseline == nil || inJob == nil || value.Main != original || value.Prompt.PID != original.PID ||
		value.Prompt.OwnerHWND != original.HWND || !strings.EqualFold(value.Prompt.ClassName, hiddenPromptS5Class) ||
		!validHiddenWindowIdentity(value.Prompt, original.DesktopHash) || !inJob(original.PID) || !inJob(value.Prompt.PID) {
		return "", hiddenPromptS5Control{}, 0, 0, errors.New("prompt window identity is stale or foreign")
	}
	if _, err := admitHiddenDirectMainWindow([]hiddenWindowIdentity{value.Main}, original, inJob); err != nil {
		return "", hiddenPromptS5Control{}, 0, 0, err
	}
	_, old := baseline[value.Prompt.HWND]
	if old || !value.NewAfterLaunch || value.StableSamples < 2 || value.CandidateCount != 1 {
		return "", hiddenPromptS5Control{}, 0, 0, errors.New("prompt is old, unstable or ambiguous")
	}
	if !validHiddenWindowHash(value.PatternHash) {
		return "", hiddenPromptS5Control{}, 0, 0, errors.New("prompt diagnostic hash is malformed")
	}
	return hiddenPromptS5Topology(value.Controls, value.Prompt.PID)
}

func admitAndConfirmHiddenPromptS5(original hiddenWindowIdentity, baseline map[uintptr]struct{}, first, second hiddenPromptS5Snapshot,
	inJob func(uint32) bool, ledger *hiddenPromptS5Ledger,
	action func(uintptr, hiddenPromptS5Control) (bool, uint64, error), post func() (hiddenPromptS5PostState, error)) (hiddenPromptS5Receipt, error) {
	receipt := hiddenPromptS5Receipt{Schema: hiddenPromptS5Schema, Status: "prompt_admission_rejected"}
	if ledger == nil || ledger.Attempts != 0 || ledger.FocusCalls != 0 || ledger.KeyMessages != 0 || action == nil || post == nil {
		return receipt, errors.New("prompt action ledger is unavailable or used")
	}
	firstTopology, firstAction, invokes, values, err := admitHiddenPromptS5Snapshot(original, baseline, first, inJob)
	if err != nil {
		return receipt, err
	}
	receipt.Status = "prompt_readmission_rejected"
	_, secondAction, _, _, err := admitHiddenPromptS5Snapshot(original, baseline, second, inJob)
	if err != nil || first.Main != second.Main || first.Prompt != second.Prompt || firstAction != secondAction {
		return receipt, errors.New("prompt or action identity changed before action")
	}
	receipt.MainIdentityHash, receipt.PromptIdentityHash = hiddenDirectMainIdentityHash(original), hiddenDirectMainIdentityHash(first.Prompt)
	receipt.PatternHash, receipt.TopologyHash, receipt.ActionPathHash = first.PatternHash, firstTopology, firstAction.PathHash
	receipt.RootGeometryHash, receipt.ActionGeometryHash = firstAction.RootGeometryHash, firstAction.GeometryHash
	receipt.ControlCount, receipt.InvokeCount, receipt.ValueCount = len(first.Controls), invokes, values
	ledger.Attempts, receipt.ActionAttempts, receipt.Status = 1, 1, "addressed_confirmation_failed"
	focused, keys, actionErr := action(first.Prompt.HWND, firstAction)
	if focused {
		ledger.FocusCalls, receipt.FocusCalls = 1, 1
	}
	ledger.KeyMessages, receipt.KeyMessages = keys, keys
	if actionErr != nil || !focused || keys != 2 {
		return receipt, errors.New("addressed prompt confirmation failed")
	}
	receipt.Status = "prompt_post_state_rejected"
	state, postErr := post()
	if postErr != nil || len(state.PromptWindows) != 0 || state.OperatorWindowCount != 0 ||
		validateHiddenDirectObservationReceipt(state.Observation) != nil || state.Observation.MainIdentityHash != receipt.MainIdentityHash {
		return receipt, errors.New("exact passive prompt post-state was not observed")
	}
	receipt.Status, receipt.PromptClosed = hiddenPromptS5Confirmed, true
	return receipt, validateHiddenPromptS5Receipt(receipt)
}

func validateHiddenPromptS5Receipt(value hiddenPromptS5Receipt) error {
	hashes := []string{value.MainIdentityHash, value.PromptIdentityHash, value.PatternHash, value.TopologyHash, value.ActionPathHash, value.RootGeometryHash, value.ActionGeometryHash}
	for _, hash := range hashes {
		if !validHiddenWindowHash(hash) {
			return errors.New("prompt receipt contains a malformed identity")
		}
	}
	if value.Schema != hiddenPromptS5Schema || value.Status != hiddenPromptS5Confirmed || value.ControlCount < 1 || value.ControlCount > 128 ||
		value.InvokeCount < 1 || value.InvokeCount > value.ControlCount || value.ValueCount < 0 || value.ValueCount > value.ControlCount ||
		value.ActionAttempts != 1 || value.FocusCalls != 1 || value.KeyMessages != 2 || !value.PromptClosed || value.RawUIRetained ||
		value.ActionPathHash != hiddenPromptS5ActionPathHash {
		return errors.New("prompt receipt is invalid")
	}
	return nil
}

func validateHiddenPromptS5InventoryDiagnostic(value hiddenPromptS5InventoryDiagnostic) error {
	allowed := map[string]bool{"observed": true, "root_failed": true, "root_missing": true, "geometry_missing": true,
		"enumeration_failed": true, "control_limit_exceeded": true, "row_failed": true}
	if !allowed[value.Code] || value.RowCount < 0 || value.RowCount > 128 || value.ExactPIDCount < 0 ||
		value.ExactPIDCount > value.RowCount || value.TargetMatchCount < 0 || value.TargetMatchCount > value.RowCount ||
		(value.Complete != (value.Code == "observed")) || (value.Complete && !value.HashesValid) {
		return errors.New("prompt inventory diagnostic is invalid")
	}
	return nil
}
