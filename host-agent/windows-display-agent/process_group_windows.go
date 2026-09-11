//go:build windows

package main

import (
	"os"
	"os/exec"
	"strconv"
	"syscall"
)

const createNewProcessGroup = 0x00000200

const ctrlBreakEvent = 1

var procGenerateConsoleCtrlEvent = syscall.NewLazyDLL("kernel32.dll").NewProc("GenerateConsoleCtrlEvent")

func configureProcessGroup(cmd *exec.Cmd) {
	if cmd == nil {
		return
	}
	if cmd.SysProcAttr == nil {
		cmd.SysProcAttr = &syscall.SysProcAttr{}
	}
	// Preserve launch attributes already applied by the caller. In particular,
	// console helpers call hideChildWindow before configuring their process
	// group; replacing SysProcAttr here silently dropped CREATE_NO_WINDOW and
	// made short-lived helpers flash a console in the interactive desktop.
	cmd.SysProcAttr.CreationFlags |= createNewProcessGroup
}

func killProcessGroup(process *os.Process) error {
	if process == nil {
		return nil
	}
	taskkill := exec.Command("taskkill", "/PID", strconv.Itoa(process.Pid), "/T", "/F")
	hideChildWindow(taskkill)
	err := taskkill.Run()
	if err == nil {
		return nil
	}
	return process.Kill()
}

func signalProcessGroup(process *os.Process) error {
	if process == nil {
		return nil
	}
	ok, _, err := procGenerateConsoleCtrlEvent.Call(ctrlBreakEvent, uintptr(process.Pid))
	if ok == 0 {
		return err
	}
	return nil
}
