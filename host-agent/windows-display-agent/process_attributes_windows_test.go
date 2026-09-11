//go:build windows

package main

import (
	"os/exec"
	"testing"
)

func TestConfigureProcessGroupPreservesNoWindow(t *testing.T) {
	cmd := exec.Command("cmd.exe", "/c", "exit", "0")
	hideChildWindow(cmd)
	configureProcessGroup(cmd)

	want := uint32(createNoWindow | createNewProcessGroup)
	if got := cmd.SysProcAttr.CreationFlags; got&want != want {
		t.Fatalf("creation flags = %#x, want both %#x", got, want)
	}
}

func TestHideChildConsoleKeepsProcessGroupAndUsesHiddenStartup(t *testing.T) {
	cmd := exec.Command("cmd.exe", "/c", "exit", "0")
	configureProcessGroup(cmd)
	hideChildConsole(cmd)

	if !cmd.SysProcAttr.HideWindow {
		t.Fatal("console child startup is not hidden")
	}
	if got := cmd.SysProcAttr.CreationFlags; got&createNewProcessGroup == 0 {
		t.Fatalf("process-group flag was lost: %#x", got)
	}
	if got := cmd.SysProcAttr.CreationFlags; got&createNoWindow != 0 {
		t.Fatalf("console-preserving child unexpectedly uses CREATE_NO_WINDOW: %#x", got)
	}
}
