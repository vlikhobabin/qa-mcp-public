//go:build windows

package main

import (
	"bufio"
	"bytes"
	"context"
	"crypto/rand"
	"crypto/subtle"
	"encoding/base64"
	"fmt"
	"net"
	"net/http"
	"os"
	"os/exec"
	"strings"
	"syscall"
	"time"
	"unsafe"
)

const (
	infiniteWait       = 0xFFFFFFFF
	waitFailed         = 0xFFFFFFFF
	waitTimeout        = 0x00000102
	wtsNoActiveSession = 0xFFFFFFFF
	processSynchronize = 0x00100000
	processTerminate   = 0x0001
)

var (
	testClientKernel32             = syscall.NewLazyDLL("kernel32.dll")
	procWaitForSingleObject        = testClientKernel32.NewProc("WaitForSingleObject")
	procTerminateProcess           = testClientKernel32.NewProc("TerminateProcess")
	procProcessIDToSessionID       = testClientKernel32.NewProc("ProcessIdToSessionId")
	procWTSGetActiveConsoleSession = testClientKernel32.NewProc("WTSGetActiveConsoleSessionId")
)

func startTestClientProcess(
	ctx context.Context,
	executable string,
	args []string,
	env []string,
	port int,
	ownerWaitTimeout time.Duration,
	launchContext testClientLaunchContext,
) (*launchedTestClientProcess, testClientLaunchContext, *testClientProcessStartError) {
	launchContext.Method = interactiveTaskShellBrokerMethod
	activeSession, sessionErr := verifiedInteractiveHostAgentSession()
	if sessionErr != nil {
		return nil, launchContext, startError("testclient-interactive-session-unavailable", sessionErr.Error())
	}
	launchContext.SessionID = &activeSession
	select {
	case <-ctx.Done():
		return nil, launchContext, startError("testclient-launch-canceled", "TestClient launch was canceled before process creation")
	default:
	}

	brokerInput, err := testClientShellBrokerInput(executable, args, port)
	if err != nil {
		return nil, launchContext, startError("testclient-launch-start-failed", "TestClient shell-broker request could not be encoded")
	}
	listener, err := net.Listen("tcp4", "127.0.0.1:0")
	if err != nil {
		return nil, launchContext, startError("testclient-launch-start-failed", "interactive task rendezvous listener failed: "+err.Error())
	}
	defer listener.Close()
	rendezvousPort := listener.Addr().(*net.TCPAddr).Port
	nonce, err := randomTaskBrokerValue(32)
	if err != nil {
		return nil, launchContext, startError("testclient-launch-start-failed", "interactive task rendezvous token generation failed")
	}
	taskSuffix, err := randomTaskBrokerValue(12)
	if err != nil {
		return nil, launchContext, startError("testclient-launch-start-failed", "interactive task identifier generation failed")
	}
	taskName := "qa-mcp-testclient-launch-" + taskSuffix
	actionArgument := testClientTaskBrokerActionArgument(rendezvousPort, nonce)
	brokerExecutable, err := os.Executable()
	if err != nil {
		return nil, launchContext, startError("testclient-launch-start-failed", "native TestClient broker executable could not be resolved")
	}
	registrationInput, err := testClientTaskRegistrationInput(taskName, brokerExecutable, actionArgument)
	if err != nil {
		return nil, launchContext, startError("testclient-launch-start-failed", "interactive task registration request could not be encoded")
	}
	registrationExecutable, registrationArgs := testClientTaskRegistrationCommand()
	registration := exec.CommandContext(ctx, registrationExecutable, registrationArgs...)
	registration.Env = env
	registration.Stdin = bytes.NewReader(registrationInput)
	var registrationError bytes.Buffer
	registration.Stderr = &registrationError
	hideChildWindow(registration)
	configureProcessGroup(registration)
	if err := registration.Start(); err != nil {
		return nil, launchContext, startError("testclient-launch-start-failed", "interactive task registration failed: "+err.Error())
	}
	taskCleanup := newTestClientTaskCleanupGuard(taskName, env, unregisterTestClientLaunchTask)
	defer taskCleanup.Fallback()
	registrationDone := make(chan error, 1)
	go func() { registrationDone <- registration.Wait() }()

	brokerPID, brokerErr := acceptTaskBrokerResult(listener, nonce, brokerInput)
	var registrationErr error
	var acknowledgedProcess syscall.Handle
	var acknowledgedLease *testClientAcknowledgedProcessLease
	if brokerErr == nil && brokerPID != 0 {
		var retentionErr *testClientProcessStartError
		acknowledgedLease, retentionErr = retainTestClientAcknowledgedProcessLease(
			brokerPID,
			func(pid uint32) (*testClientAcknowledgedProcessLease, *testClientProcessStartError) {
				lease, process, startErr := openAcknowledgedTestClientProcessLease(pid, activeSession)
				acknowledgedProcess = process
				return lease, startErr
			},
			func() *testClientProcessStartError {
				registrationErr = <-registrationDone
				if cleanupErr := taskCleanup.Cleanup(); cleanupErr != nil {
					return startError("testclient-launch-cleanup-failed", cleanupErr.Error())
				}
				if registrationErr != nil {
					detail := strings.TrimSpace(registrationError.String())
					if detail == "" {
						detail = registrationErr.Error()
					}
					return startError("testclient-launch-start-failed", "interactive task registration failed: "+detail)
				}
				return nil
			},
		)
		if retentionErr != nil {
			return nil, launchContext, retentionErr
		}
	} else {
		registrationErr = <-registrationDone
		if cleanupErr := taskCleanup.Cleanup(); cleanupErr != nil {
			return nil, launchContext, startError("testclient-launch-cleanup-failed", cleanupErr.Error())
		}
	}
	if brokerErr != nil {
		detail := brokerErr.Error()
		if registrationErr != nil {
			registrationDetail := strings.TrimSpace(registrationError.String())
			if registrationDetail == "" {
				registrationDetail = registrationErr.Error()
			}
			detail += "; interactive task result: " + registrationDetail
		}
		return nil, launchContext, startError("testclient-launch-start-failed", detail)
	}
	if registrationErr != nil {
		detail := strings.TrimSpace(registrationError.String())
		if detail == "" {
			detail = registrationErr.Error()
		}
		return nil, launchContext, startError("testclient-launch-start-failed", "interactive task registration failed: "+detail)
	}
	pid := uint32(0)
	var process syscall.Handle
	if brokerPID == 0 {
		var listenerErr error
		pid, listenerErr = waitForTestClientListenerPID(ctx, port, ownerWaitTimeout)
		if listenerErr != nil {
			return nil, launchContext, startError("testclient-launch-start-failed", listenerErr.Error())
		}
	} else {
		resolution := resolveTestClientListenerOwner(acknowledgedLease, func() (uint32, error) {
			return waitForTestClientListenerPID(ctx, port, ownerWaitTimeout)
		})
		switch resolution.Outcome {
		case testClientBrokerOutcomeListenerOwner:
			pid = resolution.PID
			if pid == brokerPID {
				process = acknowledgedProcess
			} else {
				acknowledgedLease.Close()
			}
		case testClientBrokerOutcomeExitedEarly:
			acknowledgedLease.Close()
			return nil, launchContext, startErrorWithProcess(
				"testclient-exited-early",
				"acknowledged TestClient process exited before TPort ownership appeared",
				resolution.PID,
				false,
				"exited_early",
			)
		case testClientBrokerOutcomeListenerUnavailable:
			acknowledgedLease.Close()
			return nil, launchContext, startErrorWithProcess(
				"testclient-not-listening",
				"acknowledged TestClient process did not expose the requested TPort and its retained process handle was terminated",
				resolution.PID,
				false,
				"not_listening",
			)
		case testClientBrokerOutcomeCleanupFailed:
			alive := acknowledgedLease.Alive()
			acknowledgedLease.Close()
			return nil, launchContext, startErrorWithProcess(
				"testclient-launch-cleanup-failed",
				resolution.CleanupError.Error(),
				resolution.PID,
				alive,
				"cleanup_failed",
			)
		default:
			acknowledgedLease.Close()
			return nil, launchContext, startError("testclient-launch-start-failed", "TestClient listener ownership could not be resolved")
		}
	}
	if process == 0 {
		selectedProcess, openErr := syscall.OpenProcess(
			processSynchronize|processQueryLimitedInformation|processTerminate,
			false,
			pid,
		)
		if openErr != nil {
			selectedAlive := testClientProcessAlive(int(pid))
			if !selectedAlive {
				return nil, launchContext, startErrorWithProcess(
					"testclient-exited-early",
					"TestClient listener owner exited before its lifecycle handle could be opened",
					pid,
					false,
					"exited_early",
				)
			}
			return nil, launchContext, startErrorWithProcess(
				"testclient-pid-handoff-failed",
				"TestClient listener-owner process handle failed: "+windowsCallError(openErr),
				pid,
				true,
				"pid_handoff_failed",
			)
		}
		process = selectedProcess
		childSession, childSessionOK := processSessionID(pid)
		if !childSessionOK || childSession != activeSession {
			_, _, _ = procTerminateProcess.Call(uintptr(process), 1)
			syscall.CloseHandle(process)
			return nil, launchContext, startError("testclient-interactive-session-unavailable", "TestClient listener-owner process did not inherit the verified active console session")
		}
	}
	done := make(chan struct{})
	go waitForWindowsProcess(process, done)
	return &launchedTestClientProcess{
		PID:  int(pid),
		Done: done,
		Terminate: func() error {
			ok, _, terminateErr := procTerminateProcess.Call(uintptr(process), 1)
			if ok == 0 && !testClientProcessDone(done) {
				return fmt.Errorf("TerminateProcess failed: %s", windowsCallError(terminateErr))
			}
			return nil
		},
	}, launchContext, nil
}

func openAcknowledgedTestClientProcessLease(
	pid uint32,
	activeSession uint32,
) (*testClientAcknowledgedProcessLease, syscall.Handle, *testClientProcessStartError) {
	process, openErr := syscall.OpenProcess(
		processSynchronize|processQueryLimitedInformation|processTerminate,
		false,
		pid,
	)
	if openErr != nil {
		acknowledgedAlive := testClientProcessAlive(int(pid))
		classification := classifyTestClientBrokerProcess(testClientBrokerProcessObservation{
			AcknowledgedPID:   pid,
			AcknowledgedAlive: acknowledgedAlive,
			HandleError:       openErr,
		})
		if classification.Outcome == testClientBrokerOutcomeExitedEarly {
			return nil, 0, startErrorWithProcess(
				"testclient-exited-early",
				"acknowledged TestClient process exited before its lifecycle handle could be retained",
				pid,
				false,
				"exited_early",
			)
		}
		return nil, 0, startErrorWithProcess(
			"testclient-pid-handoff-failed",
			"acknowledged TestClient process handle could not be retained: "+windowsCallError(openErr),
			pid,
			acknowledgedAlive,
			"pid_handoff_failed",
		)
	}
	if !testClientProcessHandleAlive(process) {
		syscall.CloseHandle(process)
		return nil, 0, startErrorWithProcess(
			"testclient-exited-early",
			"acknowledged TestClient process exited before TPort ownership appeared",
			pid,
			false,
			"exited_early",
		)
	}
	childSession, childSessionOK := processSessionID(pid)
	if !childSessionOK || childSession != activeSession {
		_, _, _ = procTerminateProcess.Call(uintptr(process), 1)
		_, _, _ = procWaitForSingleObject.Call(uintptr(process), uintptr(5_000))
		syscall.CloseHandle(process)
		return nil, 0, startError(
			"testclient-interactive-session-unavailable",
			"acknowledged TestClient process did not inherit the verified active console session",
		)
	}
	closed := false
	lease := &testClientAcknowledgedProcessLease{
		PID:   pid,
		Alive: func() bool { return !closed && testClientProcessHandleAlive(process) },
		Terminate: func() error {
			if closed {
				return fmt.Errorf("acknowledged TestClient process handle is already closed")
			}
			return terminateRetainedTestClientProcess(process)
		},
		Close: func() {
			if !closed {
				syscall.CloseHandle(process)
				closed = true
			}
		},
	}
	return lease, process, nil
}

func terminateRetainedTestClientProcess(process syscall.Handle) error {
	ok, _, terminateErr := procTerminateProcess.Call(uintptr(process), 1)
	if ok == 0 && testClientProcessHandleAlive(process) {
		return fmt.Errorf("exact acknowledged TestClient cleanup failed: %s", windowsCallError(terminateErr))
	}
	_, _, _ = procWaitForSingleObject.Call(uintptr(process), uintptr(5_000))
	if testClientProcessHandleAlive(process) {
		return fmt.Errorf("exact acknowledged TestClient remained alive after listener-timeout cleanup")
	}
	return nil
}

func testClientProcessHandleAlive(process syscall.Handle) bool {
	wait, _, _ := procWaitForSingleObject.Call(uintptr(process), 0)
	return uint32(wait) == waitTimeout
}

func unregisterTestClientLaunchTask(taskName string, env []string) error {
	input, err := testClientTaskUnregisterInput(taskName)
	if err != nil {
		return fmt.Errorf("interactive task cleanup request could not be encoded")
	}
	cleanupContext, cancel := newTestClientTaskCleanupContext()
	defer cancel()
	executable, args := testClientTaskUnregisterCommand()
	command := exec.CommandContext(cleanupContext, executable, args...)
	command.Env = env
	command.Stdin = bytes.NewReader(input)
	hideChildWindow(command)
	configureProcessGroup(command)
	output, err := command.CombinedOutput()
	if err == nil {
		return nil
	}
	detail := strings.TrimSpace(string(output))
	if detail == "" {
		detail = err.Error()
	}
	return fmt.Errorf("interactive task exact-name cleanup failed: %s", detail)
}

func randomTaskBrokerValue(size int) (string, error) {
	buffer := make([]byte, size)
	if _, err := rand.Read(buffer); err != nil {
		return "", err
	}
	return base64.RawURLEncoding.EncodeToString(buffer), nil
}

func acceptTaskBrokerResult(listener net.Listener, nonce string, payload []byte) (uint32, error) {
	if tcpListener, ok := listener.(*net.TCPListener); ok {
		_ = tcpListener.SetDeadline(time.Now().Add(30 * time.Second))
	}
	connection, err := listener.Accept()
	if err != nil {
		return 0, fmt.Errorf("interactive task shell broker did not connect: %w", err)
	}
	defer connection.Close()
	_ = connection.SetDeadline(time.Now().Add(15 * time.Second))
	reader := bufio.NewReaderSize(connection, 1<<20)
	provided, err := reader.ReadString('\n')
	if err != nil {
		return 0, fmt.Errorf("interactive task shell broker authentication failed")
	}
	provided = strings.TrimSpace(provided)
	if subtle.ConstantTimeCompare([]byte(provided), []byte(nonce)) != 1 {
		return 0, fmt.Errorf("interactive task shell broker authentication failed")
	}
	encodedPayload := base64.StdEncoding.EncodeToString(payload)
	if _, err := fmt.Fprintf(connection, "%s\n", encodedPayload); err != nil {
		return 0, fmt.Errorf("interactive task shell broker request failed: %w", err)
	}
	acknowledgement, err := reader.ReadString('\n')
	if err != nil {
		return 0, fmt.Errorf("interactive task shell broker did not acknowledge shell launch")
	}
	if detail, failed := parseTaskBrokerFailure(acknowledgement); failed {
		return 0, fmt.Errorf("interactive task shell broker failed before process acknowledgement: %s", detail)
	}
	pid, ok := parseTaskBrokerAcknowledgement(acknowledgement)
	if !ok {
		return 0, fmt.Errorf("interactive task shell broker returned an invalid acknowledgement")
	}
	return pid, nil
}

func waitForTestClientListenerPID(ctx context.Context, port int, timeout time.Duration) (uint32, error) {
	if !validTCPPort(port) {
		return 0, fmt.Errorf("interactive task shell broker received an invalid TestClient port")
	}
	deadline := time.NewTimer(timeout)
	defer deadline.Stop()
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()
	for {
		if pid, ok := pidListeningOnPort(uint16(port)); ok && pid != 0 {
			return pid, nil
		}
		select {
		case <-ctx.Done():
			return 0, fmt.Errorf("interactive task shell broker launch was canceled before TPort ownership appeared")
		case <-deadline.C:
			return 0, fmt.Errorf("interactive task shell broker did not expose the requested TPort before timeout")
		case <-ticker.C:
		}
	}
}

func verifiedInteractiveHostAgentSession() (uint32, error) {
	activeSession, _, _ := procWTSGetActiveConsoleSession.Call()
	if uint32(activeSession) == wtsNoActiveSession {
		return 0, fmt.Errorf("no active console session is available")
	}
	hostSession, ok := processSessionID(uint32(os.Getpid()))
	if !ok {
		return 0, fmt.Errorf("host-agent session could not be resolved")
	}
	if hostSession != uint32(activeSession) {
		return 0, fmt.Errorf("host-agent is not running in the active console session")
	}
	return hostSession, nil
}

func processSessionID(pid uint32) (uint32, bool) {
	var sessionID uint32
	ok, _, _ := procProcessIDToSessionID.Call(uintptr(pid), uintptr(unsafe.Pointer(&sessionID)))
	return sessionID, ok != 0
}

func waitForWindowsProcess(process syscall.Handle, done chan<- struct{}) {
	defer syscall.CloseHandle(process)
	defer close(done)
	wait, _, _ := procWaitForSingleObject.Call(uintptr(process), uintptr(infiniteWait))
	if uint32(wait) == waitFailed {
		return
	}
	var exitCode uint32
	ok, _, _ := procGetExitCodeProcess.Call(uintptr(process), uintptr(unsafe.Pointer(&exitCode)))
	if ok == 0 {
		return
	}
	_ = exitCode
}

func startError(code string, detail string) *testClientProcessStartError {
	return &testClientProcessStartError{Status: http.StatusBadGateway, Code: code, Detail: detail}
}

func startErrorWithProcess(code string, detail string, pid uint32, alive bool, readiness string) *testClientProcessStartError {
	processPID := int(pid)
	return &testClientProcessStartError{
		Status:    http.StatusBadGateway,
		Code:      code,
		Detail:    detail,
		PID:       &processPID,
		Alive:     alive,
		Listening: false,
		Readiness: readiness,
	}
}

func windowsCallError(err error) string {
	if err == nil || err == syscall.Errno(0) {
		return "unknown Windows error"
	}
	return err.Error()
}
