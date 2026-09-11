//go:build windows

package main

import (
	"errors"
	"os"
	"strings"
	"syscall"
	"testing"
	"time"

	"golang.org/x/sys/windows"
)

var (
	foundationUser32             = windows.NewLazySystemDLL("user32.dll")
	foundationKernel32           = windows.NewLazySystemDLL("kernel32.dll")
	foundationGetThreadDesktop   = foundationUser32.NewProc("GetThreadDesktop")
	foundationGetCurrentThreadID = foundationKernel32.NewProc("GetCurrentThreadId")
	foundationEnumDesktopWindows = foundationUser32.NewProc("EnumDesktopWindows")
)

func TestHiddenDesktopProcessFoundationProcessContract(t *testing.T) {
	oldCreate, oldClose, oldTerminate := foundationCreateProcess, foundationCloseHandle, foundationTerminateProcess
	defer func() {
		foundationCreateProcess, foundationCloseHandle, foundationTerminateProcess = oldCreate, oldClose, oldTerminate
	}()
	var flags uint32
	var inherited bool
	var closed []windows.Handle
	var terminated windows.Handle
	foundationCreateProcess = func(_ *uint16, _ *uint16, _ *windows.SecurityAttributes, _ *windows.SecurityAttributes, inherit bool, creationFlags uint32, _ *uint16, _ *uint16, startup *windows.StartupInfo, process *windows.ProcessInformation) error {
		flags, inherited = creationFlags, inherit
		if windows.UTF16PtrToString(startup.Desktop) != `Winsta0\qa-mcp-0123456789abcdef` {
			return errors.New("wrong desktop")
		}
		process.Process, process.Thread = 101, 202
		return nil
	}
	closeFailure := true
	foundationCloseHandle = func(handle windows.Handle) error {
		closed = append(closed, handle)
		if handle == 202 && closeFailure {
			closeFailure = false
			return errors.New("injected thread close failure")
		}
		return nil
	}
	foundationTerminateProcess = func(handle windows.Handle, _ uint32) error { terminated = handle; return nil }
	executable, err := os.Executable()
	if err != nil {
		t.Fatal(err)
	}
	process, err := startHiddenDesktopFoundationProcess(executable, nil, []string{"NORMAL=one"}, `Winsta0\qa-mcp-0123456789abcdef`)
	if err == nil || process.Process != 0 || process.Thread != 0 {
		t.Fatalf("close failure result = %+v, %v", process, err)
	}
	if inherited || flags != windows.CREATE_UNICODE_ENVIRONMENT|windows.CREATE_NO_WINDOW {
		t.Fatalf("creation inherit=%v flags=%#x", inherited, flags)
	}
	if terminated != 101 || len(closed) != 3 || closed[0] != 202 || closed[1] != 202 || closed[2] != 101 {
		t.Fatalf("cleanup terminated=%d closed=%v", terminated, closed)
	}
}

func TestHiddenDesktopProcessFoundationCleanupClosesHandlesWhenTerminateFails(t *testing.T) {
	oldClose, oldTerminate := foundationCloseHandle, foundationTerminateProcess
	defer func() {
		foundationCloseHandle, foundationTerminateProcess = oldClose, oldTerminate
	}()
	terminateFailure := errors.New("injected terminate failure")
	cause := errors.New("injected creation cleanup cause")
	var closed []windows.Handle
	foundationTerminateProcess = func(handle windows.Handle, _ uint32) error {
		if handle != 101 {
			t.Fatalf("terminate handle = %d", handle)
		}
		return terminateFailure
	}
	foundationCloseHandle = func(handle windows.Handle) error {
		closed = append(closed, handle)
		return nil
	}
	process, err := cleanupHiddenDesktopFoundationProcess(windows.ProcessInformation{Process: 101, Thread: 202}, cause)
	if !errors.Is(err, cause) || !errors.Is(err, terminateFailure) {
		t.Fatalf("cleanup error = %v", err)
	}
	if process.Process != 0 || process.Thread != 0 {
		t.Fatalf("successfully closed handles retained: %+v", process)
	}
	if len(closed) != 2 || closed[0] != 202 || closed[1] != 101 {
		t.Fatalf("close attempts = %v", closed)
	}
}

func TestHiddenDesktopProcessFoundationNativeLifecycle(t *testing.T) {
	identity, err := newHiddenDesktopProcessIdentity("native-foundation-run", "native-foundation-token")
	if err != nil {
		t.Fatal(err)
	}
	desktop, err := createHiddenDesktopFoundation(identity)
	if err != nil {
		t.Fatal(err)
	}
	defer func() {
		if err := desktop.Close(); err != nil {
			t.Errorf("close desktop: %v", err)
		}
	}()
	executable, err := os.Executable()
	if err != nil {
		t.Fatal(err)
	}
	environment, err := composeHiddenDesktopProcessEnvironment(
		append(os.Environ(), "qa_mcp_internal_hidden_stale=forbidden"),
		[]string{"QA_MCP_INTERNAL_HIDDEN_FOUNDATION_CHILD=1", "QA_MCP_INTERNAL_HIDDEN_DESKTOP=" + identity.Desktop},
	)
	if err != nil {
		t.Fatal(err)
	}
	process, err := startHiddenDesktopFoundationProcess(
		executable,
		[]string{"-test.run=^TestHiddenDesktopProcessFoundationNativeChild$", "-test.count=1"},
		environment,
		identity.Desktop,
	)
	if err != nil {
		t.Fatal(err)
	}
	defer windows.CloseHandle(process.Process)
	if wait, err := windows.WaitForSingleObject(process.Process, 20_000); err != nil || wait != windows.WAIT_OBJECT_0 {
		windows.TerminateProcess(process.Process, 125)
		t.Fatalf("child wait = %d, %v", wait, err)
	}
	var exitCode uint32
	if err := windows.GetExitCodeProcess(process.Process, &exitCode); err != nil || exitCode != 0 {
		t.Fatalf("child exit = %d, %v", exitCode, err)
	}
	console := os.Getenv("COMSPEC")
	if console == "" {
		console = `C:\Windows\System32\cmd.exe`
	}
	consoleProcess, err := startHiddenDesktopFoundationProcess(console, []string{"/D", "/C", "ping -n 4 127.0.0.1 >NUL"}, environment, identity.Desktop)
	if err != nil {
		t.Fatal(err)
	}
	defer windows.CloseHandle(consoleProcess.Process)
	time.Sleep(500 * time.Millisecond)
	if wait, err := windows.WaitForSingleObject(consoleProcess.Process, 0); err != nil || wait != uint32(windows.WAIT_TIMEOUT) {
		t.Fatalf("console child did not remain alive: %d, %v", wait, err)
	}
	if count, err := hiddenDesktopFoundationWindowCount(desktop.handle); err != nil || count != 0 {
		t.Fatalf("windowless child windows = %d, %v", count, err)
	}
	if err := windows.TerminateProcess(consoleProcess.Process, 125); err != nil {
		t.Fatal(err)
	}
}

func TestHiddenDesktopProcessFoundationNativeChild(t *testing.T) {
	if os.Getenv("QA_MCP_INTERNAL_HIDDEN_FOUNDATION_CHILD") != "1" {
		t.Skip("foundation child only")
	}
	expected := os.Getenv("QA_MCP_INTERNAL_HIDDEN_DESKTOP")
	if expected == "" || !strings.HasPrefix(expected, `Winsta0\qa-mcp-`) {
		t.Fatal("bounded desktop identity is absent")
	}
	if _, present := os.LookupEnv("QA_MCP_INTERNAL_HIDDEN_STALE"); present {
		t.Fatal("stale reserved environment survived")
	}
	threadID, _, _ := foundationGetCurrentThreadID.Call()
	handle, _, _ := foundationGetThreadDesktop.Call(threadID)
	name, ok := desktopObjectName(handle)
	if !ok || !strings.EqualFold(name, expected[strings.LastIndex(expected, `\`)+1:]) {
		t.Fatalf("child desktop mismatch")
	}
}

func hiddenDesktopFoundationWindowCount(desktop windows.Handle) (int, error) {
	count := 0
	callback := syscall.NewCallback(func(_ uintptr, _ uintptr) uintptr { count++; return 1 })
	ok, _, err := foundationEnumDesktopWindows.Call(uintptr(desktop), callback, 0)
	if ok == 0 && err != windows.ERROR_SUCCESS {
		return 0, err
	}
	return count, nil
}
