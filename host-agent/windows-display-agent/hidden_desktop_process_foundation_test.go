package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"strings"
	"testing"
)

func TestHiddenDesktopProcessFoundationIdentityIsOpaqueAndBounded(t *testing.T) {
	first, err := newHiddenDesktopProcessIdentity("run-one", "worker-token-one")
	if err != nil {
		t.Fatal(err)
	}
	second, err := newHiddenDesktopProcessIdentity("run-two", "worker-token-two")
	if err != nil {
		t.Fatal(err)
	}
	if first.Desktop == second.Desktop || first.RunIDHash == second.RunIDHash || first.WorkerTokenHash == second.WorkerTokenHash {
		t.Fatal("distinct bounded identities collapsed")
	}
	if !strings.HasPrefix(first.Desktop, `Winsta0\qa-mcp-`) || len(first.RunIDHash) != 64 || len(first.WorkerTokenHash) != 64 {
		t.Fatalf("invalid derived identity shape: %+v", first)
	}
	encoded, err := json.Marshal(first)
	if err != nil {
		t.Fatal(err)
	}
	for _, secret := range []string{"run-one", "worker-token-one"} {
		if strings.Contains(string(encoded), secret) {
			t.Fatalf("serialized identity retained raw value %q", secret)
		}
	}
	if err := validateHiddenDesktopProcessName(first.Desktop); err != nil {
		t.Fatalf("derived desktop rejected: %v", err)
	}
}

func TestHiddenDesktopProcessFoundationRejectsInvalidIdentityAndDesktop(t *testing.T) {
	oversized := strings.Repeat("x", 257)
	padded := strings.Repeat(" ", 256) + "x"
	unicodePadded := strings.Repeat("\u2003", 128) + "x"
	for _, values := range [][2]string{
		{"", "token"}, {"run", ""}, {oversized, "token"}, {"run", oversized},
		{padded, "token"}, {"run", unicodePadded},
		{" run", "token"}, {"run ", "token"}, {"\u2003run", "token"}, {"run\u2003", "token"},
		{"run", " token"}, {"run", "token "}, {"run", "\u2003token"}, {"run", "token\u2003"},
	} {
		if _, err := newHiddenDesktopProcessIdentity(values[0], values[1]); err == nil {
			t.Fatalf("identity accepted run=%d token=%d", len(values[0]), len(values[1]))
		}
	}
	for _, name := range []string{"", `Winsta0\Default`, `qa-mcp-deadbeef`, `Winsta0\qa-mcp-xyz`, `Winsta0\qa-mcp-0123456789abcdef0`} {
		if err := validateHiddenDesktopProcessName(name); err == nil {
			t.Fatalf("desktop name accepted: %q", name)
		}
	}
}

func TestHiddenDesktopProcessFoundationReplacesReservedEnvironment(t *testing.T) {
	environment, err := composeHiddenDesktopProcessEnvironment(
		[]string{"Path=C:\\Windows", "NORMAL=one", "qa_mcp_internal_hidden_stale=secret", "PATH=C:\\Tools"},
		[]string{"QA_MCP_INTERNAL_HIDDEN_RUN_HASH=run-hash", "QA_MCP_INTERNAL_HIDDEN_TOKEN_HASH=token-hash"},
	)
	if err != nil {
		t.Fatal(err)
	}
	want := []string{"NORMAL=one", "PATH=C:\\Tools", "QA_MCP_INTERNAL_HIDDEN_RUN_HASH=run-hash", "QA_MCP_INTERNAL_HIDDEN_TOKEN_HASH=token-hash"}
	if strings.Join(environment, "\n") != strings.Join(want, "\n") {
		t.Fatalf("environment = %#v, want %#v", environment, want)
	}
	for _, entry := range environment {
		if strings.Contains(strings.ToLower(entry), "stale") || strings.Contains(entry, "secret") {
			t.Fatalf("stale reserved environment survived: %q", entry)
		}
	}
}

func TestHiddenDesktopProcessFoundationRejectsMalformedEnvironment(t *testing.T) {
	cases := [][]string{
		nil,
		{"MISSING_SEPARATOR"},
		{"=missing-name"},
		{"PUBLIC_KEY=value"},
		{"QA_MCP_INTERNAL_HIDDEN_DUP=one", "qa_mcp_internal_hidden_dup=two"},
		{"QA_MCP_INTERNAL_HIDDEN_BIG=" + strings.Repeat("x", 32768)},
	}
	for _, additions := range cases {
		if _, err := composeHiddenDesktopProcessEnvironment(nil, additions); err == nil {
			t.Fatalf("malformed additions accepted: lengths=%v", environmentEntryLengths(additions))
		}
	}
}

func TestHiddenDesktopProcessFoundationIsDormantAndInputFree(t *testing.T) {
	directory := sourceDirectory(t)
	foundation := []string{"hidden_desktop_process_foundation.go", "hidden_desktop_process_foundation_windows.go"}
	forbidden := []string{"SendInput", "SetCursorPos", "SetForegroundWindow", "SwitchDesktop", "mouse_event", "keybd_event"}
	for _, name := range foundation {
		data, err := os.ReadFile(filepath.Join(directory, name))
		if err != nil {
			t.Fatal(err)
		}
		for _, symbol := range forbidden {
			if strings.Contains(string(data), symbol) {
				t.Fatalf("%s contains forbidden global-input symbol %s", name, symbol)
			}
		}
	}
	entries, err := os.ReadDir(directory)
	if err != nil {
		t.Fatal(err)
	}
	for _, entry := range entries {
		name := entry.Name()
		if entry.IsDir() || !strings.HasSuffix(name, ".go") || strings.HasSuffix(name, "_test.go") || name == foundation[0] || name == foundation[1] {
			continue
		}
		data, err := os.ReadFile(filepath.Join(directory, name))
		if err != nil {
			t.Fatal(err)
		}
		if name == "hidden_desktop_worker_lifecycle_windows.go" {
			if strings.Count(string(data), "createHiddenDesktopFoundation(") != 1 || strings.Count(string(data), "startHiddenDesktopFoundationProcess(") != 2 {
				t.Fatal("foundation is consumed outside the exact bounded S2 lifecycle")
			}
			continue
		}
		for _, symbol := range []string{"createHiddenDesktopFoundation(", "startHiddenDesktopFoundationProcess("} {
			if strings.Contains(string(data), symbol) {
				t.Fatalf("foundation is active from existing production file %s", name)
			}
		}
	}
}

func environmentEntryLengths(entries []string) []int {
	lengths := make([]int, len(entries))
	for index := range entries {
		lengths[index] = len(entries[index])
	}
	return lengths
}

func sourceDirectory(t *testing.T) string {
	t.Helper()
	directory, err := os.Getwd()
	if err != nil {
		t.Fatal(err)
	}
	return directory
}
