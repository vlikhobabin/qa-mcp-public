package main

import (
	"encoding/base64"
	"encoding/json"
	"errors"
	"go/ast"
	"go/parser"
	"go/token"
	"os"
	"strings"
	"testing"
	"time"
)

func TestInteractiveHostAgentLaunchContextIsBounded(t *testing.T) {
	payload := testClientLaunchResult(
		nil,
		testClientLaunchRequest{InfobasePath: "C:/Bases/demo10413", Port: 15381},
		`File="C:/Bases/demo10413";`,
		platformExecutable{Path: `C:\Program Files\1cv8\8.3.27.2130\bin\1cv8.exe`, Version: "8.3.27.2130"},
		nil,
		false,
		true,
		true,
		"ready",
		testClientLaunchContext{Method: interactiveTaskShellBrokerMethod},
		"",
	)
	context, ok := payload["launch_context"].(map[string]any)
	if !ok || context["method"] != "interactive_task_shell_broker" {
		t.Fatalf("launch context = %#v", payload["launch_context"])
	}
	if len(context) != 1 {
		t.Fatalf("launch context exposes implementation details: %#v", context)
	}
}

func TestInteractiveShellBrokerKeepsSecretsOutOfHelperCommandLine(t *testing.T) {
	secret := "do-not-put-this-in-helper-argv"
	actionArgument := testClientTaskBrokerActionArgument(32123, "one-time-nonce")
	executable, registrationArgs := testClientTaskRegistrationCommand()
	joined := executable + " " + strings.Join(registrationArgs, " ") + " " + actionArgument
	if strings.Contains(joined, secret) {
		t.Fatalf("task or registration command line contains the TestClient credential")
	}
	payload, err := testClientShellBrokerInput(
		`C:\Program Files\1cv8\8.3.27.2130\bin\1cv8.exe`,
		[]string{"ENTERPRISE", `/IBConnectionString`, `File="C:\Bases\demo";`, "/P" + secret},
		15381,
	)
	if err != nil {
		t.Fatal(err)
	}
	if !strings.Contains(string(payload), secret) {
		t.Fatalf("authenticated in-memory payload omitted the credential")
	}
	if !strings.Contains(actionArgument, "-testclient-broker-port 32123") {
		t.Fatal("task action does not invoke the native transient broker mode")
	}
	if !strings.Contains(testClientNativeBrokerStartScript, "Shell.Application") ||
		!strings.Contains(testClientNativeBrokerStartScript, ".ShellExecute(") {
		t.Fatal("native broker does not delegate launch through the interactive Windows shell")
	}
	if strings.Contains(testClientNativeBrokerStartScript, "Start-Process") {
		t.Fatal("native broker still launches TestClient as a hidden PowerShell child")
	}
	if !strings.Contains(testClientNativeBrokerStartScript, "FromBase64String") ||
		!strings.Contains(testClientNativeBrokerStartScript, "Text.Encoding]::UTF8") {
		t.Fatal("native broker does not decode its in-memory payload as explicit UTF-8")
	}
	if !strings.Contains(testClientNativeBrokerStartScript, "FinalReleaseComObject") {
		t.Fatal("native broker does not release the interactive shell COM object")
	}
}

func TestInteractiveShellBrokerAcknowledgementCarriesPID(t *testing.T) {
	pid, ok := parseTaskBrokerAcknowledgement("started 4242\r\n")
	if !ok || pid != 4242 {
		t.Fatalf("ack pid = %d ok=%v", pid, ok)
	}
	pid, ok = parseTaskBrokerAcknowledgement("started\n")
	if !ok || pid != 0 {
		t.Fatalf("legacy ack pid = %d ok=%v", pid, ok)
	}
	for _, ack := range []string{"", "started 0", "started abc", "failed 4242", "started 1 extra"} {
		if pid, ok := parseTaskBrokerAcknowledgement(ack); ok {
			t.Fatalf("invalid ack %q parsed as pid=%d", ack, pid)
		}
	}
}

func TestInteractiveShellBrokerFailureCarriesBoundedDetail(t *testing.T) {
	encoded := base64.StdEncoding.EncodeToString([]byte("System.InvalidOperationException: Access is denied"))
	detail, ok := parseTaskBrokerFailure("failed " + encoded + "\r\n")
	if !ok || detail != "System.InvalidOperationException: Access is denied" {
		t.Fatalf("failure detail = %q ok=%v", detail, ok)
	}
	for _, acknowledgement := range []string{"", "failed", "failed !!!", "started 4242"} {
		if detail, ok := parseTaskBrokerFailure(acknowledgement); ok {
			t.Fatalf("invalid failure %q parsed as %q", acknowledgement, detail)
		}
	}
}

func TestClassifyTestClientBrokerProcessObservation(t *testing.T) {
	tests := []struct {
		name        string
		observation testClientBrokerProcessObservation
		wantPID     uint32
		wantOutcome string
	}{
		{
			name: "listener owner is authoritative over acknowledged launcher",
			observation: testClientBrokerProcessObservation{
				AcknowledgedPID:   4100,
				ListenerPID:       4200,
				AcknowledgedAlive: false,
			},
			wantPID:     4200,
			wantOutcome: testClientBrokerOutcomeListenerOwner,
		},
		{
			name: "acknowledged process disappeared before tport",
			observation: testClientBrokerProcessObservation{
				AcknowledgedPID:   4300,
				AcknowledgedAlive: false,
				HandleError:       errors.New("The parameter is incorrect."),
			},
			wantPID:     4300,
			wantOutcome: testClientBrokerOutcomeExitedEarly,
		},
		{
			name: "live acknowledged process cannot be owned",
			observation: testClientBrokerProcessObservation{
				AcknowledgedPID:   4400,
				AcknowledgedAlive: true,
				HandleError:       errors.New("Access is denied."),
			},
			wantPID:     4400,
			wantOutcome: testClientBrokerOutcomePIDHandoffFailed,
		},
		{
			name:        "broker returned no process acknowledgement",
			observation: testClientBrokerProcessObservation{},
			wantOutcome: testClientBrokerOutcomeStartFailed,
		},
	}

	for _, test := range tests {
		t.Run(test.name, func(t *testing.T) {
			got := classifyTestClientBrokerProcess(test.observation)
			if got.PID != test.wantPID || got.Outcome != test.wantOutcome {
				t.Fatalf("classification = %#v, want pid=%d outcome=%q", got, test.wantPID, test.wantOutcome)
			}
		})
	}
}

func TestInteractiveTaskPowerShellScriptsSuppressProgressCLIXML(t *testing.T) {
	for name, script := range map[string]string{
		"registration": testClientTaskRegistrationScript,
		"broker-start": testClientNativeBrokerStartScript,
		"unregister":   testClientTaskUnregisterScript,
	} {
		if !strings.Contains(script, "$ProgressPreference = 'SilentlyContinue'") {
			t.Fatalf("%s script does not suppress PowerShell progress stream", name)
		}
	}
}

func TestInteractiveShellBrokerUsesOneString1CQuoting(t *testing.T) {
	got := testClientShellArgumentLine([]string{
		"ENTERPRISE",
		"/IBConnectionString",
		`File="C:\Bases\demo";`,
		"/NАдминистратор",
		`/Pp"w`,
		"/TESTCLIENT",
		"-TPort",
		"15381",
		"/DisableStartupDialogs",
		"/DisableStartupMessages",
	})
	want := `ENTERPRISE /IBConnectionString "File=""C:\Bases\demo"";" /N"Администратор" /P"p""w" /TESTCLIENT -TPort 15381 /DisableStartupDialogs /DisableStartupMessages`
	if got != want {
		t.Fatalf("shell argument line = %q, want %q", got, want)
	}
}

func TestTestClientLaunchHardwareLicenseSearchIsExplicitOptIn(t *testing.T) {
	connection := `File="C:\Bases\demo";`
	withoutOptIn := testClientLaunchArgs(
		testClientLaunchRequest{InfobasePath: `C:\Bases\demo`, Port: 15381}, connection,
	)
	if strings.Contains(strings.Join(withoutOptIn, " "), "/UseHWLicenses+") {
		t.Fatal("hardware-license search was enabled without explicit opt-in")
	}
	withOptIn := testClientLaunchArgs(
		testClientLaunchRequest{InfobasePath: `C:\Bases\demo`, Port: 15381, UseHWLicenses: true}, connection,
	)
	if !strings.Contains(strings.Join(withOptIn, " "), "/UseHWLicenses+") {
		t.Fatal("explicit hardware-license search option was not forwarded")
	}
}

func TestInteractiveTaskCleanupUsesExactNameAndBoundedIndependentContext(t *testing.T) {
	taskName := "qa-mcp-testclient-launch-exact-owned-task"
	executable, args := testClientTaskUnregisterCommand()
	if executable != "powershell.exe" || len(args) != 4 || args[2] != "-EncodedCommand" {
		t.Fatalf("unexpected cleanup command: %q %#v", executable, args)
	}
	if !strings.Contains(testClientTaskUnregisterScript, "Unregister-ScheduledTask -TaskName $taskName") {
		t.Fatal("cleanup does not unregister the exact task name")
	}
	if strings.Contains(testClientTaskUnregisterScript, "qa-mcp-testclient-launch-*") {
		t.Fatal("cleanup contains a name-wide task pattern")
	}
	input, err := testClientTaskUnregisterInput(taskName)
	if err != nil {
		t.Fatal(err)
	}
	var request testClientTaskUnregisterRequest
	if err := json.Unmarshal(input, &request); err != nil {
		t.Fatal(err)
	}
	if request.TaskName != taskName || strings.Contains(string(input), "password") {
		t.Fatalf("unexpected cleanup input: %s", input)
	}

	ctx, cancel := newTestClientTaskCleanupContext()
	defer cancel()
	select {
	case <-ctx.Done():
		t.Fatalf("fresh cleanup context is already canceled: %v", ctx.Err())
	default:
	}
	deadline, ok := ctx.Deadline()
	if !ok || time.Until(deadline) <= 0 || time.Until(deadline) > testClientTaskCleanupTimeout {
		t.Fatalf("cleanup deadline is not bounded by %s", testClientTaskCleanupTimeout)
	}
}

func TestInteractiveTaskCleanupGuardFailsClosedAndRetriesFallback(t *testing.T) {
	taskName := "qa-mcp-testclient-launch-guard-owned-task"
	env := []string{"SYSTEMROOT=C:\\Windows"}
	calls := 0
	guard := newTestClientTaskCleanupGuard(taskName, env, func(gotTaskName string, gotEnv []string) error {
		calls++
		if gotTaskName != taskName {
			t.Fatalf("cleanup task name = %q, want %q", gotTaskName, taskName)
		}
		if len(gotEnv) != 1 || gotEnv[0] != env[0] {
			t.Fatalf("cleanup env = %#v, want %#v", gotEnv, env)
		}
		if calls == 1 {
			return errors.New("injected exact-task cleanup failure")
		}
		return nil
	})

	if err := guard.Cleanup(); err == nil {
		t.Fatal("explicit cleanup failure was not returned")
	}
	guard.Fallback()
	if calls != 2 {
		t.Fatalf("failed explicit cleanup did not retain one fallback retry: calls=%d", calls)
	}
	guard.Fallback()
	if calls != 2 {
		t.Fatalf("successful fallback was not idempotent: calls=%d", calls)
	}
}

func TestInteractiveTaskCleanupGuardSuppressesFallbackAfterSuccess(t *testing.T) {
	calls := 0
	guard := newTestClientTaskCleanupGuard(
		"qa-mcp-testclient-launch-guard-success",
		nil,
		func(string, []string) error {
			calls++
			return nil
		},
	)
	if err := guard.Cleanup(); err != nil {
		t.Fatal(err)
	}
	guard.Fallback()
	if calls != 1 {
		t.Fatalf("successful explicit cleanup unexpectedly retried: calls=%d", calls)
	}
}

func TestWindowsLaunchUsesDirectInteractiveChildWithRetainedProcessLease(t *testing.T) {
	source, err := os.ReadFile("testclient_process_windows.go")
	if err != nil {
		t.Fatal(err)
	}
	file, err := parser.ParseFile(token.NewFileSet(), "testclient_process_windows.go", source, 0)
	if err != nil {
		t.Fatal(err)
	}
	var launch *ast.FuncDecl
	for _, declaration := range file.Decls {
		candidate, ok := declaration.(*ast.FuncDecl)
		if ok && candidate.Name.Name == "startTestClientProcess" {
			launch = candidate
			break
		}
	}
	if launch == nil {
		t.Fatal("startTestClientProcess production launch function is missing")
	}

	shellRequestCalls := 0
	shellLaunchCalls := 0
	retainedLeaseCalls := 0
	taskCleanupCalls := 0
	ast.Inspect(launch.Body, func(node ast.Node) bool {
		call, ok := node.(*ast.CallExpr)
		if !ok {
			return true
		}
		switch function := call.Fun.(type) {
		case *ast.Ident:
			if function.Name == "testClientShellBrokerInput" {
				shellRequestCalls++
			}
			if function.Name == "startTestClientFromNativeBroker" {
				shellLaunchCalls++
			}
			if function.Name == "openAcknowledgedTestClientProcessLease" {
				retainedLeaseCalls++
			}
			if function.Name == "newTestClientTaskCleanupGuard" {
				taskCleanupCalls++
			}
		}
		return true
	})
	if shellRequestCalls != 1 || shellLaunchCalls != 0 || retainedLeaseCalls != 1 || taskCleanupCalls != 1 {
		t.Fatalf(
			"production direct-shell-child wiring invalid: shell_request=%d shell_launch=%d retained_lease=%d task_cleanup=%d",
			shellRequestCalls,
			shellLaunchCalls,
			retainedLeaseCalls,
			taskCleanupCalls,
		)
	}
}

func TestResolveTestClientListenerOwnerTerminatesRetainedLeaseWithoutLifecycle(t *testing.T) {
	alive := true
	terminated := 0
	lease := &testClientAcknowledgedProcessLease{
		PID:   4450,
		Alive: func() bool { return alive },
		Terminate: func() error {
			terminated++
			alive = false
			return nil
		},
	}
	resolution := resolveTestClientListenerOwner(lease, func() (uint32, error) {
		return 0, errors.New("listener owner timeout")
	})
	if resolution.Outcome != testClientBrokerOutcomeListenerUnavailable || resolution.PID != lease.PID {
		t.Fatalf("timeout resolution = %#v", resolution)
	}
	if resolution.LifecycleReady || resolution.CleanupError != nil || terminated != 1 || alive {
		t.Fatalf("timeout did not fail closed with exact cleanup: %#v terminated=%d alive=%v", resolution, terminated, alive)
	}
}

func TestResolveTestClientListenerOwnerDoesNotTerminateRecycledOrExitedLease(t *testing.T) {
	terminated := 0
	lease := &testClientAcknowledgedProcessLease{
		PID:   4460,
		Alive: func() bool { return false },
		Terminate: func() error {
			terminated++
			return nil
		},
	}
	resolution := resolveTestClientListenerOwner(lease, func() (uint32, error) {
		return 0, errors.New("listener owner timeout")
	})
	if resolution.Outcome != testClientBrokerOutcomeExitedEarly || resolution.LifecycleReady || terminated != 0 {
		t.Fatalf("exited lease resolution = %#v terminated=%d", resolution, terminated)
	}
}

func TestResolveTestClientListenerOwnerSelectsDifferingOwnerWithoutCleanup(t *testing.T) {
	terminated := 0
	lease := &testClientAcknowledgedProcessLease{
		PID:   4470,
		Alive: func() bool { return true },
		Terminate: func() error {
			terminated++
			return nil
		},
	}
	resolution := resolveTestClientListenerOwner(lease, func() (uint32, error) { return 4480, nil })
	if resolution.Outcome != testClientBrokerOutcomeListenerOwner || resolution.PID != 4480 || !resolution.LifecycleReady {
		t.Fatalf("listener-owner resolution = %#v", resolution)
	}
	if terminated != 0 {
		t.Fatalf("authoritative listener selection terminated acknowledged lease %d times", terminated)
	}
}

func TestResolveTestClientListenerOwnerSurfacesExactCleanupFailure(t *testing.T) {
	cleanupErr := errors.New("injected retained-handle termination failure")
	lease := &testClientAcknowledgedProcessLease{
		PID:       4490,
		Alive:     func() bool { return true },
		Terminate: func() error { return cleanupErr },
	}
	resolution := resolveTestClientListenerOwner(lease, func() (uint32, error) {
		return 0, errors.New("listener owner timeout")
	})
	if resolution.Outcome != testClientBrokerOutcomeCleanupFailed || resolution.PID != lease.PID {
		t.Fatalf("cleanup-failure resolution = %#v", resolution)
	}
	if resolution.LifecycleReady || !errors.Is(resolution.CleanupError, cleanupErr) {
		t.Fatalf("cleanup failure was not surfaced: %#v", resolution)
	}
}

func TestRetainAcknowledgedProcessLeasePrecedesRegistrationContinuation(t *testing.T) {
	events := []string{}
	wantLease := &testClientAcknowledgedProcessLease{
		PID:       4510,
		Alive:     func() bool { return true },
		Terminate: func() error { return nil },
	}
	lease, startErr := retainTestClientAcknowledgedProcessLease(
		wantLease.PID,
		func(pid uint32) (*testClientAcknowledgedProcessLease, *testClientProcessStartError) {
			events = append(events, "retain-handle")
			if pid != wantLease.PID {
				t.Fatalf("acquire pid = %d, want %d", pid, wantLease.PID)
			}
			return wantLease, nil
		},
		func() *testClientProcessStartError {
			events = append(events, "registration-and-task-cleanup")
			return nil
		},
	)
	if startErr != nil || lease != wantLease {
		t.Fatalf("retention result lease=%#v error=%#v", lease, startErr)
	}
	if got := strings.Join(events, ","); got != "retain-handle,registration-and-task-cleanup" {
		t.Fatalf("acknowledgement ordering = %q", got)
	}
}

func TestRetainAcknowledgedProcessLeaseCleansExactLeaseAfterContinuationFailure(t *testing.T) {
	events := []string{}
	alive := true
	closed := false
	wantErr := &testClientProcessStartError{Code: "injected-registration-failure"}
	lease, startErr := retainTestClientAcknowledgedProcessLease(
		4520,
		func(pid uint32) (*testClientAcknowledgedProcessLease, *testClientProcessStartError) {
			events = append(events, "retain-handle")
			return &testClientAcknowledgedProcessLease{
				PID:   pid,
				Alive: func() bool { return alive },
				Terminate: func() error {
					events = append(events, "terminate-retained-handle")
					alive = false
					return nil
				},
				Close: func() {
					events = append(events, "close-retained-handle")
					closed = true
				},
			}, nil
		},
		func() *testClientProcessStartError {
			events = append(events, "registration-and-task-cleanup")
			return wantErr
		},
	)
	if lease != nil || startErr != wantErr {
		t.Fatalf("failed continuation result lease=%#v error=%#v", lease, startErr)
	}
	if alive || !closed {
		t.Fatalf("retained lease cleanup alive=%v closed=%v", alive, closed)
	}
	wantEvents := "retain-handle,registration-and-task-cleanup,terminate-retained-handle,close-retained-handle"
	if got := strings.Join(events, ","); got != wantEvents {
		t.Fatalf("failed continuation ordering = %q, want %q", got, wantEvents)
	}
}

func TestRetainAcknowledgedProcessLeaseStillCleansTaskAfterAcquisitionFailure(t *testing.T) {
	events := []string{}
	wantErr := &testClientProcessStartError{Code: "testclient-pid-handoff-failed"}
	lease, startErr := retainTestClientAcknowledgedProcessLease(
		4530,
		func(uint32) (*testClientAcknowledgedProcessLease, *testClientProcessStartError) {
			events = append(events, "retain-handle-attempt")
			return nil, wantErr
		},
		func() *testClientProcessStartError {
			events = append(events, "registration-and-task-cleanup")
			return nil
		},
	)
	if lease != nil || startErr != wantErr {
		t.Fatalf("acquisition failure result lease=%#v error=%#v", lease, startErr)
	}
	if got := strings.Join(events, ","); got != "retain-handle-attempt,registration-and-task-cleanup" {
		t.Fatalf("acquisition failure ordering = %q", got)
	}
}
