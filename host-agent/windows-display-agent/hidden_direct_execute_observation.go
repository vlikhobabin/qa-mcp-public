package main

import (
	"errors"
	"fmt"
	"sort"
	"strconv"
	"strings"
)

const (
	hiddenDirectObservationSchema   = "qa-mcp.hidden-direct-execute-observation.v1"
	hiddenDirectObservationObserved = "exact_marker_topology_observed"
	hiddenDirectPreReceiptSchema    = "qa-mcp.s4-pre-receipt-diagnostic.v1"
	hiddenDirectUIALimit            = 512
)

type hiddenDirectLivenessStatus string

const (
	hiddenDirectLivenessLive    hiddenDirectLivenessStatus = "live"
	hiddenDirectLivenessExited  hiddenDirectLivenessStatus = "exited"
	hiddenDirectLivenessUnknown hiddenDirectLivenessStatus = "unknown"
)

type hiddenDirectInventoryStatus string

const (
	hiddenDirectInventoryError    hiddenDirectInventoryStatus = "error"
	hiddenDirectInventoryEmpty    hiddenDirectInventoryStatus = "empty"
	hiddenDirectInventoryNonEmpty hiddenDirectInventoryStatus = "nonempty"
)

type hiddenDirectFencedStatus string

const (
	hiddenDirectFenceObserved        hiddenDirectFencedStatus = "observed"
	hiddenDirectFenceChildExited     hiddenDirectFencedStatus = "child_exited"
	hiddenDirectFenceChildUnknown    hiddenDirectFencedStatus = "child_unknown"
	hiddenDirectFenceListenerExited  hiddenDirectFencedStatus = "listener_exited"
	hiddenDirectFenceListenerUnknown hiddenDirectFencedStatus = "listener_unknown"
	hiddenDirectFenceInventoryError  hiddenDirectFencedStatus = "inventory_error"
	hiddenDirectFenceChanged         hiddenDirectFencedStatus = "lifecycle_changed"
)

type hiddenDirectInventoryFailure string

const (
	hiddenDirectInventoryFailureHiddenOpen        hiddenDirectInventoryFailure = "hidden_open"
	hiddenDirectInventoryFailureHiddenEnumerate   hiddenDirectInventoryFailure = "hidden_enumerate"
	hiddenDirectInventoryFailureHiddenOverflow    hiddenDirectInventoryFailure = "hidden_overflow"
	hiddenDirectInventoryFailureOperatorOpen      hiddenDirectInventoryFailure = "operator_open"
	hiddenDirectInventoryFailureOperatorEnumerate hiddenDirectInventoryFailure = "operator_enumerate"
	hiddenDirectInventoryFailureOperatorOverflow  hiddenDirectInventoryFailure = "operator_overflow"
	hiddenDirectInventoryFailureIsolation         hiddenDirectInventoryFailure = "isolation_validation"
)

type hiddenDirectInventoryCause string

const (
	hiddenDirectCauseChildExited       hiddenDirectInventoryCause = "pre_fence_child_exited"
	hiddenDirectCauseChildUnknown      hiddenDirectInventoryCause = "pre_fence_child_unknown"
	hiddenDirectCauseListenerExited    hiddenDirectInventoryCause = "pre_fence_listener_exited"
	hiddenDirectCauseListenerUnknown   hiddenDirectInventoryCause = "pre_fence_listener_unknown"
	hiddenDirectCauseHiddenOpen        hiddenDirectInventoryCause = "hidden_desktop_open_failed"
	hiddenDirectCauseHiddenEnumerate   hiddenDirectInventoryCause = "hidden_desktop_enumeration_failed"
	hiddenDirectCauseHiddenOverflow    hiddenDirectInventoryCause = "hidden_desktop_overflow_failed"
	hiddenDirectCauseOperatorOpen      hiddenDirectInventoryCause = "operator_desktop_open_failed"
	hiddenDirectCauseOperatorEnumerate hiddenDirectInventoryCause = "operator_desktop_enumeration_failed"
	hiddenDirectCauseOperatorOverflow  hiddenDirectInventoryCause = "operator_desktop_overflow_failed"
	hiddenDirectCauseIsolation         hiddenDirectInventoryCause = "isolation_validation_failed"
	hiddenDirectCausePostFenceChanged  hiddenDirectInventoryCause = "post_fence_lifecycle_changed"
	hiddenDirectCauseSuccessfulEmpty   hiddenDirectInventoryCause = "successful_empty"
	hiddenDirectCauseMainAbsent        hiddenDirectInventoryCause = "successful_nonempty_main_absent"
	hiddenDirectCauseExactMain         hiddenDirectInventoryCause = "exact_main"
)

type hiddenDirectMainStatus string

const (
	hiddenDirectMainUnchecked hiddenDirectMainStatus = "unchecked"
	hiddenDirectMainAbsent    hiddenDirectMainStatus = "absent"
	hiddenDirectMainExact     hiddenDirectMainStatus = "exact"
	hiddenDirectMainInvalid   hiddenDirectMainStatus = "invalid"
)

type hiddenDirectLivenessSnapshot struct {
	Child, Listener                      hiddenDirectLivenessStatus
	ChildInJob, ListenerInJob, ExactPort bool
}

type hiddenDirectFencedSample struct {
	Status           hiddenDirectFencedStatus
	InventoryStatus  hiddenDirectInventoryStatus
	InventoryFailure hiddenDirectInventoryFailure
	Pre, Post        hiddenDirectLivenessSnapshot
	Isolation        hiddenWindowIsolationReceipt
	Windows          []hiddenWindowIdentity
}

type hiddenDirectPreReceiptDiagnostic struct {
	Schema        string `json:"schema"`
	Stage         string `json:"stage"`
	Status        string `json:"status"`
	FailureCode   string `json:"failure_code"`
	ActionCount   uint64 `json:"action_count"`
	RawUIRetained bool   `json:"raw_ui_retained"`
}

var hiddenDirectPreReceiptFailureByStage = map[string]string{
	"first_window_inventory":  "first_window_inventory_failed",
	"second_window_inventory": "second_window_inventory_failed",
}

func hiddenDirectPreLivenessStatus(value hiddenDirectLivenessSnapshot) hiddenDirectFencedStatus {
	if value.Child == hiddenDirectLivenessExited {
		return hiddenDirectFenceChildExited
	}
	if value.Child != hiddenDirectLivenessLive || !value.ChildInJob {
		return hiddenDirectFenceChildUnknown
	}
	if value.Listener == hiddenDirectLivenessExited {
		return hiddenDirectFenceListenerExited
	}
	if value.Listener != hiddenDirectLivenessLive || !value.ListenerInJob || !value.ExactPort {
		return hiddenDirectFenceListenerUnknown
	}
	return hiddenDirectFenceObserved
}

func observeHiddenDirectFencedSample(snapshot func() hiddenDirectLivenessSnapshot, inventory func() (hiddenWindowIsolationReceipt, []hiddenWindowIdentity, hiddenDirectInventoryFailure, error)) hiddenDirectFencedSample {
	result := hiddenDirectFencedSample{Status: hiddenDirectFenceChildUnknown}
	if snapshot == nil || inventory == nil {
		return result
	}
	result.Pre = snapshot()
	if result.Status = hiddenDirectPreLivenessStatus(result.Pre); result.Status != hiddenDirectFenceObserved {
		return result
	}
	var err error
	result.Isolation, result.Windows, result.InventoryFailure, err = inventory()
	result.Post = snapshot()
	if hiddenDirectPreLivenessStatus(result.Post) != hiddenDirectFenceObserved || result.Post != result.Pre {
		result.Status = hiddenDirectFenceChanged
		return result
	}
	if err != nil {
		result.Status, result.InventoryStatus = hiddenDirectFenceInventoryError, hiddenDirectInventoryError
		return result
	}
	result.InventoryStatus = hiddenDirectInventoryNonEmpty
	if len(result.Windows) == 0 {
		result.InventoryStatus = hiddenDirectInventoryEmpty
	}
	result.Status = hiddenDirectFenceObserved
	return result
}

func classifyHiddenDirectInventoryCause(sample hiddenDirectFencedSample, main hiddenDirectMainStatus) (hiddenDirectInventoryCause, error) {
	invalid := func() (hiddenDirectInventoryCause, error) {
		return "", errors.New("hidden direct inventory cause state is invalid")
	}
	if main != hiddenDirectMainUnchecked && main != hiddenDirectMainAbsent && main != hiddenDirectMainExact {
		return invalid()
	}
	if sample.Status != hiddenDirectFenceObserved && main != hiddenDirectMainUnchecked {
		return invalid()
	}
	if sample.Status != hiddenDirectFenceInventoryError && sample.Status != hiddenDirectFenceChanged && sample.InventoryFailure != "" {
		return invalid()
	}
	switch sample.Status {
	case hiddenDirectFenceChildExited:
		if sample.InventoryStatus == "" {
			return hiddenDirectCauseChildExited, nil
		}
	case hiddenDirectFenceChildUnknown:
		if sample.InventoryStatus == "" {
			return hiddenDirectCauseChildUnknown, nil
		}
	case hiddenDirectFenceListenerExited:
		if sample.InventoryStatus == "" {
			return hiddenDirectCauseListenerExited, nil
		}
	case hiddenDirectFenceListenerUnknown:
		if sample.InventoryStatus == "" {
			return hiddenDirectCauseListenerUnknown, nil
		}
	case hiddenDirectFenceInventoryError:
		if sample.InventoryStatus != hiddenDirectInventoryError {
			break
		}
		causes := map[hiddenDirectInventoryFailure]hiddenDirectInventoryCause{
			hiddenDirectInventoryFailureHiddenOpen:        hiddenDirectCauseHiddenOpen,
			hiddenDirectInventoryFailureHiddenEnumerate:   hiddenDirectCauseHiddenEnumerate,
			hiddenDirectInventoryFailureHiddenOverflow:    hiddenDirectCauseHiddenOverflow,
			hiddenDirectInventoryFailureOperatorOpen:      hiddenDirectCauseOperatorOpen,
			hiddenDirectInventoryFailureOperatorEnumerate: hiddenDirectCauseOperatorEnumerate,
			hiddenDirectInventoryFailureOperatorOverflow:  hiddenDirectCauseOperatorOverflow,
			hiddenDirectInventoryFailureIsolation:         hiddenDirectCauseIsolation,
		}
		if cause := causes[sample.InventoryFailure]; cause != "" {
			return cause, nil
		}
	case hiddenDirectFenceChanged:
		return hiddenDirectCausePostFenceChanged, nil
	case hiddenDirectFenceObserved:
		if sample.InventoryFailure != "" {
			break
		}
		switch sample.InventoryStatus {
		case hiddenDirectInventoryEmpty:
			if main == hiddenDirectMainAbsent {
				return hiddenDirectCauseSuccessfulEmpty, nil
			}
		case hiddenDirectInventoryNonEmpty:
			if main == hiddenDirectMainAbsent {
				return hiddenDirectCauseMainAbsent, nil
			}
			if main == hiddenDirectMainExact {
				return hiddenDirectCauseExactMain, nil
			}
		}
	}
	return invalid()
}

func hiddenDirectPreReceiptDiagnosticFor(stage string) hiddenDirectPreReceiptDiagnostic {
	return hiddenDirectPreReceiptDiagnostic{Schema: hiddenDirectPreReceiptSchema, Stage: stage, Status: "failed", FailureCode: hiddenDirectPreReceiptFailureByStage[stage]}
}

func validateHiddenDirectPreReceiptDiagnostic(value hiddenDirectPreReceiptDiagnostic) error {
	failure, validStage := hiddenDirectPreReceiptFailureByStage[value.Stage]
	if value.Schema != hiddenDirectPreReceiptSchema || !validStage || value.Status != "failed" || value.FailureCode != failure || value.ActionCount != 0 || value.RawUIRetained {
		return errors.New("hidden direct pre-receipt diagnostic is invalid")
	}
	return nil
}

type hiddenDirectUIARow struct {
	PID                                                    uint32
	ControlTypeHash, ClassHash, AutomationIDHash, NameHash string
	PathHash                                               string
	Invoke, Value, ExpandCollapse, SelectionItem           bool
}

type hiddenDirectObservationReceipt struct {
	Schema             string `json:"schema"`
	Status             string `json:"status"`
	MainIdentityHash   string `json:"main_identity_hash,omitempty"`
	ExpectedMarkerHash string `json:"expected_marker_hash,omitempty"`
	TopologyHash       string `json:"topology_hash,omitempty"`
	MarkerMatchCount   int    `json:"marker_match_count"`
	ControlCount       int    `json:"control_count"`
	ActionCount        uint64 `json:"action_count"`
	RawUIRetained      bool   `json:"raw_ui_retained"`
}

func hiddenDirectMainIdentityHash(value hiddenWindowIdentity) string {
	return hiddenWindowHash(fmt.Sprintf("%d|%d|%s|%d|%s", value.HWND, value.PID, hiddenWindowHash(strings.ToLower(value.ClassName)), value.OwnerHWND, value.DesktopHash))
}

func admitHiddenDirectMainWindow(items []hiddenWindowIdentity, expected hiddenWindowIdentity, inJob func(uint32) bool) (hiddenWindowIdentity, error) {
	if expected.PID == 0 || expected.ClassName == "" || !validHiddenWindowHash(expected.DesktopHash) || inJob == nil {
		return hiddenWindowIdentity{}, errors.New("main window predicate is invalid")
	}
	matches := make([]hiddenWindowIdentity, 0, 1)
	for _, item := range items {
		if !validHiddenWindowIdentity(item, expected.DesktopHash) || !inJob(item.PID) {
			return hiddenWindowIdentity{}, errors.New("foreign hidden main window")
		}
		if item.PID == expected.PID && strings.EqualFold(item.ClassName, expected.ClassName) && item.OwnerHWND == expected.OwnerHWND {
			matches = append(matches, item)
		}
	}
	if len(matches) != 1 || matches[0].HWND != expected.HWND {
		return hiddenWindowIdentity{}, errors.New("exact main window is missing, ambiguous or changed")
	}
	return matches[0], nil
}

func hiddenDirectValidMainRow(item hiddenWindowIdentity, expectedDesktop string) bool {
	return item.HWND != 0 && item.PID != 0 && item.OwnerHWND != item.HWND && item.ClassName != "" && len(item.ClassName) <= 256 &&
		item.DesktopHash == expectedDesktop && hiddenDirectCanonicalHash(item.DesktopHash)
}

func hiddenDirectCanonicalHash(value string) bool {
	return validHiddenWindowHash(value)
}

func hiddenDirectValidSecondExpected(expected hiddenWindowIdentity) bool {
	return expected.HWND != 0 && expected.PID != 0 && expected.OwnerHWND != expected.HWND && expected.ClassName != "" && len(expected.ClassName) <= 256 &&
		hiddenDirectCanonicalHash(expected.DesktopHash)
}

func hiddenDirectMainInventoryStatusFor(items []hiddenWindowIdentity, expected hiddenWindowIdentity, inJob func(uint32) bool, requireValidIdentity bool) hiddenDirectMainStatus {
	if inJob == nil || requireValidIdentity && !hiddenDirectValidSecondExpected(expected) || !requireValidIdentity &&
		(expected.PID == 0 || expected.ClassName == "" || len(expected.ClassName) > 256 || !hiddenDirectCanonicalHash(expected.DesktopHash)) {
		return hiddenDirectMainInvalid
	}
	matches := make([]hiddenWindowIdentity, 0, 1)
	for _, item := range items {
		if !hiddenDirectValidMainRow(item, expected.DesktopHash) || !inJob(item.PID) {
			return hiddenDirectMainInvalid
		}
		if item.PID == expected.PID && strings.EqualFold(item.ClassName, expected.ClassName) && item.OwnerHWND == expected.OwnerHWND {
			matches = append(matches, item)
		}
	}
	if len(matches) == 0 {
		return hiddenDirectMainAbsent
	}
	if len(matches) != 1 || requireValidIdentity && matches[0].HWND != expected.HWND {
		return hiddenDirectMainInvalid
	}
	return hiddenDirectMainExact
}

func hiddenDirectRecordedMembership(inJob func(uint32) bool) (func(uint32) bool, func(uint32) bool, func() bool) {
	if inJob == nil {
		return nil, nil, func() bool { return false }
	}
	values := make([]bool, 0)
	record := func(pid uint32) bool {
		value := inJob(pid)
		values = append(values, value)
		return value
	}
	next := 0
	valid := true
	replay := func(uint32) bool {
		if next >= len(values) {
			valid = false
			return false
		}
		value := values[next]
		next++
		return value
	}
	return record, replay, func() bool { return valid && next == len(values) }
}

func hiddenDirectMainAdmissionStatus(replayed hiddenDirectMainStatus, complete bool, current, expected hiddenWindowIdentity, admissionErr error, requireExactIdentity bool) hiddenDirectMainStatus {
	if complete && admissionErr == nil && replayed == hiddenDirectMainExact && (!requireExactIdentity || current == expected) {
		return hiddenDirectMainExact
	}
	if complete && admissionErr != nil && replayed == hiddenDirectMainAbsent {
		return hiddenDirectMainAbsent
	}
	return hiddenDirectMainInvalid
}

func classifyHiddenDirectMainInventoryCause(sample hiddenDirectFencedSample, items []hiddenWindowIdentity, expected hiddenWindowIdentity, inJob func(uint32) bool) (hiddenDirectMainStatus, hiddenDirectInventoryCause, error) {
	main := hiddenDirectMainInventoryStatusFor(items, expected, inJob, false)
	cause, err := classifyHiddenDirectInventoryCause(sample, main)
	return main, cause, err
}

func observeHiddenDirectAfterReadmission(expected hiddenWindowIdentity, items []hiddenWindowIdentity, inJob func(uint32) bool, observe func(uintptr, uint32) ([]hiddenDirectUIARow, error)) ([]hiddenDirectUIARow, error) {
	return observeHiddenDirectAfterReadmissionClassified(expected, items, inJob, nil, observe)
}

func observeHiddenDirectAfterReadmissionClassified(expected hiddenWindowIdentity, items []hiddenWindowIdentity, inJob func(uint32) bool, classify func(hiddenDirectMainStatus, hiddenDirectMainStatus, bool) error, observe func(uintptr, uint32) ([]hiddenDirectUIARow, error)) ([]hiddenDirectUIARow, error) {
	if observe == nil {
		return nil, errors.New("passive UIA observer is unavailable")
	}
	if !hiddenDirectValidSecondExpected(expected) {
		if classify != nil {
			_ = classify(hiddenDirectMainInvalid, hiddenDirectMainInvalid, true)
		}
		return nil, errors.New("exact main window provenance is invalid")
	}
	record, replay, complete := hiddenDirectRecordedMembership(inJob)
	current, err := admitHiddenDirectMainWindow(items, expected, record)
	replayed := hiddenDirectMainInventoryStatusFor(items, expected, replay, true)
	replayComplete := complete()
	main := hiddenDirectMainAdmissionStatus(replayed, replayComplete, current, expected, err, true)
	if classify != nil {
		if classifyErr := classify(main, replayed, replayComplete); classifyErr != nil {
			return nil, classifyErr
		}
	}
	if main != hiddenDirectMainExact {
		return nil, errors.New("exact main window identity changed before observation")
	}
	return observe(current.HWND, current.PID)
}

func hiddenDirectRows(rows []hiddenDirectUIARow, pid uint32, markerHash string) (string, int, error) {
	if pid == 0 || len(rows) == 0 || len(rows) > hiddenDirectUIALimit {
		return "", 0, errors.New("UIA inventory is missing or oversized")
	}
	encoded, paths, markerCount := make([]string, 0, len(rows)), make(map[string]struct{}, len(rows)), 0
	for _, row := range rows {
		hashes := []string{row.ControlTypeHash, row.ClassHash, row.AutomationIDHash, row.NameHash, row.PathHash}
		if row.PID != pid {
			return "", 0, errors.New("UIA inventory contains a foreign PID")
		}
		for _, hash := range hashes {
			if !validHiddenWindowHash(hash) {
				return "", 0, errors.New("UIA inventory contains a malformed hash")
			}
		}
		if _, exists := paths[row.PathHash]; exists {
			return "", 0, errors.New("UIA topology is ambiguous")
		}
		paths[row.PathHash] = struct{}{}
		if row.NameHash == markerHash {
			markerCount++
		}
		encoded = append(encoded, strings.Join(append(hashes,
			strconv.FormatBool(row.Invoke), strconv.FormatBool(row.Value),
			strconv.FormatBool(row.ExpandCollapse), strconv.FormatBool(row.SelectionItem)), "|"))
	}
	sort.Strings(encoded)
	return hiddenWindowHash(strings.Join(encoded, "\n")), markerCount, nil
}

func admitHiddenDirectObservation(original hiddenWindowIdentity, firstWindows, secondWindows []hiddenWindowIdentity, markerHash string, first, second []hiddenDirectUIARow, inJob func(uint32) bool) (hiddenDirectObservationReceipt, error) {
	receipt := hiddenDirectObservationReceipt{Schema: hiddenDirectObservationSchema, Status: "main_window_identity_rejected"}
	if !validHiddenWindowHash(markerHash) {
		receipt.Status = "marker_hash_rejected"
		return receipt, errors.New("expected marker hash is invalid")
	}
	main, err := admitHiddenDirectMainWindow(firstWindows, original, inJob)
	current, secondErr := admitHiddenDirectMainWindow(secondWindows, original, inJob)
	if err != nil || secondErr != nil || main != original || current != original {
		return receipt, errors.New("exact main window identity changed")
	}
	receipt.MainIdentityHash, receipt.ExpectedMarkerHash = hiddenDirectMainIdentityHash(main), markerHash
	firstHash, firstCount, err := hiddenDirectRows(first, main.PID, markerHash)
	if err != nil {
		receipt.Status = "uia_topology_rejected"
		return receipt, err
	}
	secondHash, secondCount, err := hiddenDirectRows(second, main.PID, markerHash)
	if err != nil || firstHash != secondHash || len(first) != len(second) {
		receipt.Status = "uia_topology_changed"
		return receipt, errors.New("UIA topology changed")
	}
	receipt.MarkerMatchCount, receipt.ControlCount, receipt.TopologyHash = secondCount, len(second), secondHash
	if firstCount != 1 || secondCount != 1 {
		receipt.Status = "marker_missing_or_ambiguous"
		return receipt, errors.New("exact marker is missing or ambiguous")
	}
	receipt.Status = hiddenDirectObservationObserved
	return receipt, validateHiddenDirectObservationReceipt(receipt)
}

func validateHiddenDirectObservationReceipt(value hiddenDirectObservationReceipt) error {
	if value.Schema != hiddenDirectObservationSchema || value.Status != hiddenDirectObservationObserved ||
		!validHiddenWindowHash(value.MainIdentityHash) || !validHiddenWindowHash(value.ExpectedMarkerHash) ||
		!validHiddenWindowHash(value.TopologyHash) || value.MarkerMatchCount != 1 || value.ControlCount <= 0 ||
		value.ControlCount > hiddenDirectUIALimit || value.ActionCount != 0 || value.RawUIRetained {
		return errors.New("direct-execute observation receipt is invalid")
	}
	return nil
}
