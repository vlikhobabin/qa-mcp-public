package main

import (
	"encoding/json"
	"errors"
	"os"
	"strings"
	"testing"
	"time"
)

type hiddenDirectWorkerObservation struct {
	Status    string                         `json:"status"`
	Receipt   hiddenDirectObservationReceipt `json:"receipt"`
	Isolation hiddenWindowIsolationReceipt   `json:"isolation"`
}

func observeHiddenDirectInWorkerLoop(markerHash string, sample func() hiddenDirectFencedSample, expected hiddenWindowIdentity, member func(uint32) bool, observe func(uintptr, uint32) ([]hiddenDirectUIARow, error), report func(hiddenDirectPreReceiptDiagnostic) error, now func() time.Time, sleep func(time.Duration), projected func(string, hiddenDirectMainStatus, hiddenDirectMainStatus, bool, hiddenDirectInventoryCause)) hiddenDirectWorkerObservation {
	deadline := now().Add(60 * time.Second)
	result := hiddenDirectWorkerObservation{Status: "main_not_ready"}
	for now().Before(deadline) {
		firstSample := sample()
		if firstSample.Status != hiddenDirectFenceObserved {
			result.Status = "window_inventory_failed"
			_, causeErr := classifyHiddenDirectInventoryCause(firstSample, hiddenDirectMainUnchecked)
			if causeErr != nil || report(hiddenDirectPreReceiptDiagnosticFor("first_window_inventory")) != nil {
				result.Status = "pre_receipt_diagnostic_failed"
			}
			return result
		}
		firstIsolation, firstWindows := firstSample.Isolation, firstSample.Windows
		record, replay, complete := hiddenDirectRecordedMembership(member)
		main, mainErr := admitExactHiddenWindow(firstWindows, expected.DesktopHash, expected.PID, expected.ClassName, expected.OwnerHWND, record)
		replayedStatus := hiddenDirectMainInventoryStatusFor(firstWindows, expected, replay, false)
		replayComplete := complete()
		mainStatus := hiddenDirectMainAdmissionStatus(replayedStatus, replayComplete, main, expected, mainErr, false)
		firstCause, causeErr := classifyHiddenDirectInventoryCause(firstSample, mainStatus)
		projected("first_window_inventory", mainStatus, replayedStatus, replayComplete, firstCause)
		if mainStatus == hiddenDirectMainInvalid {
			sleep(200 * time.Millisecond)
			continue
		}
		if causeErr != nil || (mainStatus == hiddenDirectMainExact && firstCause != hiddenDirectCauseExactMain) {
			result.Status = "window_inventory_failed"
			return result
		}
		if mainStatus == hiddenDirectMainAbsent {
			sleep(200 * time.Millisecond)
			continue
		}
		firstRows, firstErr := observe(main.HWND, main.PID)
		if firstErr != nil {
			result.Status = "first_uia_not_ready"
			sleep(200 * time.Millisecond)
			continue
		}
		sleep(250 * time.Millisecond)
		secondSample := sample()
		if secondSample.Status != hiddenDirectFenceObserved {
			result.Status = "second_window_inventory_failed"
			_, secondCauseErr := classifyHiddenDirectInventoryCause(secondSample, hiddenDirectMainUnchecked)
			if secondCauseErr != nil || report(hiddenDirectPreReceiptDiagnosticFor("second_window_inventory")) != nil {
				result.Status = "pre_receipt_diagnostic_failed"
			}
			return result
		}
		secondIsolation, secondWindows := secondSample.Isolation, secondSample.Windows
		secondRows, secondErr := observeHiddenDirectAfterReadmissionClassified(main, secondWindows, member, func(status, replayed hiddenDirectMainStatus, complete bool) error {
			cause, err := classifyHiddenDirectInventoryCause(secondSample, status)
			projected("second_window_inventory", status, replayed, complete, cause)
			if err != nil || (status == hiddenDirectMainExact && cause != hiddenDirectCauseExactMain) {
				return errors.New("hidden direct second inventory cause is invalid")
			}
			return nil
		}, observe)
		if secondErr != nil {
			result.Status = "second_uia_not_ready"
			sleep(200 * time.Millisecond)
			continue
		}
		receipt, admitErr := admitHiddenDirectObservation(main, firstWindows, secondWindows, markerHash, firstRows, secondRows, member)
		if admitErr == nil && firstIsolation.JobOwnedOperatorWindowCount == 0 && secondIsolation.JobOwnedOperatorWindowCount == 0 {
			return hiddenDirectWorkerObservation{Status: "passed", Receipt: receipt, Isolation: secondIsolation}
		}
		result.Status = receipt.Status
		sleep(200 * time.Millisecond)
	}
	return result
}

func TestHiddenDirectFencedSampleHostileMatrix(t *testing.T) {
	live := hiddenDirectLivenessSnapshot{Child: hiddenDirectLivenessLive, Listener: hiddenDirectLivenessLive, ChildInJob: true, ListenerInJob: true, ExactPort: true}
	tests := []struct {
		name      string
		snapshots []hiddenDirectLivenessSnapshot
		windows   []hiddenWindowIdentity
		inventory error
		failure   hiddenDirectInventoryFailure
		want      hiddenDirectFencedStatus
		wantState hiddenDirectInventoryStatus
		wantSnaps int
		wantCalls int
	}{
		{name: "live nonempty", snapshots: []hiddenDirectLivenessSnapshot{live, live}, windows: []hiddenWindowIdentity{{HWND: 1}}, want: hiddenDirectFenceObserved, wantState: hiddenDirectInventoryNonEmpty, wantSnaps: 2, wantCalls: 1},
		{name: "live empty", snapshots: []hiddenDirectLivenessSnapshot{live, live}, want: hiddenDirectFenceObserved, wantState: hiddenDirectInventoryEmpty, wantSnaps: 2, wantCalls: 1},
		{name: "inventory error", snapshots: []hiddenDirectLivenessSnapshot{live, live}, inventory: errors.New("hostile raw endpoint 192.0.2.1"), failure: hiddenDirectInventoryFailureHiddenOpen, want: hiddenDirectFenceInventoryError, wantState: hiddenDirectInventoryError, wantSnaps: 2, wantCalls: 1},
		{name: "child exited", snapshots: []hiddenDirectLivenessSnapshot{{Child: hiddenDirectLivenessExited}}, want: hiddenDirectFenceChildExited, wantSnaps: 1},
		{name: "child unknown", snapshots: []hiddenDirectLivenessSnapshot{{Child: hiddenDirectLivenessUnknown}}, want: hiddenDirectFenceChildUnknown, wantSnaps: 1},
		{name: "child outside job", snapshots: []hiddenDirectLivenessSnapshot{{Child: hiddenDirectLivenessLive}}, want: hiddenDirectFenceChildUnknown, wantSnaps: 1},
		{name: "listener exited", snapshots: []hiddenDirectLivenessSnapshot{{Child: hiddenDirectLivenessLive, ChildInJob: true, Listener: hiddenDirectLivenessExited}}, want: hiddenDirectFenceListenerExited, wantSnaps: 1},
		{name: "listener unknown", snapshots: []hiddenDirectLivenessSnapshot{{Child: hiddenDirectLivenessLive, ChildInJob: true, Listener: hiddenDirectLivenessUnknown}}, want: hiddenDirectFenceListenerUnknown, wantSnaps: 1},
		{name: "wrong port", snapshots: []hiddenDirectLivenessSnapshot{{Child: hiddenDirectLivenessLive, Listener: hiddenDirectLivenessLive, ChildInJob: true, ListenerInJob: true}}, want: hiddenDirectFenceListenerUnknown, wantSnaps: 1},
		{name: "post changed", snapshots: []hiddenDirectLivenessSnapshot{live, {Child: hiddenDirectLivenessExited}}, windows: []hiddenWindowIdentity{{HWND: 1}}, want: hiddenDirectFenceChanged, wantSnaps: 2, wantCalls: 1},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			snapshotCalls, inventoryCalls := 0, 0
			result := observeHiddenDirectFencedSample(func() hiddenDirectLivenessSnapshot {
				value := test.snapshots[snapshotCalls]
				snapshotCalls++
				return value
			}, func() (hiddenWindowIsolationReceipt, []hiddenWindowIdentity, hiddenDirectInventoryFailure, error) {
				inventoryCalls++
				return hiddenWindowIsolationReceipt{}, test.windows, test.failure, test.inventory
			})
			if result.Status != test.want || result.InventoryStatus != test.wantState || snapshotCalls != test.wantSnaps || inventoryCalls != test.wantCalls {
				t.Fatalf("fence mismatch: result=%#v snapshots=%d inventory=%d", result, snapshotCalls, inventoryCalls)
			}
		})
	}
}

func TestHiddenDirectPreReceiptDiagnosticIsClosedAndPrivate(t *testing.T) {
	for _, stage := range []string{"first_window_inventory", "second_window_inventory"} {
		value := hiddenDirectPreReceiptDiagnosticFor(stage)
		if err := validateHiddenDirectPreReceiptDiagnostic(value); err != nil {
			t.Fatalf("valid diagnostic rejected: %#v %v", value, err)
		}
		data, err := json.Marshal(value)
		if err != nil {
			t.Fatal(err)
		}
		if _, err := decodeS4R1Checkpoint(data); err != nil {
			t.Fatalf("existing clean-HEAD checkpoint decoder rejected diagnostic: %v", err)
		}
		for _, forbidden := range []string{"192.0.2.1", "desktop-name", "raw error", "handle", "pid", "port", "ui value"} {
			if strings.Contains(strings.ToLower(string(data)), forbidden) {
				t.Fatalf("diagnostic leaked %q: %s", forbidden, data)
			}
		}
	}
	for name, value := range map[string]hiddenDirectPreReceiptDiagnostic{
		"absent":               {},
		"foreign schema":       {Schema: "foreign", Stage: "first_window_inventory", Status: "failed", FailureCode: "first_window_inventory_failed"},
		"dynamic stage":        {Schema: hiddenDirectPreReceiptSchema, Stage: "desktop-name", Status: "failed", FailureCode: "desktop-name_failed"},
		"contradictory passed": {Schema: hiddenDirectPreReceiptSchema, Stage: "first_window_inventory", Status: "passed", FailureCode: "first_window_inventory_failed"},
		"contradictory failed": {Schema: hiddenDirectPreReceiptSchema, Stage: "second_window_inventory", Status: "failed"},
		"action":               {Schema: hiddenDirectPreReceiptSchema, Stage: "first_window_inventory", Status: "failed", FailureCode: "first_window_inventory_failed", ActionCount: 1},
		"raw ui":               {Schema: hiddenDirectPreReceiptSchema, Stage: "first_window_inventory", Status: "failed", FailureCode: "first_window_inventory_failed", RawUIRetained: true},
	} {
		t.Run(name, func(t *testing.T) {
			if validateHiddenDirectPreReceiptDiagnostic(value) == nil {
				t.Fatalf("malformed diagnostic admitted: %#v", value)
			}
		})
	}
}

func TestHiddenDirectInventoryRefusalCauseHostileMatrix(t *testing.T) {
	rows := []struct {
		name   string
		cause  hiddenDirectInventoryCause
		sample hiddenDirectFencedSample
		main   hiddenDirectMainStatus
	}{
		{name: "pre-fence child exited", cause: hiddenDirectCauseChildExited, sample: hiddenDirectFencedSample{Status: hiddenDirectFenceChildExited}, main: hiddenDirectMainUnchecked},
		{name: "pre-fence child unknown", cause: hiddenDirectCauseChildUnknown, sample: hiddenDirectFencedSample{Status: hiddenDirectFenceChildUnknown}, main: hiddenDirectMainUnchecked},
		{name: "pre-fence listener exited", cause: hiddenDirectCauseListenerExited, sample: hiddenDirectFencedSample{Status: hiddenDirectFenceListenerExited}, main: hiddenDirectMainUnchecked},
		{name: "pre-fence listener unknown", cause: hiddenDirectCauseListenerUnknown, sample: hiddenDirectFencedSample{Status: hiddenDirectFenceListenerUnknown}, main: hiddenDirectMainUnchecked},
		{name: "hidden desktop open failure", cause: hiddenDirectCauseHiddenOpen, sample: hiddenDirectFencedSample{Status: hiddenDirectFenceInventoryError, InventoryStatus: hiddenDirectInventoryError, InventoryFailure: hiddenDirectInventoryFailureHiddenOpen}, main: hiddenDirectMainUnchecked},
		{name: "hidden desktop enumeration failure", cause: hiddenDirectCauseHiddenEnumerate, sample: hiddenDirectFencedSample{Status: hiddenDirectFenceInventoryError, InventoryStatus: hiddenDirectInventoryError, InventoryFailure: hiddenDirectInventoryFailureHiddenEnumerate}, main: hiddenDirectMainUnchecked},
		{name: "hidden desktop overflow failure", cause: hiddenDirectCauseHiddenOverflow, sample: hiddenDirectFencedSample{Status: hiddenDirectFenceInventoryError, InventoryStatus: hiddenDirectInventoryError, InventoryFailure: hiddenDirectInventoryFailureHiddenOverflow}, main: hiddenDirectMainUnchecked},
		{name: "operator desktop open failure", cause: hiddenDirectCauseOperatorOpen, sample: hiddenDirectFencedSample{Status: hiddenDirectFenceInventoryError, InventoryStatus: hiddenDirectInventoryError, InventoryFailure: hiddenDirectInventoryFailureOperatorOpen}, main: hiddenDirectMainUnchecked},
		{name: "operator desktop enumeration failure", cause: hiddenDirectCauseOperatorEnumerate, sample: hiddenDirectFencedSample{Status: hiddenDirectFenceInventoryError, InventoryStatus: hiddenDirectInventoryError, InventoryFailure: hiddenDirectInventoryFailureOperatorEnumerate}, main: hiddenDirectMainUnchecked},
		{name: "operator desktop overflow failure", cause: hiddenDirectCauseOperatorOverflow, sample: hiddenDirectFencedSample{Status: hiddenDirectFenceInventoryError, InventoryStatus: hiddenDirectInventoryError, InventoryFailure: hiddenDirectInventoryFailureOperatorOverflow}, main: hiddenDirectMainUnchecked},
		{name: "isolation validation failure", cause: hiddenDirectCauseIsolation, sample: hiddenDirectFencedSample{Status: hiddenDirectFenceInventoryError, InventoryStatus: hiddenDirectInventoryError, InventoryFailure: hiddenDirectInventoryFailureIsolation}, main: hiddenDirectMainUnchecked},
		{name: "post-fence lifecycle change", cause: hiddenDirectCausePostFenceChanged, sample: hiddenDirectFencedSample{Status: hiddenDirectFenceChanged, InventoryStatus: hiddenDirectInventoryNonEmpty}, main: hiddenDirectMainUnchecked},
		{name: "successful empty", cause: hiddenDirectCauseSuccessfulEmpty, sample: hiddenDirectFencedSample{Status: hiddenDirectFenceObserved, InventoryStatus: hiddenDirectInventoryEmpty}, main: hiddenDirectMainAbsent},
		{name: "successful non-empty main absent", cause: hiddenDirectCauseMainAbsent, sample: hiddenDirectFencedSample{Status: hiddenDirectFenceObserved, InventoryStatus: hiddenDirectInventoryNonEmpty}, main: hiddenDirectMainAbsent},
		{name: "exact main", cause: hiddenDirectCauseExactMain, sample: hiddenDirectFencedSample{Status: hiddenDirectFenceObserved, InventoryStatus: hiddenDirectInventoryNonEmpty}, main: hiddenDirectMainExact},
	}
	for _, row := range rows {
		t.Run(row.name, func(t *testing.T) {
			row.sample.Windows = []hiddenWindowIdentity{{ClassName: "hostile-raw-error 192.0.2.1 desktop-name-secret handle-777 pid-4242 port-15471 ui-value-secret"}}
			cause, err := classifyHiddenDirectInventoryCause(row.sample, row.main)
			if err != nil || cause != row.cause {
				t.Fatalf("cause mismatch: got=%q want=%q err=%v sample=%#v", cause, row.cause, err, row.sample)
			}
			if cause == hiddenDirectCauseSuccessfulEmpty || cause == hiddenDirectCauseMainAbsent || cause == hiddenDirectCauseExactMain {
				return
			}
			for _, stage := range []string{"first_window_inventory", "second_window_inventory"} {
				value := hiddenDirectPreReceiptDiagnosticFor(stage)
				if err := validateHiddenDirectPreReceiptDiagnostic(value); err != nil {
					t.Fatalf("valid cause diagnostic rejected: %#v %v", value, err)
				}
				data, err := json.Marshal(value)
				if err != nil {
					t.Fatal(err)
				}
				if strings.Contains(string(data), `"cause"`) || strings.Contains(string(data), string(cause)) {
					t.Fatalf("private cause reached the existing v1 wire surface: cause=%q data=%s", cause, data)
				}
				for _, forbidden := range []string{"hostile-raw-error", "192.0.2.1", "desktop-name-secret", "handle-777", "pid-4242", "port-15471", "ui-value-secret"} {
					if strings.Contains(strings.ToLower(string(data)), forbidden) {
						t.Fatalf("diagnostic leaked %q: %s", forbidden, data)
					}
				}
			}
		})
	}

	invalid := map[string]struct {
		sample hiddenDirectFencedSample
		main   hiddenDirectMainStatus
	}{
		"absent":                    {},
		"unknown failure":           {sample: hiddenDirectFencedSample{Status: hiddenDirectFenceInventoryError, InventoryStatus: hiddenDirectInventoryError, InventoryFailure: "raw-hostile-source"}, main: hiddenDirectMainUnchecked},
		"missing failure":           {sample: hiddenDirectFencedSample{Status: hiddenDirectFenceInventoryError, InventoryStatus: hiddenDirectInventoryError}, main: hiddenDirectMainUnchecked},
		"conflicting child success": {sample: hiddenDirectFencedSample{Status: hiddenDirectFenceChildExited, InventoryStatus: hiddenDirectInventoryNonEmpty}, main: hiddenDirectMainUnchecked},
		"success unchecked":         {sample: hiddenDirectFencedSample{Status: hiddenDirectFenceObserved, InventoryStatus: hiddenDirectInventoryNonEmpty}, main: hiddenDirectMainUnchecked},
		"empty exact":               {sample: hiddenDirectFencedSample{Status: hiddenDirectFenceObserved, InventoryStatus: hiddenDirectInventoryEmpty}, main: hiddenDirectMainExact},
		"unknown main":              {sample: hiddenDirectFencedSample{Status: hiddenDirectFenceObserved, InventoryStatus: hiddenDirectInventoryNonEmpty}, main: "raw-hostile-main"},
	}
	for name, test := range invalid {
		t.Run(name, func(t *testing.T) {
			if cause, err := classifyHiddenDirectInventoryCause(test.sample, test.main); err == nil || cause != "" {
				t.Fatalf("malformed cause state admitted: cause=%q sample=%#v main=%q", cause, test.sample, test.main)
			}
		})
	}
}

func TestHiddenDirectWorkerHasExactlyTwoConnectedFencedBoundaries(t *testing.T) {
	data, err := os.ReadFile("hidden_direct_execute_observation_windows_test.go")
	if err != nil {
		t.Fatal(err)
	}
	text := string(data)
	start := strings.Index(text, "func observeHiddenDirectInWorker(")
	end := strings.Index(text[start:], "\nfunc TestHiddenDirectWindowsFenceLivenessAndHandleClose(")
	if start < 0 || end < 0 {
		t.Fatal("worker source boundary is missing")
	}
	worker := text[start : start+end]
	if strings.Count(worker, "observeHiddenDirectInWorkerLoop(") != 1 || strings.Count(worker, "observeHiddenDirectWindowsFencedSample(") != 1 || strings.Count(worker, "inventoryHiddenWindowIsolation(") != 0 {
		t.Fatal("Windows worker is disconnected from the shared worker loop")
	}
	source, err := os.ReadFile("hidden_direct_execute_observation.go")
	if err != nil || strings.Count(string(source), "record, replay, complete := hiddenDirectRecordedMembership(inJob)") != 1 || strings.Count(string(source), "replayed := hiddenDirectMainInventoryStatusFor(items, expected, replay, true)") != 1 {
		t.Fatal("closed main-inventory taxonomy is disconnected from a boundary")
	}
	loopSource, err := os.ReadFile("hidden_direct_execute_observation_test.go")
	if err != nil {
		t.Fatal(err)
	}
	loopStart := strings.Index(string(loopSource), "func observeHiddenDirectInWorkerLoop(")
	if loopStart < 0 {
		t.Fatal("shared worker loop source boundary is missing")
	}
	loopEnd := strings.Index(string(loopSource)[loopStart:], "\nfunc TestHiddenDirectFencedSampleHostileMatrix(")
	if loopEnd < 0 {
		t.Fatal("shared worker loop source boundary is missing")
	}
	loop := string(loopSource)[loopStart : loopStart+loopEnd]
	if strings.Count(loop, "sample()") != 2 || strings.Count(loop, "report(") != 2 || strings.Count(loop, "hiddenDirectRecordedMembership(") != 1 || strings.Count(loop, "hiddenDirectMainInventoryStatusFor(") != 1 || strings.Count(loop, "observeHiddenDirectAfterReadmissionClassified(") != 1 || !strings.Contains(loop, "mainStatus == hiddenDirectMainInvalid") {
		t.Fatal("shared worker loop does not preserve both connected boundaries and invalid-state retry")
	}
}

func TestHiddenDirectMainInventoryStatusRejectsHostileState(t *testing.T) {
	main, inventory, _, _, member := hiddenDirectObservationFixture()
	firstPredicate := main
	firstPredicate.HWND = 0
	foreign := main
	foreign.DesktopHash = hiddenWindowHash(`Winsta0\qa-mcp-foreign`)
	malformed := main
	malformed.ClassName = ""
	conflicting := main
	conflicting.HWND++
	rows := []struct {
		name     string
		items    []hiddenWindowIdentity
		expected hiddenWindowIdentity
		want     hiddenDirectMainStatus
	}{
		{name: "first exact", items: inventory, expected: firstPredicate, want: hiddenDirectMainExact},
		{name: "second exact", items: inventory, expected: main, want: hiddenDirectMainExact},
		{name: "true absence", items: []hiddenWindowIdentity{{HWND: 202, PID: main.PID, ClassName: "Other", DesktopHash: main.DesktopHash}}, expected: main, want: hiddenDirectMainAbsent},
		{name: "malformed", items: []hiddenWindowIdentity{malformed}, expected: main, want: hiddenDirectMainInvalid},
		{name: "foreign", items: []hiddenWindowIdentity{foreign}, expected: main, want: hiddenDirectMainInvalid},
		{name: "duplicate ambiguous", items: []hiddenWindowIdentity{main, main}, expected: main, want: hiddenDirectMainInvalid},
		{name: "conflicting identity", items: []hiddenWindowIdentity{conflicting}, expected: main, want: hiddenDirectMainInvalid},
		{name: "invalid predicate", items: inventory, expected: hiddenWindowIdentity{}, want: hiddenDirectMainInvalid},
	}
	for _, row := range rows {
		t.Run(row.name, func(t *testing.T) {
			if got := hiddenDirectMainInventoryStatusFor(row.items, row.expected, member, row.expected.HWND != 0); got != row.want {
				t.Fatalf("main inventory taxonomy mismatch: got=%q want=%q", got, row.want)
			}
		})
	}
}

func TestHiddenDirectMainRowRulesAreCompleteAndOrdered(t *testing.T) {
	main, _, _, _, _ := hiddenDirectObservationFixture()
	tests := []struct {
		name     string
		row      hiddenWindowIdentity
		expected string
		want     bool
	}{
		{name: "valid", row: main, expected: main.DesktopHash, want: true},
		{name: "zero hwnd", row: func() hiddenWindowIdentity { value := main; value.HWND, value.OwnerHWND = 0, 1; return value }(), expected: main.DesktopHash},
		{name: "zero pid", row: func() hiddenWindowIdentity { value := main; value.PID = 0; return value }(), expected: main.DesktopHash},
		{name: "self owner", row: func() hiddenWindowIdentity { value := main; value.OwnerHWND = value.HWND; return value }(), expected: main.DesktopHash},
		{name: "empty class", row: func() hiddenWindowIdentity { value := main; value.ClassName = ""; return value }(), expected: main.DesktopHash},
		{name: "class length 256", row: func() hiddenWindowIdentity { value := main; value.ClassName = strings.Repeat("x", 256); return value }(), expected: main.DesktopHash, want: true},
		{name: "class length 257", row: func() hiddenWindowIdentity { value := main; value.ClassName = strings.Repeat("x", 257); return value }(), expected: main.DesktopHash},
		{name: "desktop mismatch", row: main, expected: hiddenWindowHash("other")},
		{name: "malformed matching desktop", row: func() hiddenWindowIdentity { value := main; value.DesktopHash = "bad"; return value }(), expected: "bad"},
		{name: "uppercase matching desktop", row: func() hiddenWindowIdentity {
			value := main
			value.DesktopHash = strings.ToUpper(value.DesktopHash)
			return value
		}(), expected: strings.ToUpper(main.DesktopHash)},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if got := hiddenDirectValidMainRow(test.row, test.expected); got != test.want {
				t.Fatalf("row validity mismatch: got=%v want=%v", got, test.want)
			}
		})
	}
}

func TestHiddenDirectConnectedMainInventoryRejectsHostileState(t *testing.T) {
	main, _, _, _, member := hiddenDirectObservationFixture()
	firstPredicate := main
	firstPredicate.HWND = 0
	foreign := main
	foreign.DesktopHash = hiddenWindowHash(`Winsta0\qa-mcp-foreign`)
	malformed := main
	malformed.ClassName = ""
	conflicting := main
	conflicting.HWND++
	hostile := []struct {
		name       string
		items      []hiddenWindowIdentity
		firstInput bool
	}{
		{name: "malformed", items: []hiddenWindowIdentity{malformed}, firstInput: true},
		{name: "foreign", items: []hiddenWindowIdentity{foreign}, firstInput: true},
		{name: "duplicate ambiguous", items: []hiddenWindowIdentity{main, main}, firstInput: true},
		{name: "conflicting identity", items: []hiddenWindowIdentity{conflicting}},
	}
	for _, row := range hostile {
		t.Run(row.name, func(t *testing.T) {
			sample := hiddenDirectFencedSample{Status: hiddenDirectFenceObserved, InventoryStatus: hiddenDirectInventoryNonEmpty, Windows: row.items}
			if row.firstInput {
				status, cause, err := classifyHiddenDirectMainInventoryCause(sample, row.items, firstPredicate, member)
				if status != hiddenDirectMainInvalid || cause != "" || err == nil {
					t.Fatalf("first connected boundary synthesized a hostile cause: status=%q cause=%q err=%v", status, cause, err)
				}
			}
			classified, uiaCalls := hiddenDirectMainUnchecked, 0
			_, err := observeHiddenDirectAfterReadmissionClassified(main, row.items, member, func(status, _ hiddenDirectMainStatus, _ bool) error {
				classified = status
				_, causeErr := classifyHiddenDirectInventoryCause(sample, status)
				return causeErr
			}, func(uintptr, uint32) ([]hiddenDirectUIARow, error) {
				uiaCalls++
				return nil, nil
			})
			if err == nil || classified != hiddenDirectMainInvalid || uiaCalls != 0 {
				t.Fatalf("second connected boundary admitted hostile state: status=%q uia=%d err=%v", classified, uiaCalls, err)
			}
		})
	}
}

func TestHiddenDirectWorkerLoopRejectsHostileMainInventory(t *testing.T) {
	main, inventory, rows, markerHash, member := hiddenDirectObservationFixture()
	expected := main
	expected.HWND = 0
	foreign := main
	foreign.DesktopHash = hiddenWindowHash(`Winsta0\qa-mcp-foreign`)
	malformed := main
	malformed.ClassName = ""
	conflicting := main
	conflicting.HWND++
	for _, test := range []struct {
		name, stage string
		hostile     []hiddenWindowIdentity
		wantMember  int
	}{
		{name: "first malformed", stage: "first", hostile: []hiddenWindowIdentity{malformed}},
		{name: "first foreign", stage: "first", hostile: []hiddenWindowIdentity{foreign}},
		{name: "first duplicate ambiguous", stage: "first", hostile: []hiddenWindowIdentity{main, main}, wantMember: 2},
		{name: "second malformed", stage: "second", hostile: []hiddenWindowIdentity{malformed}, wantMember: 1},
		{name: "second foreign", stage: "second", hostile: []hiddenWindowIdentity{foreign}, wantMember: 1},
		{name: "second duplicate ambiguous", stage: "second", hostile: []hiddenWindowIdentity{main, main}, wantMember: 3},
		{name: "second conflicting identity", stage: "second", hostile: []hiddenWindowIdentity{conflicting}, wantMember: 2},
	} {
		t.Run(test.name, func(t *testing.T) {
			sampleCalls, memberCalls, uiaCalls, reportCalls := 0, 0, 0, 0
			var sleeps []time.Duration
			var projections []struct {
				stage  string
				status hiddenDirectMainStatus
				cause  hiddenDirectInventoryCause
			}
			current := time.Unix(0, 0)
			result := observeHiddenDirectInWorkerLoop(markerHash, func() hiddenDirectFencedSample {
				sampleCalls++
				items := test.hostile
				if test.stage == "second" && sampleCalls == 1 {
					items = inventory
				}
				return hiddenDirectFencedSample{Status: hiddenDirectFenceObserved, InventoryStatus: hiddenDirectInventoryNonEmpty, Windows: append([]hiddenWindowIdentity(nil), items...)}
			}, expected, func(pid uint32) bool {
				memberCalls++
				return member(pid)
			}, func(uintptr, uint32) ([]hiddenDirectUIARow, error) {
				uiaCalls++
				return append([]hiddenDirectUIARow(nil), rows...), nil
			}, func(hiddenDirectPreReceiptDiagnostic) error {
				reportCalls++
				return nil
			}, func() time.Time {
				return current
			}, func(value time.Duration) {
				sleeps = append(sleeps, value)
				current = current.Add(61 * time.Second)
			}, func(stage string, status, _ hiddenDirectMainStatus, _ bool, cause hiddenDirectInventoryCause) {
				projections = append(projections, struct {
					stage  string
					status hiddenDirectMainStatus
					cause  hiddenDirectInventoryCause
				}{stage: stage, status: status, cause: cause})
			})
			if test.stage == "first" {
				if result.Status != "main_not_ready" || sampleCalls != 1 || memberCalls != test.wantMember || uiaCalls != 0 || reportCalls != 0 || len(sleeps) != 1 || sleeps[0] != 200*time.Millisecond || len(projections) != 1 || projections[0].stage != "first_window_inventory" || projections[0].status != hiddenDirectMainInvalid || projections[0].cause != "" {
					t.Fatalf("first hostile boundary changed predecessor behavior: result=%#v samples=%d members=%d/%d uia=%d reports=%d sleeps=%v projections=%#v", result, sampleCalls, memberCalls, test.wantMember, uiaCalls, reportCalls, sleeps, projections)
				}
				return
			}
			if result.Status != "second_uia_not_ready" || sampleCalls != 2 || memberCalls != test.wantMember || uiaCalls != 1 || reportCalls != 0 || len(sleeps) != 2 || sleeps[0] != 250*time.Millisecond || sleeps[1] != 200*time.Millisecond || len(projections) != 2 || projections[0].status != hiddenDirectMainExact || projections[0].cause != hiddenDirectCauseExactMain || projections[1].stage != "second_window_inventory" || projections[1].status != hiddenDirectMainInvalid || projections[1].cause != "" {
				t.Fatalf("second hostile boundary changed predecessor behavior: result=%#v samples=%d members=%d/%d uia=%d reports=%d sleeps=%v projections=%#v", result, sampleCalls, memberCalls, test.wantMember, uiaCalls, reportCalls, sleeps, projections)
			}
		})
	}
}

func TestHiddenDirectWorkerLoopDistinguishesFirstPredicateLengthBeforeEmptyInventory(t *testing.T) {
	main, _, _, markerHash, member := hiddenDirectObservationFixture()
	main.HWND = 0
	for _, test := range []struct {
		name       string
		className  string
		wantStatus hiddenDirectMainStatus
		wantCause  hiddenDirectInventoryCause
	}{
		{name: "length 256 is valid absence", className: strings.Repeat("x", 256), wantStatus: hiddenDirectMainAbsent, wantCause: hiddenDirectCauseSuccessfulEmpty},
		{name: "length 257 is invalid", className: strings.Repeat("x", 257), wantStatus: hiddenDirectMainInvalid},
	} {
		t.Run(test.name, func(t *testing.T) {
			expected := main
			expected.ClassName = test.className
			current := time.Unix(0, 0)
			memberCalls, uiaCalls := 0, 0
			var sleeps []time.Duration
			var gotStatus hiddenDirectMainStatus
			var gotCause hiddenDirectInventoryCause
			result := observeHiddenDirectInWorkerLoop(markerHash, func() hiddenDirectFencedSample {
				return hiddenDirectFencedSample{Status: hiddenDirectFenceObserved, InventoryStatus: hiddenDirectInventoryEmpty}
			}, expected, func(pid uint32) bool {
				memberCalls++
				return member(pid)
			}, func(uintptr, uint32) ([]hiddenDirectUIARow, error) {
				uiaCalls++
				return nil, nil
			}, func(hiddenDirectPreReceiptDiagnostic) error {
				t.Fatal("predicate decision emitted a diagnostic")
				return nil
			}, func() time.Time {
				return current
			}, func(value time.Duration) {
				sleeps = append(sleeps, value)
				current = current.Add(61 * time.Second)
			}, func(_ string, status, _ hiddenDirectMainStatus, _ bool, cause hiddenDirectInventoryCause) {
				gotStatus, gotCause = status, cause
			})
			if result.Status != "main_not_ready" || gotStatus != test.wantStatus || gotCause != test.wantCause || memberCalls != 0 || uiaCalls != 0 || len(sleeps) != 1 || sleeps[0] != 200*time.Millisecond || result.Receipt.ActionCount != 0 {
				t.Fatalf("first predicate length changed connected behavior: result=%#v status=%q/%q cause=%q/%q members=%d uia=%d sleeps=%v", result, gotStatus, test.wantStatus, gotCause, test.wantCause, memberCalls, uiaCalls, sleeps)
			}
		})
	}
}

type hiddenDirectConnectedResult struct {
	result                         hiddenDirectWorkerObservation
	samples, members, uia, reports int
	sleeps                         []time.Duration
	statuses                       []hiddenDirectMainStatus
	replayed                       []hiddenDirectMainStatus
	complete                       []bool
	causes                         []hiddenDirectInventoryCause
	events                         []string
}

func runHiddenDirectConnectedCase(t *testing.T, stage string, expected hiddenWindowIdentity, items []hiddenWindowIdentity, membership []bool, nilMember bool) hiddenDirectConnectedResult {
	t.Helper()
	main, inventory, rows, markerHash, _ := hiddenDirectObservationFixture()
	current := time.Unix(0, 0)
	var got hiddenDirectConnectedResult
	member := func(uint32) bool {
		value := true
		if got.members < len(membership) {
			value = membership[got.members]
		}
		got.members++
		return value
	}
	if nilMember {
		member = nil
	}
	got.result = observeHiddenDirectInWorkerLoop(markerHash, func() hiddenDirectFencedSample {
		got.samples++
		currentItems := items
		if stage == "second" && got.samples == 1 {
			currentItems = inventory
		}
		inventoryStatus := hiddenDirectInventoryNonEmpty
		if len(currentItems) == 0 {
			inventoryStatus = hiddenDirectInventoryEmpty
		}
		return hiddenDirectFencedSample{Status: hiddenDirectFenceObserved, InventoryStatus: inventoryStatus, Windows: append([]hiddenWindowIdentity(nil), currentItems...)}
	}, expected, member, func(uintptr, uint32) ([]hiddenDirectUIARow, error) {
		got.uia++
		got.events = append(got.events, "uia")
		return append([]hiddenDirectUIARow(nil), rows...), nil
	}, func(hiddenDirectPreReceiptDiagnostic) error {
		got.reports++
		return nil
	}, func() time.Time {
		return current
	}, func(value time.Duration) {
		got.sleeps = append(got.sleeps, value)
		got.events = append(got.events, "sleep:"+value.String())
		current = current.Add(61 * time.Second)
	}, func(stage string, status, replayed hiddenDirectMainStatus, complete bool, cause hiddenDirectInventoryCause) {
		got.statuses = append(got.statuses, status)
		got.replayed = append(got.replayed, replayed)
		got.complete = append(got.complete, complete)
		got.causes = append(got.causes, cause)
		got.events = append(got.events, "project:"+stage)
	})
	_ = main
	return got
}

func TestHiddenDirectConnectedFirstPredicateRowAndCardinalityMatrix(t *testing.T) {
	main, _, _, _, _ := hiddenDirectObservationFixture()
	expected := main
	expected.HWND = 0
	nonmatch := main
	nonmatch.ClassName = "Other"
	foreignPID := main
	foreignPID.PID++
	foreignOwner := main
	foreignOwner.OwnerHWND = 99
	length256 := nonmatch
	length256.ClassName = strings.Repeat("x", 256)
	invalidRows := map[string]hiddenWindowIdentity{
		"row zero hwnd":        func() hiddenWindowIdentity { value := main; value.HWND, value.OwnerHWND = 0, 1; return value }(),
		"row zero pid":         func() hiddenWindowIdentity { value := main; value.PID = 0; return value }(),
		"row self owner":       func() hiddenWindowIdentity { value := main; value.OwnerHWND = value.HWND; return value }(),
		"row empty class":      func() hiddenWindowIdentity { value := main; value.ClassName = ""; return value }(),
		"row class length 257": func() hiddenWindowIdentity { value := main; value.ClassName = strings.Repeat("x", 257); return value }(),
		"row desktop mismatch": func() hiddenWindowIdentity {
			value := main
			value.DesktopHash = hiddenWindowHash("other")
			return value
		}(),
		"row malformed hash": func() hiddenWindowIdentity { value := main; value.DesktopHash = "bad"; return value }(),
	}
	tests := []struct {
		name       string
		expected   hiddenWindowIdentity
		items      []hiddenWindowIdentity
		membership []bool
		nilMember  bool
		want       hiddenDirectMainStatus
		cause      hiddenDirectInventoryCause
		members    int
	}{
		{name: "empty is absence", expected: expected, want: hiddenDirectMainAbsent, cause: hiddenDirectCauseSuccessfulEmpty},
		{name: "nonmatching is absence", expected: expected, items: []hiddenWindowIdentity{nonmatch}, want: hiddenDirectMainAbsent, cause: hiddenDirectCauseMainAbsent, members: 1},
		{name: "foreign pid is absence", expected: expected, items: []hiddenWindowIdentity{foreignPID}, want: hiddenDirectMainAbsent, cause: hiddenDirectCauseMainAbsent, members: 1},
		{name: "foreign owner is absence", expected: expected, items: []hiddenWindowIdentity{foreignOwner}, want: hiddenDirectMainAbsent, cause: hiddenDirectCauseMainAbsent, members: 1},
		{name: "length 256 row is absence", expected: expected, items: []hiddenWindowIdentity{length256}, want: hiddenDirectMainAbsent, cause: hiddenDirectCauseMainAbsent, members: 1},
		{name: "duplicate nonmatching is absence", expected: expected, items: []hiddenWindowIdentity{nonmatch, nonmatch}, want: hiddenDirectMainAbsent, cause: hiddenDirectCauseMainAbsent, members: 2},
		{name: "expected zero pid", expected: func() hiddenWindowIdentity { value := expected; value.PID = 0; return value }(), want: hiddenDirectMainInvalid},
		{name: "expected empty class", expected: func() hiddenWindowIdentity { value := expected; value.ClassName = ""; return value }(), want: hiddenDirectMainInvalid},
		{name: "expected length 257", expected: func() hiddenWindowIdentity {
			value := expected
			value.ClassName = strings.Repeat("x", 257)
			return value
		}(), want: hiddenDirectMainInvalid},
		{name: "expected malformed hash", expected: func() hiddenWindowIdentity { value := expected; value.DesktopHash = "bad"; return value }(), want: hiddenDirectMainInvalid},
		{name: "expected uppercase hash", expected: func() hiddenWindowIdentity {
			value := expected
			value.DesktopHash = strings.ToUpper(value.DesktopHash)
			return value
		}(), want: hiddenDirectMainInvalid},
		{name: "expected wrong length hash", expected: func() hiddenWindowIdentity {
			value := expected
			value.DesktopHash = value.DesktopHash[:63]
			return value
		}(), want: hiddenDirectMainInvalid},
		{name: "nil membership", expected: expected, items: []hiddenWindowIdentity{main}, nilMember: true, want: hiddenDirectMainInvalid},
		{name: "membership false first", expected: expected, items: []hiddenWindowIdentity{main}, membership: []bool{false}, want: hiddenDirectMainInvalid, members: 1},
		{name: "membership false later", expected: expected, items: []hiddenWindowIdentity{nonmatch, main}, membership: []bool{true, false}, want: hiddenDirectMainInvalid, members: 2},
		{name: "duplicate matching", expected: expected, items: []hiddenWindowIdentity{main, main}, want: hiddenDirectMainInvalid, members: 2},
	}
	for name, row := range invalidRows {
		tests = append(tests, struct {
			name       string
			expected   hiddenWindowIdentity
			items      []hiddenWindowIdentity
			membership []bool
			nilMember  bool
			want       hiddenDirectMainStatus
			cause      hiddenDirectInventoryCause
			members    int
		}{name: name, expected: expected, items: []hiddenWindowIdentity{row}, want: hiddenDirectMainInvalid})
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			got := runHiddenDirectConnectedCase(t, "first", test.expected, test.items, test.membership, test.nilMember)
			if got.result.Status != "main_not_ready" || got.samples != 1 || got.members != test.members || got.uia != 0 || got.reports != 0 || len(got.sleeps) != 1 || got.sleeps[0] != 200*time.Millisecond || len(got.statuses) != 1 || got.statuses[0] != test.want || got.replayed[0] != test.want || got.complete[0] == test.nilMember || got.causes[0] != test.cause || got.result.Receipt.ActionCount != 0 {
				t.Fatalf("first connected matrix mismatch: result=%#v samples=%d members=%d/%d uia=%d reports=%d sleeps=%v status=%v replayed=%v complete=%v cause=%v", got.result, got.samples, got.members, test.members, got.uia, got.reports, got.sleeps, got.statuses, got.replayed, got.complete, got.causes)
			}
		})
	}
}

func TestHiddenDirectConnectedSecondRowCardinalityAndExactIdentityMatrix(t *testing.T) {
	main, _, _, _, _ := hiddenDirectObservationFixture()
	expected := main
	expected.HWND = 0
	nonmatch := main
	nonmatch.ClassName = "Other"
	foreignPID := main
	foreignPID.PID++
	foreignOwner := main
	foreignOwner.OwnerHWND = 99
	length256 := nonmatch
	length256.ClassName = strings.Repeat("x", 256)
	tests := []struct {
		name       string
		items      []hiddenWindowIdentity
		membership []bool
		want       hiddenDirectMainStatus
		replayed   hiddenDirectMainStatus
		cause      hiddenDirectInventoryCause
		members    int
	}{
		{name: "empty is absence", want: hiddenDirectMainAbsent, cause: hiddenDirectCauseSuccessfulEmpty, members: 1},
		{name: "nonmatching is absence", items: []hiddenWindowIdentity{nonmatch}, want: hiddenDirectMainAbsent, cause: hiddenDirectCauseMainAbsent, members: 2},
		{name: "foreign pid is absence", items: []hiddenWindowIdentity{foreignPID}, want: hiddenDirectMainAbsent, cause: hiddenDirectCauseMainAbsent, members: 2},
		{name: "foreign owner is absence", items: []hiddenWindowIdentity{foreignOwner}, want: hiddenDirectMainAbsent, cause: hiddenDirectCauseMainAbsent, members: 2},
		{name: "length 256 row is absence", items: []hiddenWindowIdentity{length256}, want: hiddenDirectMainAbsent, cause: hiddenDirectCauseMainAbsent, members: 2},
		{name: "duplicate nonmatching is absence", items: []hiddenWindowIdentity{nonmatch, nonmatch}, want: hiddenDirectMainAbsent, cause: hiddenDirectCauseMainAbsent, members: 3},
		{name: "row zero hwnd", items: []hiddenWindowIdentity{func() hiddenWindowIdentity { value := main; value.HWND, value.OwnerHWND = 0, 1; return value }()}, want: hiddenDirectMainInvalid, members: 1},
		{name: "row zero pid", items: []hiddenWindowIdentity{func() hiddenWindowIdentity { value := main; value.PID = 0; return value }()}, want: hiddenDirectMainInvalid, members: 1},
		{name: "row self owner", items: []hiddenWindowIdentity{func() hiddenWindowIdentity { value := main; value.OwnerHWND = value.HWND; return value }()}, want: hiddenDirectMainInvalid, members: 1},
		{name: "row empty class", items: []hiddenWindowIdentity{func() hiddenWindowIdentity { value := main; value.ClassName = ""; return value }()}, want: hiddenDirectMainInvalid, members: 1},
		{name: "row class length 257", items: []hiddenWindowIdentity{func() hiddenWindowIdentity { value := main; value.ClassName = strings.Repeat("x", 257); return value }()}, want: hiddenDirectMainInvalid, members: 1},
		{name: "row desktop mismatch", items: []hiddenWindowIdentity{func() hiddenWindowIdentity {
			value := main
			value.DesktopHash = hiddenWindowHash("other")
			return value
		}()}, want: hiddenDirectMainInvalid, members: 1},
		{name: "row malformed hash", items: []hiddenWindowIdentity{func() hiddenWindowIdentity { value := main; value.DesktopHash = "bad"; return value }()}, want: hiddenDirectMainInvalid, members: 1},
		{name: "membership false first", items: []hiddenWindowIdentity{main}, membership: []bool{true, false}, want: hiddenDirectMainInvalid, members: 2},
		{name: "membership false later", items: []hiddenWindowIdentity{nonmatch, main}, membership: []bool{true, true, false}, want: hiddenDirectMainInvalid, members: 3},
		{name: "duplicate matching", items: []hiddenWindowIdentity{main, main}, want: hiddenDirectMainInvalid, members: 3},
		{name: "wrong handle", items: []hiddenWindowIdentity{func() hiddenWindowIdentity { value := main; value.HWND++; return value }()}, want: hiddenDirectMainInvalid, members: 2},
		{name: "class spelling drift", items: []hiddenWindowIdentity{func() hiddenWindowIdentity {
			value := main
			value.ClassName = strings.ToLower(value.ClassName)
			return value
		}()}, want: hiddenDirectMainInvalid, replayed: hiddenDirectMainExact, members: 2},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			got := runHiddenDirectConnectedCase(t, "second", expected, test.items, test.membership, false)
			wantReplayed := test.replayed
			if wantReplayed == "" {
				wantReplayed = test.want
			}
			if got.result.Status != "second_uia_not_ready" || got.samples != 2 || got.members != test.members || got.uia != 1 || got.reports != 0 || len(got.sleeps) != 2 || got.sleeps[0] != 250*time.Millisecond || got.sleeps[1] != 200*time.Millisecond || len(got.statuses) != 2 || got.statuses[0] != hiddenDirectMainExact || got.replayed[0] != hiddenDirectMainExact || !got.complete[0] || got.causes[0] != hiddenDirectCauseExactMain || got.statuses[1] != test.want || got.replayed[1] != wantReplayed || !got.complete[1] || got.causes[1] != test.cause || got.result.Receipt.ActionCount != 0 {
				t.Fatalf("second connected matrix mismatch: result=%#v samples=%d members=%d/%d uia=%d reports=%d sleeps=%v status=%v replayed=%v complete=%v cause=%v events=%v", got.result, got.samples, got.members, test.members, got.uia, got.reports, got.sleeps, got.statuses, got.replayed, got.complete, got.causes, got.events)
			}
		})
	}
}

func TestHiddenDirectConnectedSuccessOrderAndCaseFold(t *testing.T) {
	main, inventory, _, _, _ := hiddenDirectObservationFixture()
	for _, test := range []struct {
		name     string
		expected hiddenWindowIdentity
		items    []hiddenWindowIdentity
	}{
		{name: "case fold first predicate", expected: func() hiddenWindowIdentity {
			value := main
			value.HWND = 0
			value.ClassName = strings.ToLower(value.ClassName)
			return value
		}(), items: inventory},
		{name: "class length 256", expected: func() hiddenWindowIdentity {
			value := main
			value.HWND = 0
			value.ClassName = strings.Repeat("x", 256)
			return value
		}(), items: []hiddenWindowIdentity{func() hiddenWindowIdentity { value := main; value.ClassName = strings.Repeat("x", 256); return value }()}},
	} {
		t.Run(test.name, func(t *testing.T) {
			got := runHiddenDirectConnectedCase(t, "success", test.expected, test.items, nil, false)
			wantEvents := []string{"project:first_window_inventory", "uia", "sleep:250ms", "project:second_window_inventory", "uia"}
			if got.result.Status != "passed" || got.samples != 2 || got.members != 4 || got.uia != 2 || got.reports != 0 || len(got.sleeps) != 1 || got.sleeps[0] != 250*time.Millisecond || len(got.statuses) != 2 || got.statuses[0] != hiddenDirectMainExact || got.statuses[1] != hiddenDirectMainExact || strings.Join(got.events, ",") != strings.Join(wantEvents, ",") || got.result.Receipt.ActionCount != 0 {
				t.Fatalf("connected success order changed: result=%#v samples=%d members=%d uia=%d sleeps=%v statuses=%v events=%v", got.result, got.samples, got.members, got.uia, got.sleeps, got.statuses, got.events)
			}
		})
	}
}

func TestHiddenDirectConnectedSuccessPreservesTwelveMembershipCalls(t *testing.T) {
	main, inventory, rows, markerHash, _ := hiddenDirectObservationFixture()
	expected := main
	expected.HWND = 0
	current := time.Unix(0, 0)
	samples, members, uia := 0, 0, 0
	var sleeps []time.Duration
	member := func(uint32) bool {
		members++
		return true
	}
	result := observeHiddenDirectInWorkerLoop(markerHash, func() hiddenDirectFencedSample {
		samples++
		for index := 0; index < 4; index++ {
			if !member(main.PID) {
				t.Fatal("synthetic fence membership failed")
			}
		}
		return hiddenDirectFencedSample{Status: hiddenDirectFenceObserved, InventoryStatus: hiddenDirectInventoryNonEmpty, Windows: append([]hiddenWindowIdentity(nil), inventory...)}
	}, expected, member, func(uintptr, uint32) ([]hiddenDirectUIARow, error) {
		uia++
		return append([]hiddenDirectUIARow(nil), rows...), nil
	}, func(hiddenDirectPreReceiptDiagnostic) error {
		t.Fatal("successful path emitted a diagnostic")
		return nil
	}, func() time.Time {
		return current
	}, func(value time.Duration) {
		sleeps = append(sleeps, value)
	}, func(string, hiddenDirectMainStatus, hiddenDirectMainStatus, bool, hiddenDirectInventoryCause) {})
	if result.Status != "passed" || samples != 2 || members != 12 || uia != 2 || len(sleeps) != 1 || sleeps[0] != 250*time.Millisecond || result.Receipt.ActionCount != 0 || result.Receipt.RawUIRetained {
		t.Fatalf("successful predecessor calls changed: result=%#v inventories=%d members=%d uia=%d sleeps=%v", result, samples, members, uia, sleeps)
	}
}

func TestHiddenDirectSecondPredicateProvenanceReplayAndProjection(t *testing.T) {
	main, inventory, _, _, _ := hiddenDirectObservationFixture()
	tests := []struct {
		name       string
		expected   hiddenWindowIdentity
		items      []hiddenWindowIdentity
		nilMember  bool
		incomplete bool
		want       hiddenDirectMainStatus
		cause      hiddenDirectInventoryCause
		members    int
		uia        int
		wantOK     bool
	}{
		{name: "exact", expected: main, items: inventory, want: hiddenDirectMainExact, cause: hiddenDirectCauseExactMain, members: 1, uia: 1, wantOK: true},
		{name: "valid empty", expected: main, want: hiddenDirectMainAbsent, cause: hiddenDirectCauseSuccessfulEmpty},
		{name: "zero hwnd provenance", expected: func() hiddenWindowIdentity { value := main; value.HWND, value.OwnerHWND = 0, 1; return value }(), items: inventory, want: hiddenDirectMainInvalid},
		{name: "zero hwnd provenance empty", expected: func() hiddenWindowIdentity { value := main; value.HWND, value.OwnerHWND = 0, 1; return value }(), want: hiddenDirectMainInvalid},
		{name: "zero pid provenance", expected: func() hiddenWindowIdentity { value := main; value.PID = 0; return value }(), items: inventory, want: hiddenDirectMainInvalid},
		{name: "self owner provenance", expected: func() hiddenWindowIdentity { value := main; value.OwnerHWND = value.HWND; return value }(), items: inventory, want: hiddenDirectMainInvalid},
		{name: "empty class provenance", expected: func() hiddenWindowIdentity { value := main; value.ClassName = ""; return value }(), items: inventory, want: hiddenDirectMainInvalid},
		{name: "class length provenance", expected: func() hiddenWindowIdentity { value := main; value.ClassName = strings.Repeat("x", 257); return value }(), items: inventory, want: hiddenDirectMainInvalid},
		{name: "uppercase hash provenance", expected: func() hiddenWindowIdentity {
			value := main
			value.DesktopHash = strings.ToUpper(value.DesktopHash)
			return value
		}(), items: []hiddenWindowIdentity{func() hiddenWindowIdentity {
			value := main
			value.DesktopHash = strings.ToUpper(value.DesktopHash)
			return value
		}()}, want: hiddenDirectMainInvalid},
		{name: "malformed hash provenance", expected: func() hiddenWindowIdentity { value := main; value.DesktopHash = "bad"; return value }(), items: inventory, want: hiddenDirectMainInvalid},
		{name: "mismatched hwnd", expected: func() hiddenWindowIdentity { value := main; value.HWND++; return value }(), items: inventory, want: hiddenDirectMainInvalid, members: 1},
		{name: "nil membership", expected: main, items: inventory, nilMember: true, incomplete: true, want: hiddenDirectMainInvalid},
		{name: "class spelling drift", expected: main, items: []hiddenWindowIdentity{func() hiddenWindowIdentity {
			value := main
			value.ClassName = strings.ToLower(value.ClassName)
			return value
		}()}, want: hiddenDirectMainInvalid, members: 1},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			calls, uia := 0, 0
			member := func(uint32) bool { calls++; return true }
			if test.nilMember {
				member = nil
			}
			sample := hiddenDirectFencedSample{Status: hiddenDirectFenceObserved, InventoryStatus: hiddenDirectInventoryNonEmpty}
			if len(test.items) == 0 {
				sample.InventoryStatus = hiddenDirectInventoryEmpty
			}
			gotStatus := hiddenDirectMainUnchecked
			gotCause := hiddenDirectInventoryCause("")
			gotComplete := false
			_, err := observeHiddenDirectAfterReadmissionClassified(test.expected, test.items, member, func(status, _ hiddenDirectMainStatus, complete bool) error {
				gotStatus = status
				gotComplete = complete
				var causeErr error
				gotCause, causeErr = classifyHiddenDirectInventoryCause(sample, status)
				return causeErr
			}, func(uintptr, uint32) ([]hiddenDirectUIARow, error) {
				uia++
				return nil, nil
			})
			if (err == nil) != test.wantOK || gotStatus != test.want || gotComplete == test.incomplete || gotCause != test.cause || calls != test.members || uia != test.uia {
				t.Fatalf("second predicate mismatch: err=%v status=%q/%q complete=%v cause=%q/%q members=%d/%d uia=%d/%d", err, gotStatus, test.want, gotComplete, gotCause, test.cause, calls, test.members, uia, test.uia)
			}
		})
	}
}

func TestHiddenDirectSecondObserverNilPrecedesAdmission(t *testing.T) {
	main, inventory, _, _, _ := hiddenDirectObservationFixture()
	memberCalls, projectionCalls := 0, 0
	_, err := observeHiddenDirectAfterReadmissionClassified(main, inventory, func(uint32) bool {
		memberCalls++
		return true
	}, func(hiddenDirectMainStatus, hiddenDirectMainStatus, bool) error {
		projectionCalls++
		return nil
	}, nil)
	if err == nil || memberCalls != 0 || projectionCalls != 0 {
		t.Fatalf("nil observer did not precede admission: err=%v members=%d projections=%d", err, memberCalls, projectionCalls)
	}
}

func TestHiddenDirectSecondExpectedIdentityRules(t *testing.T) {
	main, _, _, _, _ := hiddenDirectObservationFixture()
	tests := []struct {
		name     string
		expected hiddenWindowIdentity
		member   func(uint32) bool
		want     hiddenDirectMainStatus
	}{
		{name: "valid empty", expected: main, member: func(uint32) bool { return true }, want: hiddenDirectMainAbsent},
		{name: "zero hwnd", expected: func() hiddenWindowIdentity { value := main; value.HWND, value.OwnerHWND = 0, 1; return value }(), member: func(uint32) bool { return true }, want: hiddenDirectMainInvalid},
		{name: "zero pid", expected: func() hiddenWindowIdentity { value := main; value.PID = 0; return value }(), member: func(uint32) bool { return true }, want: hiddenDirectMainInvalid},
		{name: "self owner", expected: func() hiddenWindowIdentity { value := main; value.OwnerHWND = value.HWND; return value }(), member: func(uint32) bool { return true }, want: hiddenDirectMainInvalid},
		{name: "empty class", expected: func() hiddenWindowIdentity { value := main; value.ClassName = ""; return value }(), member: func(uint32) bool { return true }, want: hiddenDirectMainInvalid},
		{name: "class length", expected: func() hiddenWindowIdentity { value := main; value.ClassName = strings.Repeat("x", 257); return value }(), member: func(uint32) bool { return true }, want: hiddenDirectMainInvalid},
		{name: "malformed hash", expected: func() hiddenWindowIdentity { value := main; value.DesktopHash = "bad"; return value }(), member: func(uint32) bool { return true }, want: hiddenDirectMainInvalid},
		{name: "nil membership", expected: main, want: hiddenDirectMainInvalid},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if got := hiddenDirectMainInventoryStatusFor(nil, test.expected, test.member, true); got != test.want {
				t.Fatalf("second expected identity mismatch: got=%q want=%q", got, test.want)
			}
		})
	}
}

func TestHiddenDirectMembershipReplayIsCallNeutralAndExactlyConsumed(t *testing.T) {
	memberCalls := 0
	record, replay, complete := hiddenDirectRecordedMembership(func(pid uint32) bool {
		memberCalls++
		return pid%2 == 0
	})
	if !record(2) || record(3) || memberCalls != 2 || complete() {
		t.Fatal("recording membership did not retain ordered booleans")
	}
	if !replay(999) || memberCalls != 2 || complete() {
		t.Fatal("partial replay called membership or accepted surplus")
	}
	if replay(888) || memberCalls != 2 || !complete() {
		t.Fatal("exact replay did not consume the ordered record")
	}
	if replay(777) || complete() || memberCalls != 2 {
		t.Fatal("replay underflow was accepted or called membership")
	}
	missingRecord, missingReplay, missingComplete := hiddenDirectRecordedMembership(nil)
	if missingRecord != nil || missingReplay != nil || missingComplete() {
		t.Fatal("nil membership produced a valid replay")
	}
}

func TestHiddenDirectAdmissionReplayDisagreementIsInvalid(t *testing.T) {
	main, _, _, _, _ := hiddenDirectObservationFixture()
	drift := main
	drift.ClassName = strings.ToLower(drift.ClassName)
	tests := []struct {
		name     string
		replayed hiddenDirectMainStatus
		complete bool
		current  hiddenWindowIdentity
		err      error
		exactID  bool
		want     hiddenDirectMainStatus
	}{
		{name: "exact agreement", replayed: hiddenDirectMainExact, complete: true, current: main, exactID: true, want: hiddenDirectMainExact},
		{name: "first exact agreement", replayed: hiddenDirectMainExact, complete: true, current: drift, want: hiddenDirectMainExact},
		{name: "absence agreement", replayed: hiddenDirectMainAbsent, complete: true, err: errors.New("broad"), want: hiddenDirectMainAbsent},
		{name: "success versus absence", replayed: hiddenDirectMainAbsent, complete: true, current: main, want: hiddenDirectMainInvalid},
		{name: "error versus exact", replayed: hiddenDirectMainExact, complete: true, err: errors.New("broad"), want: hiddenDirectMainInvalid},
		{name: "invalid replay", replayed: hiddenDirectMainInvalid, complete: true, err: errors.New("broad"), want: hiddenDirectMainInvalid},
		{name: "identity drift", replayed: hiddenDirectMainExact, complete: true, current: drift, exactID: true, want: hiddenDirectMainInvalid},
		{name: "incomplete replay", replayed: hiddenDirectMainExact, current: main, exactID: true, want: hiddenDirectMainInvalid},
	}
	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			if got := hiddenDirectMainAdmissionStatus(test.replayed, test.complete, test.current, main, test.err, test.exactID); got != test.want {
				t.Fatalf("admission/replay disagreement mismatch: got=%q want=%q", got, test.want)
			}
		})
	}
}

func TestHiddenDirectWindowsInventoryCauseMappingIsClosed(t *testing.T) {
	data, err := os.ReadFile("hidden_desktop_window_isolation_windows.go")
	if err != nil {
		t.Fatal(err)
	}
	text := string(data)
	for _, token := range []string{
		"hiddenWindowInventoryFailureOpen",
		"hiddenWindowInventoryFailureEnumerate",
		"hiddenWindowInventoryFailureOverflow",
		"hiddenDirectInventoryFailureHiddenOpen",
		"hiddenDirectInventoryFailureHiddenEnumerate",
		"hiddenDirectInventoryFailureHiddenOverflow",
		"hiddenDirectInventoryFailureOperatorOpen",
		"hiddenDirectInventoryFailureOperatorEnumerate",
		"hiddenDirectInventoryFailureOperatorOverflow",
		"hiddenDirectInventoryFailureIsolation",
	} {
		if !strings.Contains(text, token) {
			t.Fatalf("classified Windows inventory source is disconnected: %s", token)
		}
	}
	if strings.Count(text, "hiddenWindowOpenDesktop.Call(") != 1 || strings.Count(text, "hiddenWindowEnumDesktop.Call(") != 1 {
		t.Fatal("classified inventory changed the existing Windows open/enumeration call surface")
	}
	for _, forbidden := range []string{"err.Error()", "callErr.Error()", "enumErr.Error()"} {
		if strings.Contains(text, forbidden) {
			t.Fatalf("classified inventory parses raw error text: %s", forbidden)
		}
	}
}

func hiddenDirectObservationFixture() (hiddenWindowIdentity, []hiddenWindowIdentity, []hiddenDirectUIARow, string, func(uint32) bool) {
	desktopHash := hiddenWindowHash(`Winsta0\qa-mcp-0123456789abcdef`)
	main := hiddenWindowIdentity{HWND: 101, PID: 4200, ClassName: "V8TopLevelFrameSDI", DesktopHash: desktopHash}
	markerHash := hiddenWindowHash("synthetic-secret-marker")
	rows := []hiddenDirectUIARow{
		{PID: 4200, ControlTypeHash: hiddenWindowHash("ControlType.Window"), ClassHash: hiddenWindowHash("V8TopLevelFrameSDI"), AutomationIDHash: hiddenWindowHash("root"), NameHash: hiddenWindowHash("opaque-root"), PathHash: hiddenWindowHash("path/root")},
		{PID: 4200, ControlTypeHash: hiddenWindowHash("ControlType.Text"), ClassHash: hiddenWindowHash("Static"), AutomationIDHash: hiddenWindowHash("marker"), NameHash: markerHash, PathHash: hiddenWindowHash("path/root/marker")},
	}
	return main, []hiddenWindowIdentity{main}, rows, markerHash, func(pid uint32) bool { return pid == 4200 }
}

func TestHiddenDirectObservationExactStableReceipt(t *testing.T) {
	main, inventory, rows, markerHash, member := hiddenDirectObservationFixture()
	receipt, err := admitHiddenDirectObservation(main, inventory, inventory, markerHash, rows, append([]hiddenDirectUIARow(nil), rows...), member)
	if err != nil || receipt.Status != hiddenDirectObservationObserved || receipt.MarkerMatchCount != 1 || receipt.ControlCount != 2 || receipt.ActionCount != 0 || receipt.RawUIRetained || !validHiddenWindowHash(receipt.MainIdentityHash) || !validHiddenWindowHash(receipt.TopologyHash) {
		t.Fatalf("exact passive observation rejected: %#v %v", receipt, err)
	}
	if err := validateHiddenDirectObservationReceipt(receipt); err != nil {
		t.Fatal(err)
	}
}

func TestHiddenDirectObservationHostileIdentityFailsClosed(t *testing.T) {
	baseMain, baseInventory, rows, markerHash, member := hiddenDirectObservationFixture()
	cases := map[string]func(*hiddenWindowIdentity, *[]hiddenWindowIdentity, *func(uint32) bool){
		"missing main": func(_ *hiddenWindowIdentity, inventory *[]hiddenWindowIdentity, _ *func(uint32) bool) {
			*inventory = nil
		},
		"duplicate main": func(_ *hiddenWindowIdentity, inventory *[]hiddenWindowIdentity, _ *func(uint32) bool) {
			*inventory = append(*inventory, (*inventory)[0])
		},
		"foreign pid": func(_ *hiddenWindowIdentity, inventory *[]hiddenWindowIdentity, _ *func(uint32) bool) {
			(*inventory)[0].PID = 4300
		},
		"foreign job": func(_ *hiddenWindowIdentity, _ *[]hiddenWindowIdentity, member *func(uint32) bool) {
			*member = func(uint32) bool { return false }
		},
		"foreign desktop": func(_ *hiddenWindowIdentity, inventory *[]hiddenWindowIdentity, _ *func(uint32) bool) {
			(*inventory)[0].DesktopHash = hiddenWindowHash(`Winsta0\foreign`)
		},
		"foreign window": func(_ *hiddenWindowIdentity, inventory *[]hiddenWindowIdentity, _ *func(uint32) bool) {
			(*inventory)[0].ClassName = "Foreign"
		},
		"changed hwnd": func(main *hiddenWindowIdentity, _ *[]hiddenWindowIdentity, _ *func(uint32) bool) { main.HWND = 102 },
	}
	for name, mutate := range cases {
		t.Run(name, func(t *testing.T) {
			main := baseMain
			inventory := append([]hiddenWindowIdentity(nil), baseInventory...)
			currentMember := member
			mutate(&main, &inventory, &currentMember)
			receipt, err := admitHiddenDirectObservation(main, inventory, inventory, markerHash, rows, rows, currentMember)
			if err == nil || receipt.ActionCount != 0 {
				t.Fatalf("hostile identity admitted action: %#v %v", receipt, err)
			}
		})
	}
}

func TestHiddenDirectObservationMarkerAndTopologyFailClosed(t *testing.T) {
	main, inventory, baseRows, markerHash, member := hiddenDirectObservationFixture()
	cases := map[string]func(*string, *[]hiddenDirectUIARow, *[]hiddenDirectUIARow){
		"invalid marker hash": func(hash *string, _, _ *[]hiddenDirectUIARow) { *hash = "raw-marker" },
		"missing marker": func(_ *string, first, second *[]hiddenDirectUIARow) {
			(*first)[1].NameHash = hiddenWindowHash("other")
			(*second)[1].NameHash = hiddenWindowHash("other")
		},
		"duplicate marker": func(_ *string, first, second *[]hiddenDirectUIARow) {
			(*first)[0].NameHash = markerHash
			(*second)[0].NameHash = markerHash
		},
		"foreign UIA pid": func(_ *string, first, second *[]hiddenDirectUIARow) { (*first)[1].PID = 4300; (*second)[1].PID = 4300 },
		"ambiguous topology": func(_ *string, first, second *[]hiddenDirectUIARow) {
			(*first)[1].PathHash = (*first)[0].PathHash
			(*second)[1].PathHash = (*second)[0].PathHash
		},
		"changed topology": func(_ *string, _, second *[]hiddenDirectUIARow) {
			(*second)[1].AutomationIDHash = hiddenWindowHash("changed")
		},
	}
	for name, mutate := range cases {
		t.Run(name, func(t *testing.T) {
			hash := markerHash
			first := append([]hiddenDirectUIARow(nil), baseRows...)
			second := append([]hiddenDirectUIARow(nil), baseRows...)
			mutate(&hash, &first, &second)
			receipt, err := admitHiddenDirectObservation(main, inventory, inventory, hash, first, second, member)
			if err == nil || receipt.ActionCount != 0 {
				t.Fatalf("hostile observation admitted action: %#v %v", receipt, err)
			}
		})
	}
}

func TestHiddenDirectObservationSecondMainSnapshotChangedFailsClosed(t *testing.T) {
	main, inventory, rows, markerHash, member := hiddenDirectObservationFixture()
	second := append([]hiddenWindowIdentity(nil), inventory...)
	second[0].HWND++
	receipt, err := admitHiddenDirectObservation(main, inventory, second, markerHash, rows, rows, member)
	if err == nil || receipt.ActionCount != 0 {
		t.Fatalf("changed second main identity admitted action: %#v %v", receipt, err)
	}
}

func TestHiddenDirectObservationReadmissionPrecedesSecondTraversal(t *testing.T) {
	main, inventory, _, _, member := hiddenDirectObservationFixture()
	second := append([]hiddenWindowIdentity(nil), inventory...)
	second[0].HWND++
	observerCalls := 0
	_, err := observeHiddenDirectAfterReadmission(main, second, member, func(uintptr, uint32) ([]hiddenDirectUIARow, error) {
		observerCalls++
		return nil, nil
	})
	if err == nil || observerCalls != 0 {
		t.Fatalf("changed identity reached passive observer: calls=%d err=%v", observerCalls, err)
	}
}

func TestHiddenDirectObservationReceiptRejectsLeakageAndAction(t *testing.T) {
	main, inventory, rows, markerHash, member := hiddenDirectObservationFixture()
	receipt, err := admitHiddenDirectObservation(main, inventory, inventory, markerHash, rows, rows, member)
	if err != nil {
		t.Fatal(err)
	}
	receipt.ActionCount = 1
	if validateHiddenDirectObservationReceipt(receipt) == nil {
		t.Fatal("non-zero action count was admitted")
	}
	receipt.ActionCount, receipt.RawUIRetained = 0, true
	if validateHiddenDirectObservationReceipt(receipt) == nil {
		t.Fatal("raw UI retention was admitted")
	}
	receipt.RawUIRetained = false
	data, err := json.Marshal(receipt)
	if err != nil {
		t.Fatal(err)
	}
	serialized := strings.ToLower(string(data))
	for _, forbidden := range []string{"synthetic-secret-marker", "credential", "password", "connection_string", "title", "geometry", "screenshot", "ui_text"} {
		if strings.Contains(serialized, forbidden) {
			t.Fatalf("receipt leaked forbidden field/value %q", forbidden)
		}
	}
}

func TestHiddenDirectObservationSourceIsDormantAndActionFree(t *testing.T) {
	for _, name := range []string{"hidden_direct_execute_observation.go", "hidden_direct_execute_observation_windows.go"} {
		data, err := os.ReadFile(name)
		if err != nil {
			t.Fatal(err)
		}
		for _, forbidden := range []string{"SendInput", "SetCursorPos", "SetForegroundWindow", "SwitchDesktop", "mouse_event", "keybd_event", "PostMessage", "SendMessage", ".Invoke(", ".SetValue(", ".SetFocus(", "ValuePattern.SetValue", "InvokePattern.Invoke"} {
			if strings.Contains(string(data), forbidden) {
				t.Fatalf("%s contains forbidden action primitive %s", name, forbidden)
			}
		}
	}
	entries, err := os.ReadDir(".")
	if err != nil {
		t.Fatal(err)
	}
	for _, entry := range entries {
		name := entry.Name()
		if entry.IsDir() || !strings.HasSuffix(name, ".go") || strings.HasSuffix(name, "_test.go") || strings.HasPrefix(name, "hidden_direct_execute_observation") {
			continue
		}
		data, err := os.ReadFile(name)
		if err != nil {
			t.Fatal(err)
		}
		if strings.Contains(string(data), "admitHiddenDirectObservation(") || strings.Contains(string(data), "observeHiddenDirectUIA(") {
			t.Fatalf("S4 primitive has non-test caller in %s", name)
		}
	}
}
