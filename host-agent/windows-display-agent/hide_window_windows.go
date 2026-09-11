//go:build windows

package main

import (
	"os/exec"
	"syscall"
)

// createNoWindow (CREATE_NO_WINDOW) suppresses the console window Windows would otherwise
// allocate for a console-subsystem child process. It has no effect on GUI applications
// (for example the 1C client), so applying it to the host-agent's console helpers keeps
// the windowless host-agent from flashing a console on each COM/UIA/CLI operation.
const createNoWindow = 0x08000000

// hideChildWindow makes cmd run without a console window. It preserves any CreationFlags
// already set on cmd (e.g. a process-group flag) by OR-ing the flag in, and allocates a
// SysProcAttr when one is not present.
func hideChildWindow(cmd *exec.Cmd) {
	if cmd == nil {
		return
	}
	if cmd.SysProcAttr == nil {
		cmd.SysProcAttr = &syscall.SysProcAttr{}
	}
	cmd.SysProcAttr.CreationFlags |= createNoWindow
}

// hideChildConsole preserves a console for helpers that require one while
// asking Windows not to show its initial window. The TestClient broker cannot complete its
// workstation warmup under CREATE_NO_WINDOW, but it must not expose a console
// or steal focus from the interactive user either.
func hideChildConsole(cmd *exec.Cmd) {
	if cmd == nil {
		return
	}
	if cmd.SysProcAttr == nil {
		cmd.SysProcAttr = &syscall.SysProcAttr{}
	}
	cmd.SysProcAttr.HideWindow = true
}
