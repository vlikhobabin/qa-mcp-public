package main

import "testing"

// splitEnvBlock decodes a rendered Windows environment block back into its
// "KEY=VALUE" segments so tests can assert structure without depending on
// Windows syscalls.
func splitEnvBlock(t *testing.T, block []uint16) []string {
	t.Helper()
	if len(block) == 0 {
		return nil
	}
	if block[len(block)-1] != 0 {
		t.Fatalf("environment block is not NUL-terminated: %v", block)
	}
	var segments []string
	var current []uint16
	// The block is segments each ending in NUL, plus a final terminator NUL.
	for i, code := range block {
		if code == 0 {
			if len(current) == 0 {
				// Empty segment: only legal as the final block terminator.
				if i != len(block)-1 {
					t.Fatalf("unexpected empty segment at index %d: %v", i, block)
				}
				break
			}
			segments = append(segments, string(utf16Runes(current)))
			current = nil
			continue
		}
		current = append(current, code)
	}
	return segments
}

func utf16Runes(codes []uint16) []rune {
	out := make([]rune, 0, len(codes))
	for _, c := range codes {
		out = append(out, rune(c))
	}
	return out
}

func TestWindowsEnvironmentBlockEmpty(t *testing.T) {
	if block := windowsEnvironmentBlock(nil); block != nil {
		t.Fatalf("nil env should render nil block, got %v", block)
	}
	if block := windowsEnvironmentBlock([]string{}); block != nil {
		t.Fatalf("empty env should render nil block, got %v", block)
	}
	if block := windowsEnvironmentBlock([]string{"", ""}); block != nil {
		t.Fatalf("all-empty env should render nil block, got %v", block)
	}
}

// TestWindowsEnvironmentBlockMultiEntry is the regression for the launch-time
// panic: syscall.StringToUTF16 aborts on any interior NUL, so a NUL-delimited
// block could never be rendered by joining and encoding in one shot. A
// multi-entry env must yield each segment intact plus the terminator, and it
// must not panic.
func TestWindowsEnvironmentBlockMultiEntry(t *testing.T) {
	env := []string{
		"USERPROFILE=C:\\Users\\User",
		"APPDATA=C:\\Users\\User\\AppData\\Roaming",
		"TEMP=C:\\Users\\User\\AppData\\Local\\Temp",
	}
	block := windowsEnvironmentBlock(env)
	if len(block) < 2 {
		t.Fatalf("multi-entry env produced too-short block: %v", block)
	}
	if block[len(block)-1] != 0 || block[len(block)-2] != 0 {
		t.Fatalf("block must end with a double NUL terminator, got tail %v", block[len(block)-2:])
	}
	got := splitEnvBlock(t, block)
	if len(got) != len(env) {
		t.Fatalf("segment count = %d, want %d (%v)", len(got), len(env), got)
	}
	for i := range env {
		if got[i] != env[i] {
			t.Fatalf("segment %d = %q, want %q", i, got[i], env[i])
		}
	}
}

func TestWindowsEnvironmentBlockSkipsEmptySegments(t *testing.T) {
	block := windowsEnvironmentBlock([]string{"A=1", "", "B=2"})
	got := splitEnvBlock(t, block)
	want := []string{"A=1", "B=2"}
	if len(got) != len(want) {
		t.Fatalf("segments = %v, want %v", got, want)
	}
	for i := range want {
		if got[i] != want[i] {
			t.Fatalf("segment %d = %q, want %q", i, got[i], want[i])
		}
	}
}

func TestWindowsEnvironmentBlockUnicode(t *testing.T) {
	// Cyrillic values (e.g. USERNAME=Админ) must survive UTF-16 encoding.
	block := windowsEnvironmentBlock([]string{"USERNAME=Админ"})
	got := splitEnvBlock(t, block)
	if len(got) != 1 || got[0] != "USERNAME=Админ" {
		t.Fatalf("unicode segment = %v, want [USERNAME=Админ]", got)
	}
}
