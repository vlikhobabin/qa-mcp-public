//go:build windows

package main

import (
	"bytes"
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"os/exec"
	"testing"
	"time"
)

const integrationTaskRegisterScript = `$ErrorActionPreference = 'Stop'
$request = [Console]::In.ReadToEnd() | ConvertFrom-Json
$taskName = [string]$request.task_name
if ($taskName -notmatch '^qa-mcp-testclient-launch-[A-Za-z0-9_-]+$') {
  throw 'invalid owned TestClient task name'
}
$action = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -NonInteractive -Command exit 0'
$identity = [Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal = New-ScheduledTaskPrincipal -UserId $identity -LogonType Interactive -RunLevel Limited
$settings = New-ScheduledTaskSettingsSet -ExecutionTimeLimit ([TimeSpan]::FromMinutes(1))
Register-ScheduledTask -TaskName $taskName -Action $action -Principal $principal -Settings $settings -Force | Out-Null
`

const integrationTaskAbsentScript = `$ErrorActionPreference = 'Stop'
$request = [Console]::In.ReadToEnd() | ConvertFrom-Json
$taskName = [string]$request.task_name
if ($taskName -notmatch '^qa-mcp-testclient-launch-[A-Za-z0-9_-]+$') {
  throw 'invalid owned TestClient task name'
}
if (Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue) {
  throw 'exact owned TestClient task remains registered'
}
`

func runIntegrationTaskScript(script string, taskName string) error {
	input, err := json.Marshal(testClientTaskUnregisterRequest{TaskName: taskName})
	if err != nil {
		return err
	}
	ctx, cancel := context.WithTimeout(context.Background(), 20*time.Second)
	defer cancel()
	command := exec.CommandContext(
		ctx,
		"powershell.exe",
		"-NoProfile",
		"-NonInteractive",
		"-EncodedCommand",
		utf16LEBase64(script),
	)
	command.Env = os.Environ()
	command.Stdin = bytes.NewReader(input)
	hideChildWindow(command)
	configureProcessGroup(command)
	if output, err := command.CombinedOutput(); err != nil {
		return fmt.Errorf("owned scheduled-task integration command failed: %w (output-bytes=%d)", err, len(output))
	}
	return nil
}

func registerIntegrationTask(taskName string) error {
	return runIntegrationTaskScript(integrationTaskRegisterScript, taskName)
}

func requireIntegrationTaskAbsent(t *testing.T, taskName string) {
	t.Helper()
	if err := runIntegrationTaskScript(integrationTaskAbsentScript, taskName); err != nil {
		t.Fatal(err)
	}
}

func integrationTaskName(t *testing.T, label string) string {
	t.Helper()
	suffix, err := randomTaskBrokerValue(12)
	if err != nil {
		t.Fatal(err)
	}
	return "qa-mcp-testclient-launch-" + label + "-" + suffix
}

func TestWindowsTransientTaskCleanupIntegration(t *testing.T) {
	if os.Getenv("QA_MCP_RUN_WINDOWS_TASK_CLEANUP_INTEGRATION") != "1" {
		t.Skip("set QA_MCP_RUN_WINDOWS_TASK_CLEANUP_INTEGRATION=1 on an owned Windows station")
	}
	env := os.Environ()

	t.Run("canceled_parent_uses_independent_exact_cleanup", func(t *testing.T) {
		taskName := integrationTaskName(t, "cancel")
		if err := registerIntegrationTask(taskName); err != nil {
			t.Fatal(err)
		}
		defer func() { _ = unregisterTestClientLaunchTask(taskName, env) }()

		parent, cancel := context.WithCancel(context.Background())
		cancel()
		if !errors.Is(parent.Err(), context.Canceled) {
			t.Fatalf("parent context was not canceled: %v", parent.Err())
		}
		if err := unregisterTestClientLaunchTask(taskName, env); err != nil {
			t.Fatalf("independent exact cleanup after parent cancellation failed: %v", err)
		}
		requireIntegrationTaskAbsent(t, taskName)
	})

	t.Run("cleanup_failure_blocks_success_and_fallback_retries_exact_name", func(t *testing.T) {
		taskName := integrationTaskName(t, "fallback")
		if err := registerIntegrationTask(taskName); err != nil {
			t.Fatal(err)
		}
		defer func() { _ = unregisterTestClientLaunchTask(taskName, env) }()

		calls := 0
		guard := newTestClientTaskCleanupGuard(taskName, env, func(gotTaskName string, gotEnv []string) error {
			calls++
			if gotTaskName != taskName {
				return fmt.Errorf("unexpected task ownership")
			}
			if calls == 1 {
				return fmt.Errorf("injected exact cleanup failure")
			}
			return unregisterTestClientLaunchTask(gotTaskName, gotEnv)
		})
		if err := guard.Cleanup(); err == nil {
			t.Fatal("injected explicit cleanup failure did not block success")
		}
		guard.Fallback()
		if calls != 2 {
			t.Fatalf("fallback cleanup calls=%d, want 2", calls)
		}
		requireIntegrationTaskAbsent(t, taskName)
	})
}
