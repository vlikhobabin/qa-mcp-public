package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func exactS5PromptFixture() (hiddenWindowIdentity, map[uintptr]struct{}, hiddenPromptS5Snapshot) {
	desktop := hiddenWindowHash(`Winsta0\qa-mcp-s5`)
	main := hiddenWindowIdentity{HWND: 100, PID: 4100, ClassName: "V8TopLevelFrameSDI", DesktopHash: desktop}
	prompt := hiddenWindowIdentity{HWND: 200, PID: 4100, ClassName: hiddenPromptS5Class, OwnerHWND: main.HWND, DesktopHash: desktop}
	rows := make([]hiddenPromptS5Control, 26)
	for index := range rows {
		rows[index] = hiddenPromptS5Control{
			PID:              main.PID,
			ControlTypeHash:  hiddenWindowHash("control-" + string(rune('a'+index))),
			PathHash:         hiddenWindowHash("path-" + string(rune('a'+index))),
			GeometryHash:     hiddenWindowHash("geometry-" + string(rune('a'+index))),
			RootGeometryHash: hiddenWindowHash("root"),
			Enabled:          index < 5,
			Offscreen:        false,
			Invoke:           index < 5,
		}
	}
	rows[0].ControlTypeHash = hiddenWindowHash("ControlType.Button")
	rows[0].PathHash = hiddenPromptS5ActionPathHash
	rows[0].Bottom, rows[0].HorizontalRank, rows[0].HorizontalPeerCount = true, 0, 2
	return main, map[uintptr]struct{}{55: {}}, hiddenPromptS5Snapshot{
		Main: main, Prompt: prompt, StableSamples: 2, CandidateCount: 1,
		NewAfterLaunch: true, PatternHash: hiddenWindowHash("prompt-pattern"), Controls: rows,
	}
}

func exactS5Post(main hiddenWindowIdentity) hiddenPromptS5PostState {
	return hiddenPromptS5PostState{Observation: hiddenDirectObservationReceipt{
		Schema: hiddenDirectObservationSchema, Status: hiddenDirectObservationObserved,
		MainIdentityHash: hiddenDirectMainIdentityHash(main), ExpectedMarkerHash: hiddenWindowHash("marker"),
		TopologyHash: hiddenWindowHash("topology"), MarkerMatchCount: 1, ControlCount: 4,
	}}
}

func cloneS5Prompt(value hiddenPromptS5Snapshot) hiddenPromptS5Snapshot {
	value.Controls = append([]hiddenPromptS5Control(nil), value.Controls...)
	return value
}

func runS5Prompt(first, second hiddenPromptS5Snapshot, baseline map[uintptr]struct{}, ledger *hiddenPromptS5Ledger, actionCalls, postCalls *int) (hiddenPromptS5Receipt, error) {
	action := func(hwnd uintptr, control hiddenPromptS5Control) (bool, uint64, error) {
		*actionCalls++
		if hwnd != first.Prompt.HWND || control.PathHash != hiddenPromptS5ActionPathHash {
			testingError := os.ErrInvalid
			return false, 0, testingError
		}
		return true, 2, nil
	}
	post := func() (hiddenPromptS5PostState, error) {
		*postCalls++
		return exactS5Post(first.Main), nil
	}
	return admitAndConfirmHiddenPromptS5(first.Main, baseline, first, second, func(pid uint32) bool { return pid == first.Main.PID }, ledger, action, post)
}

func TestHiddenPromptS5ExactAdmissionIsSingleUse(t *testing.T) {
	main, baseline, first := exactS5PromptFixture()
	second, ledger, actionCalls, postCalls := first, &hiddenPromptS5Ledger{}, 0, 0
	receipt, err := runS5Prompt(first, second, baseline, ledger, &actionCalls, &postCalls)
	if err != nil {
		t.Fatalf("exact prompt rejected: %v", err)
	}
	if receipt.Status != hiddenPromptS5Confirmed || receipt.MainIdentityHash != hiddenDirectMainIdentityHash(main) ||
		receipt.ActionAttempts != 1 || receipt.FocusCalls != 1 || receipt.KeyMessages != 2 || !receipt.PromptClosed ||
		receipt.RawUIRetained || actionCalls != 1 || postCalls != 1 || ledger.Attempts != 1 {
		t.Fatalf("unexpected exact receipt: %#v calls=%d/%d ledger=%#v", receipt, actionCalls, postCalls, ledger)
	}
	actionCalls, postCalls = 0, 0
	if _, err := runS5Prompt(first, second, baseline, ledger, &actionCalls, &postCalls); err == nil || actionCalls != 0 || postCalls != 0 {
		t.Fatalf("used action ledger was not fail-closed: action=%d post=%d", actionCalls, postCalls)
	}
}

func TestHiddenPromptS5RejectsWindowIdentityBeforeCallbacks(t *testing.T) {
	main, baseline, exact := exactS5PromptFixture()
	hostiles := []hiddenPromptS5Snapshot{
		func() hiddenPromptS5Snapshot { value := exact; value.Prompt = hiddenWindowIdentity{}; return value }(),
		func() hiddenPromptS5Snapshot { value := exact; value.NewAfterLaunch = false; return value }(),
		func() hiddenPromptS5Snapshot { value := exact; value.CandidateCount = 2; return value }(),
		func() hiddenPromptS5Snapshot { value := exact; value.Prompt.PID++; return value }(),
		func() hiddenPromptS5Snapshot {
			value := exact
			value.Prompt.DesktopHash = hiddenWindowHash("foreign")
			return value
		}(),
		func() hiddenPromptS5Snapshot { value := exact; value.Prompt.OwnerHWND++; return value }(),
		func() hiddenPromptS5Snapshot { value := exact; value.Prompt.ClassName = "#32770"; return value }(),
		func() hiddenPromptS5Snapshot { value := exact; value.StableSamples = 1; return value }(),
	}
	for index, hostile := range hostiles {
		actionCalls, postCalls := 0, 0
		if _, err := runS5Prompt(hostile, hostile, baseline, &hiddenPromptS5Ledger{}, &actionCalls, &postCalls); err == nil || actionCalls != 0 || postCalls != 0 {
			t.Fatalf("hostile %d reached callback: action=%d post=%d", index, actionCalls, postCalls)
		}
	}
	actionCalls, postCalls := 0, 0
	if _, err := admitAndConfirmHiddenPromptS5(exact.Main, baseline, exact, exact, func(uint32) bool { return false }, &hiddenPromptS5Ledger{},
		func(uintptr, hiddenPromptS5Control) (bool, uint64, error) { actionCalls++; return true, 2, nil },
		func() (hiddenPromptS5PostState, error) { postCalls++; return exactS5Post(exact.Main), nil }); err == nil || actionCalls != 0 || postCalls != 0 {
		t.Fatalf("foreign job identity reached callback")
	}
	oldBaseline := map[uintptr]struct{}{exact.Prompt.HWND: {}}
	actionCalls, postCalls = 0, 0
	if _, err := runS5Prompt(exact, exact, oldBaseline, &hiddenPromptS5Ledger{}, &actionCalls, &postCalls); err == nil || actionCalls != 0 || postCalls != 0 {
		t.Fatalf("launch-baseline prompt reached callback")
	}
	changed := exact
	changed.Main.HWND = main.HWND + 1
	for index, pair := range [][2]hiddenPromptS5Snapshot{{exact, changed}, {exact, func() hiddenPromptS5Snapshot { value := exact; value.Prompt.HWND++; return value }()}} {
		actionCalls, postCalls := 0, 0
		if _, err := runS5Prompt(pair[0], pair[1], baseline, &hiddenPromptS5Ledger{}, &actionCalls, &postCalls); err == nil || actionCalls != 0 || postCalls != 0 {
			t.Fatalf("changed identity %d reached callback", index)
		}
	}
}

func TestHiddenPromptS5IgnoresUnrelatedInventoryFingerprintDrift(t *testing.T) {
	_, baseline, exact := exactS5PromptFixture()
	first := cloneS5Prompt(exact)
	first.StableSamples = 3 // isolate legacy whole-inventory gates from its three-sample gate
	first.PatternHash = hiddenWindowHash("diagnostic-pattern-first")
	first.Controls = first.Controls[:25]
	second := cloneS5Prompt(exact)
	second.StableSamples = 3
	second.PatternHash = hiddenWindowHash("diagnostic-pattern-second")
	unrelated := second.Controls[25]
	unrelated.PID++
	unrelated.PathHash = "diagnostic-only"
	unrelated.Enabled, unrelated.Invoke, unrelated.Value = true, true, true
	second.Controls = append(second.Controls, unrelated)

	ledger, actionCalls, postCalls := &hiddenPromptS5Ledger{}, 0, 0
	receipt, err := runS5Prompt(first, second, baseline, ledger, &actionCalls, &postCalls)
	if err != nil {
		t.Fatalf("unrelated inventory drift rejected: %v", err)
	}
	if receipt.ControlCount != len(first.Controls) || receipt.PatternHash != first.PatternHash ||
		actionCalls != 1 || postCalls != 1 || ledger.Attempts != 1 {
		t.Fatalf("unexpected diagnostic-only receipt: %#v calls=%d/%d", receipt, actionCalls, postCalls)
	}
}

func TestHiddenPromptS5RejectsControlAndGeometryDriftBeforeCallbacks(t *testing.T) {
	_, baseline, exact := exactS5PromptFixture()
	hostiles := []hiddenPromptS5Snapshot{
		func() hiddenPromptS5Snapshot {
			value := cloneS5Prompt(exact)
			value.Controls[0].PID++
			return value
		}(),
		func() hiddenPromptS5Snapshot {
			value := cloneS5Prompt(exact)
			value.Controls[0].GeometryHash = "raw"
			return value
		}(),
		func() hiddenPromptS5Snapshot {
			value := cloneS5Prompt(exact)
			value.Controls[0].Enabled = false
			return value
		}(),
		func() hiddenPromptS5Snapshot {
			value := cloneS5Prompt(exact)
			value.Controls[0].ReadOnly = true
			return value
		}(),
		func() hiddenPromptS5Snapshot {
			value := cloneS5Prompt(exact)
			value.Controls[0].Offscreen = true
			return value
		}(),
		func() hiddenPromptS5Snapshot {
			value := cloneS5Prompt(exact)
			value.Controls[0].Invoke = false
			return value
		}(),
		func() hiddenPromptS5Snapshot {
			value := cloneS5Prompt(exact)
			value.Controls[1].PathHash = hiddenPromptS5ActionPathHash
			value.Controls[1].ControlTypeHash = hiddenWindowHash("ControlType.Button")
			value.Controls[1].Enabled = true
			value.Controls[1].Invoke = true
			value.Controls[1].Bottom, value.Controls[1].HorizontalRank, value.Controls[1].HorizontalPeerCount = true, 0, 2
			return value
		}(),
	}
	for index, hostile := range hostiles {
		actionCalls, postCalls := 0, 0
		if _, err := runS5Prompt(hostile, hostile, baseline, &hiddenPromptS5Ledger{}, &actionCalls, &postCalls); err == nil || actionCalls != 0 || postCalls != 0 {
			t.Fatalf("hostile topology %d reached callback", index)
		}
	}
	for index, second := range []hiddenPromptS5Snapshot{
		func() hiddenPromptS5Snapshot {
			value := cloneS5Prompt(exact)
			value.Controls[0].GeometryHash = hiddenWindowHash("moved")
			return value
		}(),
		func() hiddenPromptS5Snapshot {
			value := cloneS5Prompt(exact)
			value.Controls[0].RootGeometryHash = hiddenWindowHash("resized")
			return value
		}(),
		func() hiddenPromptS5Snapshot {
			value := cloneS5Prompt(exact)
			value.Controls[0].PathHash = hiddenWindowHash("replaced")
			return value
		}(),
	} {
		actionCalls, postCalls := 0, 0
		if _, err := runS5Prompt(exact, second, baseline, &hiddenPromptS5Ledger{}, &actionCalls, &postCalls); err == nil || actionCalls != 0 || postCalls != 0 {
			t.Fatalf("readmission drift %d reached callback", index)
		}
	}
}

func TestHiddenPromptS5RejectsPostStateWithoutRetry(t *testing.T) {
	_, baseline, exact := exactS5PromptFixture()
	tests := []hiddenPromptS5PostState{
		func() hiddenPromptS5PostState {
			value := exactS5Post(exact.Main)
			value.PromptWindows = []hiddenWindowIdentity{exact.Prompt}
			return value
		}(),
		func() hiddenPromptS5PostState {
			value := exactS5Post(exact.Main)
			value.OperatorWindowCount = 1
			return value
		}(),
		func() hiddenPromptS5PostState {
			value := exactS5Post(exact.Main)
			value.Observation.MainIdentityHash = hiddenWindowHash("changed")
			return value
		}(),
		func() hiddenPromptS5PostState {
			value := exactS5Post(exact.Main)
			value.Observation.MarkerMatchCount = 0
			return value
		}(),
	}
	for index, state := range tests {
		ledger, actionCalls, postCalls := &hiddenPromptS5Ledger{}, 0, 0
		action := func(uintptr, hiddenPromptS5Control) (bool, uint64, error) { actionCalls++; return true, 2, nil }
		post := func() (hiddenPromptS5PostState, error) { postCalls++; return state, nil }
		receipt, err := admitAndConfirmHiddenPromptS5(exact.Main, baseline, exact, exact, func(pid uint32) bool { return pid == exact.Main.PID }, ledger, action, post)
		if err == nil || actionCalls != 1 || postCalls != 1 || ledger.Attempts != 1 || receipt.ActionAttempts != 1 {
			t.Fatalf("post-state %d retried or passed: receipt=%#v calls=%d/%d", index, receipt, actionCalls, postCalls)
		}
	}
}

func TestHiddenPromptS5InventoryDiagnosticIsTypedAndBounded(t *testing.T) {
	valid := hiddenPromptS5InventoryDiagnostic{Code: "observed", Complete: true, HashesValid: true, RowCount: 26, ExactPIDCount: 25, TargetMatchCount: 1}
	if err := validateHiddenPromptS5InventoryDiagnostic(valid); err != nil {
		t.Fatal(err)
	}
	hostiles := []hiddenPromptS5InventoryDiagnostic{
		{Code: "credential-value", RowCount: 1},
		{Code: "observed", Complete: true, HashesValid: true, RowCount: 129},
		{Code: "observed", Complete: true, HashesValid: true, RowCount: 1, ExactPIDCount: 2},
		{Code: "observed", Complete: true, HashesValid: true, RowCount: 1, TargetMatchCount: 2},
		{Code: "observed", Complete: false, HashesValid: true, RowCount: 1},
		{Code: "row_failed", Complete: true, HashesValid: true, RowCount: 1},
		{Code: "observed", Complete: true, HashesValid: false, RowCount: 1},
	}
	for index, hostile := range hostiles {
		if validateHiddenPromptS5InventoryDiagnostic(hostile) == nil {
			t.Fatalf("hostile diagnostic %d was admitted: %#v", index, hostile)
		}
	}
	encoded, err := json.Marshal(valid)
	if err != nil {
		t.Fatal(err)
	}
	for _, forbidden := range []string{"credential", "password", "title", "text", "coordinate", "exception"} {
		if strings.Contains(strings.ToLower(string(encoded)), forbidden) {
			t.Fatalf("diagnostic retained forbidden field: %s", forbidden)
		}
	}
}

func TestHiddenPromptS5ReceiptAndSourcesRetainNoRawUI(t *testing.T) {
	_, baseline, exact := exactS5PromptFixture()
	ledger, actionCalls, postCalls := &hiddenPromptS5Ledger{}, 0, 0
	receipt, err := runS5Prompt(exact, exact, baseline, ledger, &actionCalls, &postCalls)
	if err != nil {
		t.Fatal(err)
	}
	encoded, err := json.Marshal(receipt)
	if err != nil {
		t.Fatal(err)
	}
	for _, forbidden := range []string{"credential", "password", "connection", "title", "raw_ui_text", "screenshot", "coordinate"} {
		if strings.Contains(strings.ToLower(string(encoded)), forbidden) {
			t.Fatalf("receipt retained forbidden UI data: %s", forbidden)
		}
	}
	for _, name := range []string{"hidden_prompt_admission_action.go", "hidden_prompt_admission_action_windows.go"} {
		data, readErr := os.ReadFile(filepath.Join(".", name))
		if readErr != nil {
			t.Fatal(readErr)
		}
		text := string(data)
		for _, forbidden := range []string{"SendInput", "SetCursorPos", "SetForegroundWindow", "SwitchDesktop", "mouse_event", "keybd_event", "InvokePattern.Invoke", "ValuePattern.SetValue", "BM_CLICK", "WM_COMMAND"} {
			if strings.Contains(text, forbidden) {
				t.Fatalf("%s contains forbidden action %s", name, forbidden)
			}
		}
	}
}

func TestHiddenPromptS5WindowsScriptsSeparateForeachKeywords(t *testing.T) {
	data, err := os.ReadFile("hidden_prompt_admission_action_windows.go")
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(data), "in$") {
		t.Fatal("PowerShell foreach keyword is not separated from its collection")
	}
	text := string(data)
	if !strings.Contains(text, "if($x.Current.ControlType-eq[Windows.Automation.ControlType]::Button){O $false 'row_failed'") ||
		!strings.Contains(text, "PropertyCondition]::new([Windows.Automation.AutomationElement]::ControlTypeProperty,[Windows.Automation.ControlType]::Button)") {
		t.Fatal("PowerShell scripts do not bind unreadable-row failure to complete button enumeration")
	}
}
