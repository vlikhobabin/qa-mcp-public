package main

import (
	"fmt"
	"testing"
)

func TestVirtualKeyFunctionKeys(t *testing.T) {
	for number := 1; number <= 12; number++ {
		name := fmt.Sprintf("f%d", number)
		got, ok := virtualKey(name)
		want := uint16(0x70 + number - 1)
		if !ok || got != want {
			t.Fatalf("virtualKey(%q) = %#x, %v; want %#x, true", name, got, ok, want)
		}
	}
}

func TestVirtualKeyF5AndExistingAliases(t *testing.T) {
	tests := map[string]uint16{
		"f5":     0x74,
		"F5":     0x74,
		" f5 ":   0x74,
		"f4":     0x73,
		"enter":  0x0D,
		"escape": 0x1B,
		"insert": 0x2D,
		"left":   0x25,
		"a":      0x41,
		"7":      0x37,
	}
	for name, want := range tests {
		got, ok := virtualKey(name)
		if !ok || got != want {
			t.Fatalf("virtualKey(%q) = %#x, %v; want %#x, true", name, got, ok, want)
		}
	}
}

func TestVirtualKeyUnsupportedFunctionKeyFailsClosed(t *testing.T) {
	for _, name := range []string{"f0", "f13", "fn", "unknown"} {
		if got, ok := virtualKey(name); ok {
			t.Fatalf("virtualKey(%q) = %#x, true; want false", name, got)
		}
	}
}

func TestTargetMessageVirtualKeys(t *testing.T) {
	for _, name := range []string{"f5", "F5", "escape", "Esc"} {
		if _, ok, err := targetMessageVirtualKey(name); err != nil || !ok {
			t.Fatalf("targetMessageVirtualKey(%q) = ok %v err %v; want ok true", name, ok, err)
		}
	}
	for _, name := range []string{"tab", "ctrl+s", "enter"} {
		if _, ok, err := targetMessageVirtualKey(name); err != nil || ok {
			t.Fatalf("targetMessageVirtualKey(%q) = ok %v err %v; want ok false nil", name, ok, err)
		}
	}
	if _, _, err := targetMessageVirtualKey("unknown"); err == nil {
		t.Fatal("targetMessageVirtualKey(\"unknown\") returned nil error")
	}
}

func TestAllTargetMessageKeysRequiresSafeWholeSequence(t *testing.T) {
	ok, err := allTargetMessageKeys([]string{"F5", "Escape"})
	if err != nil || !ok {
		t.Fatalf("allTargetMessageKeys(F5, Escape) = %v, %v; want true nil", ok, err)
	}
	ok, err = allTargetMessageKeys([]string{"F5", "Tab"})
	if err != nil || ok {
		t.Fatalf("allTargetMessageKeys(F5, Tab) = %v, %v; want false nil", ok, err)
	}
	if _, err := allTargetMessageKeys([]string{"F5", "unknown"}); err == nil {
		t.Fatal("allTargetMessageKeys with unknown key returned nil error")
	}
}
