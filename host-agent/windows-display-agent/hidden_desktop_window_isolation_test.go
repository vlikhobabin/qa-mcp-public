package main

import (
	"encoding/json"
	"os"
	"strings"
	"testing"
)

func hiddenWindowFixture() ([]hiddenWindowIdentity, []hiddenWindowIdentity, string, string, func(uint32) bool) {
	hiddenHash, operatorHash := hiddenWindowHash(`Winsta0\qa-mcp-0123456789abcdef`), hiddenWindowHash(`Winsta0\Default`)
	hidden := []hiddenWindowIdentity{
		{HWND: 11, PID: 101, ClassName: "RootClass", OwnerHWND: 0, DesktopHash: hiddenHash},
		{HWND: 12, PID: 101, ClassName: "PopupClass", OwnerHWND: 11, DesktopHash: hiddenHash},
	}
	return hidden, nil, hiddenHash, operatorHash, func(pid uint32) bool { return pid == 101 }
}

func TestHiddenWindowIsolationExactSelection(t *testing.T) {
	hidden, operator, hiddenHash, operatorHash, member := hiddenWindowFixture()
	receipt, err := validateHiddenWindowIsolation(hidden, operator, hiddenHash, operatorHash, member)
	if err != nil || receipt.HiddenWindowCount != 2 || receipt.JobOwnedHiddenWindowCount != 2 || receipt.JobOwnedOperatorWindowCount != 0 || len(receipt.ClassHashes) != 2 {
		t.Fatalf("exact isolation rejected: %#v %v", receipt, err)
	}
	for _, expected := range []struct {
		class       string
		owner, hwnd uintptr
	}{{"RootClass", 0, 11}, {"popupclass", 11, 12}} {
		window, selectErr := admitExactHiddenWindow(hidden, hiddenHash, 101, expected.class, expected.owner, member)
		if selectErr != nil || window.HWND != expected.hwnd {
			t.Fatalf("exact window rejected: %#v %v", window, selectErr)
		}
	}
}

func TestHiddenWindowIsolationHostileSurfacesFailClosed(t *testing.T) {
	base, operator, hiddenHash, operatorHash, member := hiddenWindowFixture()
	cases := map[string]func(*[]hiddenWindowIdentity, *[]hiddenWindowIdentity, *string, *string){
		"missing":     func(hidden, _ *[]hiddenWindowIdentity, _, _ *string) { *hidden = (*hidden)[:1] },
		"duplicate":   func(hidden, _ *[]hiddenWindowIdentity, _, _ *string) { *hidden = append(*hidden, (*hidden)[1]) },
		"foreign pid": func(hidden, _ *[]hiddenWindowIdentity, _, _ *string) { (*hidden)[1].PID = 202 },
		"outside job": func(hidden, _ *[]hiddenWindowIdentity, _, _ *string) { (*hidden)[1].PID = 303 },
		"wrong class": func(hidden, _ *[]hiddenWindowIdentity, _, _ *string) { (*hidden)[1].ClassName = "Other" },
		"wrong owner": func(hidden, _ *[]hiddenWindowIdentity, _, _ *string) { (*hidden)[1].OwnerHWND = 99 },
		"wrong desktop": func(hidden, _ *[]hiddenWindowIdentity, _, _ *string) {
			(*hidden)[1].DesktopHash = strings.Repeat("f", 64)
		},
		"owned default": func(_ *[]hiddenWindowIdentity, operator *[]hiddenWindowIdentity, _, _ *string) {
			*operator = append(*operator, hiddenWindowIdentity{HWND: 21, PID: 101, ClassName: "Leak", DesktopHash: operatorHash})
		},
		"wrong inventory identity": func(_ *[]hiddenWindowIdentity, _ *[]hiddenWindowIdentity, hiddenHash, _ *string) {
			*hiddenHash = strings.Repeat("e", 64)
		},
	}
	for name, mutate := range cases {
		t.Run(name, func(t *testing.T) {
			hidden := append([]hiddenWindowIdentity(nil), base...)
			currentOperator := append([]hiddenWindowIdentity(nil), operator...)
			currentHiddenHash, currentOperatorHash := hiddenHash, operatorHash
			mutate(&hidden, &currentOperator, &currentHiddenHash, &currentOperatorHash)
			if name == "owned default" || name == "foreign pid" || name == "outside job" || name == "wrong inventory identity" {
				if _, err := validateHiddenWindowIsolation(hidden, currentOperator, currentHiddenHash, currentOperatorHash, member); err == nil {
					t.Fatal("hostile inventory admitted")
				}
				return
			}
			if _, err := admitExactHiddenWindow(hidden, currentHiddenHash, 101, "PopupClass", 11, member); err == nil {
				t.Fatal("hostile candidate admitted")
			}
		})
	}
}

func TestHiddenWindowIsolationInJobWrongPIDFailsClosed(t *testing.T) {
	hidden, _, hiddenHash, _, _ := hiddenWindowFixture()
	hidden[1].PID = 202
	inJob := func(pid uint32) bool { return pid == 101 || pid == 202 }
	if _, err := admitExactHiddenWindow(hidden, hiddenHash, 101, "PopupClass", 11, inJob); err == nil {
		t.Fatal("in-job wrong-PID candidate admitted")
	}
}

func TestHiddenWindowIsolationReceiptIsSanitized(t *testing.T) {
	hidden, operator, hiddenHash, operatorHash, member := hiddenWindowFixture()
	receipt, err := validateHiddenWindowIsolation(hidden, operator, hiddenHash, operatorHash, member)
	if err != nil {
		t.Fatal(err)
	}
	data, err := json.Marshal(receipt)
	if err != nil {
		t.Fatal(err)
	}
	text := string(data)
	for _, raw := range []string{"RootClass", "PopupClass", `Winsta0`, `qa-mcp-`, `Default`} {
		if strings.Contains(text, raw) {
			t.Fatalf("receipt retained raw identity %q", raw)
		}
	}
	if receipt.GlobalInputCalls != 0 || receipt.DesktopSwitchCalls != 0 {
		t.Fatal("read-only receipt reported action")
	}
	var values map[string]any
	if err := json.Unmarshal(data, &values); err != nil {
		t.Fatal(err)
	}
	for key, value := range values {
		switch typed := value.(type) {
		case float64, bool:
		case string:
			if !validHiddenWindowHash(typed) {
				t.Fatalf("receipt string %s is not a hash", key)
			}
		case []any:
			for _, item := range typed {
				hash, ok := item.(string)
				if !ok || !validHiddenWindowHash(hash) {
					t.Fatalf("receipt list %s contains a non-hash", key)
				}
			}
		default:
			t.Fatalf("receipt key %s has forbidden value type %T", key, value)
		}
	}
}

func TestHiddenWindowIsolationSourceIsDormantAndInputFree(t *testing.T) {
	for _, name := range []string{"hidden_desktop_window_isolation.go", "hidden_desktop_window_isolation_windows.go"} {
		data, err := os.ReadFile(name)
		if err != nil {
			t.Fatal(err)
		}
		for _, forbidden := range []string{"SendInput", "SetCursorPos", "SetForegroundWindow", "SwitchDesktop", "mouse_event", "keybd_event", "PostMessage", "SendMessage", "UIAutomation", "productionObserveDirectExecute"} {
			if strings.Contains(string(data), forbidden) {
				t.Fatalf("%s contains forbidden action %s", name, forbidden)
			}
		}
	}
	entries, err := os.ReadDir(".")
	if err != nil {
		t.Fatal(err)
	}
	for _, entry := range entries {
		name := entry.Name()
		if entry.IsDir() || !strings.HasSuffix(name, ".go") || strings.HasSuffix(name, "_test.go") || strings.HasPrefix(name, "hidden_desktop_window_isolation") {
			continue
		}
		data, err := os.ReadFile(name)
		if err != nil {
			t.Fatal(err)
		}
		if strings.Contains(string(data), "validateHiddenWindowIsolation(") || strings.Contains(string(data), "admitExactHiddenWindow(") || strings.Contains(string(data), "inventoryHiddenWindowIsolation(") {
			t.Fatalf("S3 primitive has non-test caller in %s", name)
		}
	}
}
