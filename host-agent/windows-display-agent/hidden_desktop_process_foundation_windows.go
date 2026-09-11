//go:build windows

package main

import (
	"errors"
	"os"
	"path/filepath"
	"sync"
	"unsafe"

	"golang.org/x/sys/windows"
)

const (
	foundationDesktopCreateWindow = 0x0002
	foundationDesktopEnumerate    = 0x0040
	foundationDesktopReadObjects  = 0x0001
	foundationDesktopWriteObjects = 0x0080
)

var (
	hiddenDesktopCreate        = user32.NewProc("CreateDesktopW")
	hiddenDesktopClose         = user32.NewProc("CloseDesktop")
	foundationCreateProcess    = windows.CreateProcess
	foundationCloseHandle      = windows.CloseHandle
	foundationTerminateProcess = windows.TerminateProcess
)

type hiddenDesktopFoundation struct {
	Name   string
	handle windows.Handle
	mu     sync.Mutex
}

func createHiddenDesktopFoundation(identity hiddenDesktopProcessIdentity) (*hiddenDesktopFoundation, error) {
	if err := validateHiddenDesktopProcessIdentity(identity); err != nil {
		return nil, err
	}
	leaf := identity.Desktop[len(`Winsta0\`):]
	pointer, err := windows.UTF16PtrFromString(leaf)
	if err != nil {
		return nil, err
	}
	handle, _, callErr := hiddenDesktopCreate.Call(
		uintptr(unsafe.Pointer(pointer)), 0, 0, 0,
		foundationDesktopCreateWindow|foundationDesktopEnumerate|foundationDesktopReadObjects|foundationDesktopWriteObjects, 0,
	)
	if handle == 0 {
		return nil, callErr
	}
	return &hiddenDesktopFoundation{Name: identity.Desktop, handle: windows.Handle(handle)}, nil
}

func (desktop *hiddenDesktopFoundation) Close() error {
	if desktop == nil {
		return nil
	}
	desktop.mu.Lock()
	defer desktop.mu.Unlock()
	if desktop.handle == 0 {
		return nil
	}
	ok, _, callErr := hiddenDesktopClose.Call(uintptr(desktop.handle))
	if ok == 0 {
		return callErr
	}
	desktop.handle = 0
	return nil
}

func startHiddenDesktopFoundationProcess(executable string, args, environment []string, desktopName string, flags ...uint32) (windows.ProcessInformation, error) {
	if !filepath.IsAbs(executable) || validateHiddenDesktopProcessName(desktopName) != nil || validateHiddenDesktopProcessEnvironment(environment) != nil {
		return windows.ProcessInformation{}, errors.New("hidden desktop process input is invalid")
	}
	if info, err := os.Stat(executable); err != nil || info.IsDir() {
		return windows.ProcessInformation{}, errors.New("hidden desktop executable is unavailable")
	}
	application, err := windows.UTF16PtrFromString(executable)
	if err != nil {
		return windows.ProcessInformation{}, err
	}
	commandLine, err := windows.UTF16PtrFromString(windowsCommandLine(executable, args))
	if err != nil {
		return windows.ProcessInformation{}, err
	}
	desktop, err := windows.UTF16PtrFromString(desktopName)
	if err != nil {
		return windows.ProcessInformation{}, err
	}
	directory, err := windows.UTF16PtrFromString(filepath.Dir(executable))
	if err != nil {
		return windows.ProcessInformation{}, err
	}
	block := windowsEnvironmentBlock(environment)
	var blockPointer *uint16
	if len(block) != 0 {
		blockPointer = &block[0]
	}
	startup := &windows.StartupInfo{Cb: uint32(unsafe.Sizeof(windows.StartupInfo{})), Desktop: desktop}
	var process windows.ProcessInformation
	creationFlags := map[bool]uint32{false: windows.CREATE_NO_WINDOW, true: windows.CREATE_SUSPENDED}[len(flags) == 1 && flags[0] == windows.CREATE_SUSPENDED]
	if err := foundationCreateProcess(
		application, commandLine, nil, nil, false,
		windows.CREATE_UNICODE_ENVIRONMENT|creationFlags,
		blockPointer, directory, startup, &process,
	); err != nil {
		return windows.ProcessInformation{}, err
	}
	if creationFlags == windows.CREATE_SUSPENDED {
		return process, nil
	}
	if err := foundationCloseHandle(process.Thread); err != nil {
		return cleanupHiddenDesktopFoundationProcess(process, err)
	}
	process.Thread = 0
	return process, nil
}

func cleanupHiddenDesktopFoundationProcess(process windows.ProcessInformation, cause error) (windows.ProcessInformation, error) {
	terminateErr := foundationTerminateProcess(process.Process, 125)
	threadErr, processErr := foundationCloseHandle(process.Thread), foundationCloseHandle(process.Process)
	if threadErr == nil {
		process.Thread = 0
	}
	if processErr == nil {
		process.Process = 0
	}
	return process, errors.Join(cause, terminateErr, threadErr, processErr)
}
