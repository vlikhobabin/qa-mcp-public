package main

import (
	"bufio"
	"bytes"
	"context"
	"encoding/base64"
	"encoding/binary"
	"encoding/json"
	"fmt"
	"net"
	"os/exec"
	"strconv"
	"strings"
	"time"
	"unicode/utf16"
)

const testClientTaskCleanupTimeout = 15 * time.Second

const (
	testClientBrokerOutcomeListenerOwner       = "listener_owner"
	testClientBrokerOutcomeAcknowledgedPID     = "acknowledged_process"
	testClientBrokerOutcomeExitedEarly         = "exited_early"
	testClientBrokerOutcomeListenerUnavailable = "listener_unavailable"
	testClientBrokerOutcomeCleanupFailed       = "cleanup_failed"
	testClientBrokerOutcomePIDHandoffFailed    = "pid_handoff_failed"
	testClientBrokerOutcomeStartFailed         = "start_failed"
)

type testClientBrokerProcessObservation struct {
	AcknowledgedPID   uint32
	ListenerPID       uint32
	AcknowledgedAlive bool
	HandleError       error
}

type testClientBrokerProcessClassification struct {
	PID     uint32
	Outcome string
}

func classifyTestClientBrokerProcess(observation testClientBrokerProcessObservation) testClientBrokerProcessClassification {
	if observation.ListenerPID != 0 {
		return testClientBrokerProcessClassification{
			PID:     observation.ListenerPID,
			Outcome: testClientBrokerOutcomeListenerOwner,
		}
	}
	if observation.AcknowledgedPID == 0 {
		return testClientBrokerProcessClassification{Outcome: testClientBrokerOutcomeStartFailed}
	}
	if !observation.AcknowledgedAlive {
		return testClientBrokerProcessClassification{
			PID:     observation.AcknowledgedPID,
			Outcome: testClientBrokerOutcomeExitedEarly,
		}
	}
	if observation.HandleError != nil {
		return testClientBrokerProcessClassification{
			PID:     observation.AcknowledgedPID,
			Outcome: testClientBrokerOutcomePIDHandoffFailed,
		}
	}
	return testClientBrokerProcessClassification{
		PID:     observation.AcknowledgedPID,
		Outcome: testClientBrokerOutcomeAcknowledgedPID,
	}
}

// testClientAcknowledgedProcessLease binds cleanup to the process object that
// acknowledged the broker launch. Windows supplies these operations from one
// retained process handle, so a later PID reuse cannot redirect cleanup.
type testClientAcknowledgedProcessLease struct {
	PID       uint32
	Alive     func() bool
	Terminate func() error
	Close     func()
}

type testClientListenerOwnerResolution struct {
	PID            uint32
	Outcome        string
	LifecycleReady bool
	CleanupError   error
}

type testClientAcknowledgedProcessLeaseAcquireFunc func(
	pid uint32,
) (*testClientAcknowledgedProcessLease, *testClientProcessStartError)

// retainTestClientAcknowledgedProcessLease makes immutable process identity the
// first operation after acknowledgement. The continuation may wait for task
// completion and remove the exact task only after the lease exists.
func retainTestClientAcknowledgedProcessLease(
	pid uint32,
	acquire testClientAcknowledgedProcessLeaseAcquireFunc,
	continueAfterRetention func() *testClientProcessStartError,
) (*testClientAcknowledgedProcessLease, *testClientProcessStartError) {
	if pid == 0 || acquire == nil {
		return nil, &testClientProcessStartError{
			Status: 502,
			Code:   "testclient-launch-start-failed",
			Detail: "acknowledged TestClient process identity could not be retained",
		}
	}
	lease, startErr := acquire(pid)
	if startErr != nil {
		if continueAfterRetention != nil {
			continuationErr := continueAfterRetention()
			if continuationErr != nil && continuationErr.Code == "testclient-launch-cleanup-failed" {
				return nil, continuationErr
			}
		}
		return nil, startErr
	}
	if lease == nil || lease.PID != pid || lease.Alive == nil || lease.Terminate == nil {
		if lease != nil && lease.Close != nil {
			lease.Close()
		}
		return nil, &testClientProcessStartError{
			Status: 502,
			Code:   "testclient-pid-handoff-failed",
			Detail: "acknowledged TestClient process lease is incomplete",
		}
	}
	if continueAfterRetention == nil {
		return lease, nil
	}
	continuationErr := continueAfterRetention()
	if continuationErr == nil {
		return lease, nil
	}
	cleanupErr := terminateTestClientAcknowledgedProcessLease(lease)
	alive := lease.Alive()
	if lease.Close != nil {
		lease.Close()
	}
	if cleanupErr != nil {
		processPID := int(pid)
		return nil, &testClientProcessStartError{
			Status:    502,
			Code:      "testclient-launch-cleanup-failed",
			Detail:    cleanupErr.Error(),
			PID:       &processPID,
			Alive:     alive,
			Listening: false,
			Readiness: "cleanup_failed",
		}
	}
	return nil, continuationErr
}

func terminateTestClientAcknowledgedProcessLease(lease *testClientAcknowledgedProcessLease) error {
	if lease == nil || lease.Alive == nil || lease.Terminate == nil {
		return fmt.Errorf("exact acknowledged TestClient cleanup operation is unavailable")
	}
	if !lease.Alive() {
		return nil
	}
	if err := lease.Terminate(); err != nil {
		return err
	}
	if lease.Alive() {
		return fmt.Errorf("exact acknowledged TestClient remained alive after cleanup")
	}
	return nil
}

func resolveTestClientListenerOwner(
	lease *testClientAcknowledgedProcessLease,
	waitForOwner func() (uint32, error),
) testClientListenerOwnerResolution {
	listenerPID, listenerErr := waitForOwner()
	if listenerErr == nil && listenerPID != 0 {
		return testClientListenerOwnerResolution{
			PID:            listenerPID,
			Outcome:        testClientBrokerOutcomeListenerOwner,
			LifecycleReady: true,
		}
	}
	if lease == nil || lease.PID == 0 {
		return testClientListenerOwnerResolution{Outcome: testClientBrokerOutcomeStartFailed}
	}
	if lease.Alive == nil || !lease.Alive() {
		return testClientListenerOwnerResolution{
			PID:     lease.PID,
			Outcome: testClientBrokerOutcomeExitedEarly,
		}
	}
	if err := terminateTestClientAcknowledgedProcessLease(lease); err != nil {
		return testClientListenerOwnerResolution{
			PID:          lease.PID,
			Outcome:      testClientBrokerOutcomeCleanupFailed,
			CleanupError: err,
		}
	}
	return testClientListenerOwnerResolution{
		PID:     lease.PID,
		Outcome: testClientBrokerOutcomeListenerUnavailable,
	}
}

const testClientTaskRegistrationScript = `$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$request = [Console]::In.ReadToEnd() | ConvertFrom-Json
$taskName = [string]$request.task_name
try {
  $action = New-ScheduledTaskAction -Execute ([string]$request.broker_executable) -Argument ([string]$request.action_argument)
  $identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
  $principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
  $settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::Zero) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
  Register-ScheduledTask -TaskName $taskName -Action $action -Principal $principal -Settings $settings -Force | Out-Null
  $before = (Get-ScheduledTaskInfo -TaskName $taskName).LastRunTime
  Start-ScheduledTask -TaskName $taskName
  $deadline = (Get-Date).AddSeconds(30)
  $observed = $false
  do {
    Start-Sleep -Milliseconds 100
    $task = Get-ScheduledTask -TaskName $taskName
    $info = Get-ScheduledTaskInfo -TaskName $taskName
    if ($info.LastRunTime -gt $before) { $observed = $true }
    $state = [string]$task.State
    if ($observed -and $state -ne 'Running' -and $state -ne 'Queued') { break }
  } while ((Get-Date) -lt $deadline)
  if (-not $observed -or $state -eq 'Running' -or $state -eq 'Queued') { throw 'interactive launch task did not complete' }
  if ($info.LastTaskResult -ne 0) { throw ('interactive launch task failed: ' + $info.LastTaskResult) }
} finally {
  if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
    Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
  }
}
`

const testClientNativeBrokerStartScript = `$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$payload = [Text.Encoding]::UTF8.GetString([Convert]::FromBase64String([Console]::In.ReadToEnd())) | ConvertFrom-Json
$workingDirectory = [System.IO.Path]::GetDirectoryName([string]$payload.executable)
$shell = New-Object -ComObject Shell.Application
try {
  $shell.ShellExecute([string]$payload.executable, [string]$payload.argument_line, $workingDirectory, 'open', 1)
  [Console]::Out.WriteLine('started')
} finally {
  [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($shell)
}
`

const testClientTaskUnregisterScript = `$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$request = [Console]::In.ReadToEnd() | ConvertFrom-Json
$taskName = [string]$request.task_name
if ($taskName -notmatch '^qa-mcp-testclient-launch-[A-Za-z0-9_-]+$') {
  throw 'invalid owned TestClient task name'
}
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
  Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
}
`

type testClientTaskRegistrationRequest struct {
	TaskName         string `json:"task_name"`
	BrokerExecutable string `json:"broker_executable"`
	ActionArgument   string `json:"action_argument"`
}

type testClientTaskUnregisterRequest struct {
	TaskName string `json:"task_name"`
}

type testClientShellBrokerRequest struct {
	Executable   string `json:"executable"`
	ArgumentLine string `json:"argument_line"`
	Port         int    `json:"port"`
}

type testClientTaskCleanupFunc func(taskName string, env []string) error

type testClientTaskCleanupGuard struct {
	taskName  string
	env       []string
	cleanup   testClientTaskCleanupFunc
	completed bool
}

func newTestClientTaskCleanupGuard(
	taskName string,
	env []string,
	cleanup testClientTaskCleanupFunc,
) *testClientTaskCleanupGuard {
	return &testClientTaskCleanupGuard{
		taskName: taskName,
		env:      append([]string(nil), env...),
		cleanup:  cleanup,
	}
}

func (guard *testClientTaskCleanupGuard) Cleanup() error {
	if guard.completed {
		return nil
	}
	if guard.cleanup == nil {
		return fmt.Errorf("interactive task cleanup function is unavailable")
	}
	if err := guard.cleanup(guard.taskName, guard.env); err != nil {
		return err
	}
	guard.completed = true
	return nil
}

func (guard *testClientTaskCleanupGuard) Fallback() {
	_ = guard.Cleanup()
}

func testClientTaskRegistrationCommand() (string, []string) {
	encoded := utf16LEBase64(testClientTaskRegistrationScript)
	return "powershell.exe", []string{"-NoProfile", "-NonInteractive", "-EncodedCommand", encoded}
}

func testClientTaskRegistrationInput(taskName string, brokerExecutable string, actionArgument string) ([]byte, error) {
	return json.Marshal(testClientTaskRegistrationRequest{
		TaskName: taskName, BrokerExecutable: brokerExecutable, ActionArgument: actionArgument,
	})
}

func testClientTaskUnregisterCommand() (string, []string) {
	encoded := utf16LEBase64(testClientTaskUnregisterScript)
	return "powershell.exe", []string{"-NoProfile", "-NonInteractive", "-EncodedCommand", encoded}
}

func testClientTaskUnregisterInput(taskName string) ([]byte, error) {
	return json.Marshal(testClientTaskUnregisterRequest{TaskName: taskName})
}

func newTestClientTaskCleanupContext() (context.Context, context.CancelFunc) {
	return context.WithTimeout(context.Background(), testClientTaskCleanupTimeout)
}

func testClientTaskBrokerActionArgument(port int, nonce string) string {
	return fmt.Sprintf("-testclient-broker-port %d -testclient-broker-nonce %s", port, nonce)
}

func testClientShellBrokerInput(executable string, args []string, port int) ([]byte, error) {
	return json.Marshal(testClientShellBrokerRequest{
		Executable:   executable,
		ArgumentLine: testClientShellArgumentLine(args),
		Port:         port,
	})
}

func runTestClientTaskBroker(port int, nonce string) error {
	if !validTCPPort(port) {
		return fmt.Errorf("invalid TestClient broker rendezvous port")
	}
	decodedNonce, err := base64.RawURLEncoding.DecodeString(nonce)
	if err != nil || len(decodedNonce) != 32 {
		return fmt.Errorf("invalid TestClient broker rendezvous nonce")
	}
	connection, err := net.DialTimeout("tcp4", net.JoinHostPort("127.0.0.1", strconv.Itoa(port)), 15*time.Second)
	if err != nil {
		return fmt.Errorf("TestClient broker rendezvous connect failed: %w", err)
	}
	defer connection.Close()
	_ = connection.SetDeadline(time.Now().Add(30 * time.Second))
	reader := bufio.NewReaderSize(connection, 1<<20)
	writer := bufio.NewWriterSize(connection, 4096)
	if _, err := writer.WriteString(nonce + "\n"); err != nil {
		return fmt.Errorf("TestClient broker rendezvous authentication failed: %w", err)
	}
	if err := writer.Flush(); err != nil {
		return fmt.Errorf("TestClient broker rendezvous authentication failed: %w", err)
	}
	encodedPayload, err := reader.ReadString('\n')
	if err != nil {
		return fmt.Errorf("TestClient broker rendezvous request failed: %w", err)
	}
	payload, err := base64.StdEncoding.DecodeString(strings.TrimSpace(encodedPayload))
	if err != nil {
		return fmt.Errorf("TestClient broker rendezvous request was invalid")
	}
	var request testClientShellBrokerRequest
	if err := json.Unmarshal(payload, &request); err != nil || strings.TrimSpace(request.Executable) == "" || !validTCPPort(request.Port) {
		return fmt.Errorf("TestClient broker launch request was invalid")
	}
	pid, startErr := startTestClientFromNativeBroker(payload, nil)
	if startErr != nil {
		detail := startErr.Error()
		if len(detail) > 1024 {
			detail = detail[:1024]
		}
		encodedDetail := base64.StdEncoding.EncodeToString([]byte(detail))
		_, _ = writer.WriteString("failed " + encodedDetail + "\n")
		_ = writer.Flush()
		return startErr
	}
	acknowledgement := "started"
	if pid != 0 {
		acknowledgement += " " + strconv.FormatUint(uint64(pid), 10)
	}
	if _, err := writer.WriteString(acknowledgement + "\n"); err != nil {
		return fmt.Errorf("TestClient broker acknowledgement failed: %w", err)
	}
	return writer.Flush()
}

func startTestClientFromNativeBroker(payload []byte, env []string) (uint32, error) {
	command := exec.Command(
		"powershell.exe", "-NoProfile", "-NonInteractive", "-Command", testClientNativeBrokerStartScript,
	)
	if len(env) > 0 {
		command.Env = env
	}
	command.Stdin = strings.NewReader(base64.StdEncoding.EncodeToString(payload))
	var stdout bytes.Buffer
	var stderr bytes.Buffer
	command.Stdout = &stdout
	command.Stderr = &stderr
	hideChildWindow(command)
	configureProcessGroup(command)
	if err := command.Run(); err != nil {
		detail := strings.TrimSpace(stderr.String())
		if detail == "" {
			detail = err.Error()
		}
		return 0, fmt.Errorf("native TestClient broker PowerShell launch failed: %s", detail)
	}
	pidValue := strings.TrimSpace(stdout.String())
	if pidValue == "started" {
		return 0, nil
	}
	pid, err := strconv.ParseUint(pidValue, 10, 32)
	if err != nil || pid == 0 {
		return 0, fmt.Errorf("native TestClient broker returned an invalid process acknowledgement")
	}
	return uint32(pid), nil
}

func parseTaskBrokerAcknowledgement(acknowledgement string) (uint32, bool) {
	fields := strings.Fields(strings.TrimSpace(acknowledgement))
	if len(fields) == 1 && fields[0] == "started" {
		return 0, true
	}
	if len(fields) != 2 || fields[0] != "started" {
		return 0, false
	}
	pidValue, err := strconv.ParseUint(fields[1], 10, 32)
	if err != nil || pidValue == 0 {
		return 0, false
	}
	return uint32(pidValue), true
}

func parseTaskBrokerFailure(acknowledgement string) (string, bool) {
	fields := strings.Fields(strings.TrimSpace(acknowledgement))
	if len(fields) != 2 || fields[0] != "failed" {
		return "", false
	}
	decoded, err := base64.StdEncoding.DecodeString(fields[1])
	if err != nil || len(decoded) == 0 {
		return "", false
	}
	return string(decoded), true
}

func utf16LEBase64(value string) string {
	codeUnits := utf16.Encode([]rune(value))
	buffer := make([]byte, len(codeUnits)*2)
	for index, codeUnit := range codeUnits {
		binary.LittleEndian.PutUint16(buffer[index*2:], codeUnit)
	}
	return base64.StdEncoding.EncodeToString(buffer)
}
