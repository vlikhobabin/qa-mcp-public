//go:build windows

package main

import (
	"context"
	"encoding/json"
	"errors"
	"net"
	"os"
	"os/exec"
	"strconv"
	"strings"
	"testing"
	"time"
	"unsafe"

	"golang.org/x/sys/windows"
)

func TestHiddenWorkerLifecycleNativeHelper(t *testing.T) {
	switch os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_MODE") {
	case "worker":
		probe := os.Getenv("QA_MCP_S2_TEST_PROBE")
		fault := os.Getenv("QA_MCP_S2_TEST_FAULT")
		switch fault {
		case "assign":
			hiddenWorkerAssignProcessToJob = func(_ windows.Handle, process windows.Handle) error {
				pid, _ := windows.GetProcessId(process)
				_ = os.WriteFile(probe, []byte(strconv.FormatUint(uint64(pid), 10)), 0o600)
				return errors.New("injected job assignment failure")
			}
		case "publish":
			hiddenWorkerPublishResponse = func(_ string, data []byte) error {
				var response hiddenWorkerLifecycleResponse
				_ = json.Unmarshal(data, &response)
				value := strconv.FormatUint(uint64(response.ChildPID), 10) + "," + strconv.FormatUint(response.WorkerJobHandle, 10)
				_ = os.WriteFile(probe, []byte(value), 0o600)
				return errors.New("injected response publication failure")
			}
		case "publish-block", "publish-temp-block":
			hiddenWorkerPublishResponse = func(path string, data []byte) error {
				var response struct {
					WorkerPID, ChildPID, ListenerPID uint32
					JobHandle, WorkerJobHandle       uint64
				}
				_ = json.Unmarshal(data, &response)
				handle, kind := response.JobHandle, "remote"
				if response.WorkerJobHandle != 0 {
					handle, kind = response.WorkerJobHandle, "local"
				}
				value := strings.Join([]string{strconv.FormatUint(uint64(response.WorkerPID), 10), strconv.FormatUint(uint64(response.ChildPID), 10), strconv.FormatUint(uint64(response.ListenerPID), 10), strconv.FormatUint(handle, 10), kind, os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_RESPONSE")}, ",")
				if fault == "publish-temp-block" {
					_ = os.WriteFile(path+".tmp", data, 0o600)
				}
				_ = os.WriteFile(probe, []byte(value), 0o600)
				time.Sleep(30 * time.Second)
				return errors.New("blocked publication unexpectedly resumed")
			}
		case "assign-errors":
			hiddenWorkerAssignProcessToJob = func(_ windows.Handle, process windows.Handle) error {
				pid, _ := windows.GetProcessId(process)
				_ = os.WriteFile(probe, []byte(strconv.FormatUint(uint64(pid), 10)), 0o600)
				return errors.New("injected assignment failure")
			}
			hiddenWorkerTerminateProcess = func(windows.Handle, uint32) error { return errors.New("injected terminate failure") }
			hiddenWorkerWaitProcess = func(windows.Handle, uint32) (uint32, error) { return uint32(windows.WAIT_TIMEOUT), nil }
		}
		if workerErr := runHiddenWorkerLifecycleWorker(); workerErr != nil {
			if fault == "assign-errors" {
				_ = os.WriteFile(probe+".error", []byte(workerErr.Error()), 0o600)
			}
			t.Fatal(workerErr)
		}
	case "child":
		port, err := strconv.Atoi(os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_PORT"))
		if err != nil {
			t.Fatal(err)
		}
		if os.Args[len(os.Args)-1] == "no-listener" {
			if probe := os.Getenv("QA_MCP_S2_TEST_PROBE"); probe != "" {
				_ = os.WriteFile(probe, []byte(strconv.Itoa(os.Getpid())), 0o600)
			}
			time.Sleep(30 * time.Second)
			return
		}
		listener, err := net.Listen("tcp4", "127.0.0.1:"+strconv.Itoa(port))
		if err != nil {
			t.Fatal(err)
		}
		defer listener.Close()
		if len(os.Args) > 1 && os.Args[len(os.Args)-1] == "exit" {
			time.Sleep(500 * time.Millisecond)
			return
		}
		time.Sleep(30 * time.Second)
	case "unrelated":
		time.Sleep(30 * time.Second)
	default:
		t.Skip("internal lifecycle helper")
	}
}

func hiddenWorkerWaitProbe(t *testing.T, path string) []byte {
	t.Helper()
	deadline := time.Now().Add(10 * time.Second)
	for time.Now().Before(deadline) {
		if data, err := os.ReadFile(path); err == nil {
			return data
		}
		time.Sleep(25 * time.Millisecond)
	}
	t.Fatalf("test-owned probe was not published: %s", path)
	return nil
}

func hiddenWorkerProbeValues(t *testing.T, path string) []uint64 {
	t.Helper()
	data := hiddenWorkerWaitProbe(t, path)
	var err error
	parts := strings.Split(string(data), ",")
	values := make([]uint64, len(parts))
	for index, part := range parts {
		values[index], err = strconv.ParseUint(part, 10, 64)
		if err != nil {
			t.Fatal(err)
		}
	}
	return values
}

func TestHiddenWorkerLifecycleProvisionalHandleCancellationNative(t *testing.T) {
	for _, fault := range []string{"publish-block", "publish-temp-block"} {
		t.Run(fault, func(t *testing.T) {
			executable, err := os.Executable()
			if err != nil {
				t.Fatal(err)
			}
			unrelated := exec.Command(executable, "-test.run=^TestHiddenWorkerLifecycleNativeHelper$", "-test.count=1")
			unrelated.Env = append(os.Environ(), "QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_MODE=unrelated")
			if err = unrelated.Start(); err != nil {
				t.Fatal(err)
			}
			defer func() { _ = unrelated.Process.Kill(); _, _ = unrelated.Process.Wait() }()
			probe := t.TempDir() + `\provisional.txt`
			request := nativeHiddenWorkerRequest(t, freeHiddenWorkerPort(t), "hold")
			request.Environment = append(request.Environment, "QA_MCP_S2_TEST_FAULT="+fault, "QA_MCP_S2_TEST_PROBE="+probe)
			ctx, cancel := context.WithCancel(context.Background())
			defer cancel()
			result := make(chan error, 1)
			go func() {
				lifecycle, startErr := startHiddenWorkerLifecycle(ctx, request)
				if lifecycle != nil {
					_ = lifecycle.Close()
				}
				result <- startErr
			}()
			parts := strings.Split(string(hiddenWorkerWaitProbe(t, probe)), ",")
			if len(parts) != 6 {
				t.Fatalf("invalid provisional probe: %q", parts)
			}
			workerPID, _ := strconv.ParseUint(parts[0], 10, 32)
			childPID, _ := strconv.ParseUint(parts[1], 10, 32)
			listenerPID, _ := strconv.ParseUint(parts[2], 10, 32)
			cancel()
			select {
			case startErr := <-result:
				if startErr == nil {
					t.Fatal("canceled provisional transfer returned no error")
				}
			case <-time.After(10 * time.Second):
				t.Fatal("canceled provisional transfer did not return")
			}
			if parts[4] != "local" {
				t.Fatalf("worker created provisional controller handle: %s", parts[4])
			}
			assertHiddenWorkerResourcesGone(t, request, uint32(workerPID), uint32(childPID), uint32(listenerPID), 0, parts[5])
			unrelatedHandle, unrelatedAlive := hiddenWorkerProcessState(uint32(unrelated.Process.Pid))
			if unrelatedHandle != 0 {
				_ = windows.CloseHandle(unrelatedHandle)
			}
			if !unrelatedAlive {
				t.Fatal("unrelated process or handle was changed")
			}
		})
	}
}

func TestHiddenWorkerLifecycleAssignmentCleanupErrorsNative(t *testing.T) {
	probe := t.TempDir() + `\assign-errors.txt`
	request := nativeHiddenWorkerRequest(t, freeHiddenWorkerPort(t), "hold")
	request.Environment = append(request.Environment, "QA_MCP_S2_TEST_FAULT=assign-errors", "QA_MCP_S2_TEST_PROBE="+probe)
	if lifecycle, err := startHiddenWorkerLifecycle(context.Background(), request); err == nil || lifecycle != nil {
		t.Fatalf("assignment cleanup failure was admitted: %#v, %v", lifecycle, err)
	}
	values := hiddenWorkerProbeValues(t, probe)
	child, childAlive := hiddenWorkerProcessState(uint32(values[0]))
	if child != 0 {
		if childAlive {
			_ = windows.TerminateProcess(child, 125)
		}
		_, _ = windows.WaitForSingleObject(child, 5_000)
		_ = windows.CloseHandle(child)
	}
	workerError := string(hiddenWorkerWaitProbe(t, probe+".error"))
	for _, marker := range []string{"injected assignment failure", "injected terminate failure", "WAIT_TIMEOUT"} {
		if !strings.Contains(workerError, marker) {
			t.Fatalf("assignment cleanup lost %q: %s", marker, workerError)
		}
	}
}

func TestHiddenWorkerLifecycleCleanupWaitTimeoutIsError(t *testing.T) {
	oldTerminateProcess, oldWait, oldCloseHandle := hiddenWorkerTerminateProcess, hiddenWorkerWaitProcess, hiddenWorkerCloseHandle
	defer func() {
		hiddenWorkerTerminateProcess, hiddenWorkerWaitProcess, hiddenWorkerCloseHandle = oldTerminateProcess, oldWait, oldCloseHandle
	}()
	for name, status := range map[string]uint32{"WAIT_TIMEOUT": uint32(windows.WAIT_TIMEOUT), "unexpected wait status": 99} {
		t.Run(name, func(t *testing.T) {
			hiddenWorkerTerminateProcess = func(windows.Handle, uint32) error { return nil }
			hiddenWorkerWaitProcess = func(windows.Handle, uint32) (uint32, error) { return status, nil }
			hiddenWorkerCloseHandle = func(windows.Handle) error { return nil }
			lifecycle := &hiddenWorkerLifecycle{worker: 11, done: make(chan struct{})}
			if err := lifecycle.Close(); err == nil || !strings.Contains(err.Error(), name) {
				t.Fatalf("%s was accepted as cleanup success: %v", name, err)
			}
		})
	}
}

func TestHiddenWorkerLifecycleControllerTransferCancellationNative(t *testing.T) {
	executable, err := os.Executable()
	if err != nil {
		t.Fatal(err)
	}
	unrelated := exec.Command(executable, "-test.run=^TestHiddenWorkerLifecycleNativeHelper$", "-test.count=1")
	unrelated.Env = append(os.Environ(), "QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_MODE=unrelated")
	if err = unrelated.Start(); err != nil {
		t.Fatal(err)
	}
	defer func() { _ = unrelated.Process.Kill(); _, _ = unrelated.Process.Wait() }()
	type transfer struct {
		response hiddenWorkerLifecycleResponse
		job      windows.Handle
		path     string
	}
	for _, stage := range []string{"before-duplicate", "after-duplicate"} {
		t.Run(stage, func(t *testing.T) {
			oldTransfer := hiddenWorkerControllerTransfer
			defer func() { hiddenWorkerControllerTransfer = oldTransfer }()
			observed, release := make(chan transfer, 1), make(chan struct{})
			hiddenWorkerControllerTransfer = func(current string, response hiddenWorkerLifecycleResponse, job windows.Handle, path string) {
				if current == stage {
					observed <- transfer{response, job, path}
					<-release
				}
			}
			request := nativeHiddenWorkerRequest(t, freeHiddenWorkerPort(t), "hold")
			ctx, cancel := context.WithCancel(context.Background())
			result := make(chan error, 1)
			go func() {
				lifecycle, startErr := startHiddenWorkerLifecycle(ctx, request)
				if lifecycle != nil {
					_ = lifecycle.Close()
				}
				result <- startErr
			}()
			var current transfer
			select {
			case current = <-observed:
			case <-time.After(10 * time.Second):
				t.Fatal("transfer boundary was not reached")
			}
			cancel()
			close(release)
			select {
			case startErr := <-result:
				if startErr == nil {
					t.Fatal("canceled transfer was admitted")
				}
			case <-time.After(10 * time.Second):
				t.Fatal("canceled transfer did not return")
			}
			assertHiddenWorkerResourcesGone(t, request, current.response.WorkerPID, current.response.ChildPID, current.response.ListenerPID, current.job, current.path)
			handle, alive := hiddenWorkerProcessState(uint32(unrelated.Process.Pid))
			if handle != 0 {
				_ = windows.CloseHandle(handle)
			}
			if !alive {
				t.Fatal("unrelated process or handle was changed")
			}
		})
	}
}

func TestHiddenWorkerTransferredObserverHoldsExactJobAndTPort(t *testing.T) {
	request, response := validHiddenWorkerLifecycleFixture(t)
	job := windows.Handle(response.WorkerJobHandle)
	oldObserver := hiddenWorkerTransferredObserver
	defer func() { hiddenWorkerTransferredObserver = oldObserver }()
	calls := 0
	hiddenWorkerTransferredObserver = func(current hiddenWorkerLifecycleResponse, currentJob windows.Handle) error {
		calls++
		if current != response || currentJob != job || current.Port != request.Port {
			return errors.New("transferred observer lost exact ownership")
		}
		return nil
	}
	if err := validateHiddenWorkerTransferredObserver(response, uint64(job), request.Port); err != nil { t.Fatal(err) }
	if err := hiddenWorkerTransferredObserver(response, job); err != nil || calls != 1 {
		t.Fatalf("exact transferred observer rejected: calls=%d err=%v", calls, err)
	}
	if validateHiddenWorkerTransferredObserver(response, uint64(job+1), request.Port) == nil || validateHiddenWorkerTransferredObserver(response, uint64(job), request.Port+1) == nil || calls != 1 {
		t.Fatalf("foreign ownership reached callback: calls=%d", calls)
	}
}

func assertHiddenWorkerResourcesGone(t *testing.T, request hiddenWorkerLifecycleRequest, workerPID, childPID, listenerPID uint32, job windows.Handle, path string) {
	t.Helper()
	for name, pid := range map[string]uint32{"worker": workerPID, "child": childPID, "listener": listenerPID} {
		if pid == 0 {
			continue
		}
		handle, alive := hiddenWorkerProcessState(pid)
		if handle != 0 {
			_ = windows.CloseHandle(handle)
		}
		if alive {
			t.Fatalf("%s survived cleanup", name)
		}
	}
	if job != 0 {
		info := windows.JOBOBJECT_EXTENDED_LIMIT_INFORMATION{}
		if windows.QueryInformationJobObject(job, windows.JobObjectExtendedLimitInformation, uintptr(unsafe.Pointer(&info)), uint32(unsafe.Sizeof(info)), nil) == nil {
			_ = windows.CloseHandle(job)
			t.Fatal("controller job handle survived cleanup")
		}
	}
	if testClientPortListening(request.Port, 0) {
		t.Fatal("listener survived cleanup")
	}
	if hiddenWorkerDesktopExists(request.Identity.Desktop) {
		t.Fatal("desktop survived cleanup")
	}
	for _, current := range []string{path, path + ".tmp"} {
		if current != "" {
			if _, err := os.Stat(current); !os.IsNotExist(err) {
				t.Fatalf("response artifact survived: %s", current)
			}
		}
	}
}

func hiddenWorkerProcessState(pid uint32) (windows.Handle, bool) {
	handle, err := windows.OpenProcess(windows.PROCESS_QUERY_LIMITED_INFORMATION|windows.SYNCHRONIZE|windows.PROCESS_TERMINATE, false, pid)
	if err != nil {
		return 0, false
	}
	wait, _ := windows.WaitForSingleObject(handle, 0)
	return handle, wait == uint32(windows.WAIT_TIMEOUT)
}

func TestHiddenWorkerLifecyclePartialFailureCleanupNative(t *testing.T) {
	executable, err := os.Executable()
	if err != nil {
		t.Fatal(err)
	}
	unrelated := exec.Command(executable, "-test.run=^TestHiddenWorkerLifecycleNativeHelper$", "-test.count=1")
	unrelated.Env = append(os.Environ(), "QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_MODE=unrelated")
	if err = unrelated.Start(); err != nil {
		t.Fatal(err)
	}
	defer func() { _ = unrelated.Process.Kill(); _, _ = unrelated.Process.Wait() }()
	assertUnrelated := func() {
		handle, alive := hiddenWorkerProcessState(uint32(unrelated.Process.Pid))
		if handle != 0 {
			_ = windows.CloseHandle(handle)
		}
		if !alive {
			t.Fatal("unrelated process was changed")
		}
	}
	for _, fault := range []string{"assign", "publish"} {
		t.Run(fault, func(t *testing.T) {
			probe := t.TempDir() + `\probe.txt`
			request := nativeHiddenWorkerRequest(t, freeHiddenWorkerPort(t), "hold")
			request.Environment = append(request.Environment, "QA_MCP_S2_TEST_FAULT="+fault, "QA_MCP_S2_TEST_PROBE="+probe)
			if lifecycle, startErr := startHiddenWorkerLifecycle(context.Background(), request); startErr == nil || lifecycle != nil {
				t.Fatalf("partial failure was admitted: %#v, %v", lifecycle, startErr)
			}
			values := hiddenWorkerProbeValues(t, probe)
			child, childAlive := hiddenWorkerProcessState(uint32(values[0]))
			if child != 0 {
				defer func() {
					if childAlive {
						_ = windows.TerminateProcess(child, 125)
						_, _ = windows.WaitForSingleObject(child, 5_000)
					}
					_ = windows.CloseHandle(child)
				}()
			}
			handleAlive := false
			if fault == "publish" {
				info := windows.JOBOBJECT_EXTENDED_LIMIT_INFORMATION{}
				job := windows.Handle(values[1])
				handleAlive = windows.QueryInformationJobObject(job, windows.JobObjectExtendedLimitInformation, uintptr(unsafe.Pointer(&info)), uint32(unsafe.Sizeof(info)), nil) == nil
				if handleAlive {
					defer windows.CloseHandle(job)
				}
			}
			assertUnrelated()
			if childAlive || handleAlive {
				t.Fatalf("partial failure leaked child=%v controller_job_handle=%v", childAlive, handleAlive)
			}
		})
	}
}

func nativeHiddenWorkerRequest(t *testing.T, port int, childMode string) hiddenWorkerLifecycleRequest {
	t.Helper()
	identity, err := newHiddenDesktopProcessIdentity("s2-native-"+strconv.FormatInt(time.Now().UnixNano(), 10), "s2-native-token")
	if err != nil {
		t.Fatal(err)
	}
	executable, err := os.Executable()
	if err != nil {
		t.Fatal(err)
	}
	return hiddenWorkerLifecycleRequest{
		Identity: identity, WorkerToken: "s2-native-token",
		WorkerArgs:      []string{"-test.run=^TestHiddenWorkerLifecycleNativeHelper$", "-test.count=1"},
		ChildExecutable: executable,
		ChildArgs:       []string{"-test.run=^TestHiddenWorkerLifecycleNativeHelper$", "-test.count=1", "--", childMode},
		Environment:     os.Environ(), Port: port, Timeout: 15 * time.Second,
	}
}

func freeHiddenWorkerPort(t *testing.T) int {
	t.Helper()
	listener, err := net.Listen("tcp4", "127.0.0.1:0")
	if err != nil {
		t.Fatal(err)
	}
	defer listener.Close()
	return listener.Addr().(*net.TCPAddr).Port
}

func TestHiddenWorkerLifecycleNativeMatrix(t *testing.T) {
	t.Run("controller cancellation", func(t *testing.T) {
		ctx, cancel := context.WithCancel(context.Background())
		lifecycle, err := startHiddenWorkerLifecycle(ctx, nativeHiddenWorkerRequest(t, freeHiddenWorkerPort(t), "hold"))
		if err != nil {
			t.Fatal(err)
		}
		response := lifecycle.Response
		if response.WorkerPID == 0 || response.ChildPID == 0 || response.ListenerPID == 0 || response.WorkerJobHandle == 0 {
			t.Fatalf("incomplete native ownership response: %#v", response)
		}
		cancel()
		select {
		case <-lifecycle.done:
		case <-time.After(10 * time.Second):
			t.Fatal("canceled lifecycle did not clean up")
		}
		if err := lifecycle.Close(); err != nil {
			t.Fatalf("idempotent close failed: %v", err)
		}
	})
	t.Run("natural child exit", func(t *testing.T) {
		lifecycle, err := startHiddenWorkerLifecycle(context.Background(), nativeHiddenWorkerRequest(t, freeHiddenWorkerPort(t), "exit"))
		if err != nil {
			t.Fatal(err)
		}
		select {
		case <-lifecycle.done:
		case <-time.After(10 * time.Second):
			t.Fatal("natural child exit did not converge on cleanup")
		}
	})
	t.Run("response timeout partial start", func(t *testing.T) {
		executable, err := os.Executable()
		if err != nil {
			t.Fatal(err)
		}
		unrelated := exec.Command(executable, "-test.run=^TestHiddenWorkerLifecycleNativeHelper$", "-test.count=1")
		unrelated.Env = append(os.Environ(), "QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_MODE=unrelated")
		if err = unrelated.Start(); err != nil {
			t.Fatal(err)
		}
		defer func() { _ = unrelated.Process.Kill(); _, _ = unrelated.Process.Wait() }()
		probe := t.TempDir() + `\timeout-child.txt`
		port := freeHiddenWorkerPort(t)
		request := nativeHiddenWorkerRequest(t, port, "no-listener")
		request.Environment = append(request.Environment, "QA_MCP_S2_TEST_PROBE="+probe)
		request.Timeout = 500 * time.Millisecond
		oldControllerStart := hiddenWorkerControllerStart
		defer func() { hiddenWorkerControllerStart = oldControllerStart }()
		var workerPID uint32
		var responsePath string
		hiddenWorkerControllerStart = func(pid uint32, path string) {
			workerPID, responsePath = pid, path
		}
		if lifecycle, err := startHiddenWorkerLifecycle(context.Background(), request); err == nil || lifecycle != nil {
			t.Fatalf("partial start was admitted: %#v, %v", lifecycle, err)
		}
		childPID, parseErr := strconv.ParseUint(string(hiddenWorkerWaitProbe(t, probe)), 10, 32)
		if parseErr != nil {
			t.Fatal(parseErr)
		}
		assertHiddenWorkerResourcesGone(t, request, workerPID, uint32(childPID), 0, 0, responsePath)
		handle, alive := hiddenWorkerProcessState(uint32(unrelated.Process.Pid))
		if handle != 0 {
			_ = windows.CloseHandle(handle)
		}
		if !alive {
			t.Fatal("unrelated process or handle was changed")
		}
	})
}

func TestHiddenWorkerLifecycleForeignHandleRejectedBeforeOwnership(t *testing.T) {
	job, err := windows.CreateJobObject(nil, nil)
	if err != nil {
		t.Fatal(err)
	}
	defer windows.CloseHandle(job)
	request := nativeHiddenWorkerRequest(t, freeHiddenWorkerPort(t), "hold")
	response := hiddenWorkerLifecycleResponse{Schema: hiddenWorkerLifecycleSchema, Code: "ready", RunIDHash: request.Identity.RunIDHash,
		WorkerTokenHash: strings.Repeat("f", 64), DesktopHash: hiddenDesktopProcessHash(request.Identity.Desktop), Port: request.Port,
		WorkerPID: 1, ChildPID: 2, ListenerPID: 3, WorkerJobHandle: uint64(job)}
	data, _ := json.Marshal(response)
	oldRead := hiddenWorkerReadFile
	hiddenWorkerReadFile = func(string) ([]byte, error) { return data, nil }
	defer func() { hiddenWorkerReadFile = oldRead }()
	if lifecycle, err := startHiddenWorkerLifecycle(context.Background(), request); err == nil || lifecycle != nil {
		t.Fatalf("foreign response was admitted: %#v, %v", lifecycle, err)
	}
	info := windows.JOBOBJECT_EXTENDED_LIMIT_INFORMATION{}
	if err := windows.QueryInformationJobObject(job, windows.JobObjectExtendedLimitInformation, uintptr(unsafe.Pointer(&info)), uint32(unsafe.Sizeof(info)), nil); err != nil {
		t.Fatalf("untrusted foreign job handle was mutated or closed: %v", err)
	}
}

func TestHiddenWorkerLifecycleAmbiguousListenerRejected(t *testing.T) {
	if pid, ok := hiddenWorkerExactPIDForPort(buildTable(buildRow(stateListen, 15471, 101), buildRow(stateListen, 15471, 202)), 15471); ok || pid != 0 {
		t.Fatalf("ambiguous listeners were admitted: pid=%d ok=%v", pid, ok)
	}
}

func hiddenWorkerDesktopExists(desktop string) bool {
	name, _ := windows.UTF16PtrFromString(desktop[strings.LastIndex(desktop, `\`)+1:])
	handle, _, _ := foundationUser32.NewProc("OpenDesktopW").Call(uintptr(unsafe.Pointer(name)), 0, 0, 0x0001)
	if handle != 0 {
		foundationUser32.NewProc("CloseDesktop").Call(handle)
	}
	return handle != 0
}

func TestHiddenWorkerLifecycleCleanupContinuesAfterErrors(t *testing.T) {
	oldTerminateJob, oldTerminateProcess := hiddenWorkerTerminateJob, hiddenWorkerTerminateProcess
	oldWait, oldCloseHandle := hiddenWorkerWaitProcess, hiddenWorkerCloseHandle
	oldCloseDesktop, oldRemove := hiddenWorkerCloseDesktop, hiddenWorkerRemove
	defer func() {
		hiddenWorkerTerminateJob, hiddenWorkerTerminateProcess = oldTerminateJob, oldTerminateProcess
		hiddenWorkerWaitProcess, hiddenWorkerCloseHandle = oldWait, oldCloseHandle
		hiddenWorkerCloseDesktop, hiddenWorkerRemove = oldCloseDesktop, oldRemove
	}()
	calls := map[string]int{}
	hiddenWorkerTerminateJob = func(windows.Handle, uint32) error { calls["job"]++; return errors.New("job") }
	hiddenWorkerTerminateProcess = func(windows.Handle, uint32) error { calls["process"]++; return errors.New("process") }
	hiddenWorkerWaitProcess = func(windows.Handle, uint32) (uint32, error) { calls["wait"]++; return 0, errors.New("wait") }
	hiddenWorkerCloseHandle = func(windows.Handle) error { calls["handle"]++; return errors.New("handle") }
	hiddenWorkerCloseDesktop = func(*hiddenDesktopFoundation) error { calls["desktop"]++; return errors.New("desktop") }
	hiddenWorkerRemove = func(string) error { calls["path"]++; return errors.New("path") }
	lifecycle := &hiddenWorkerLifecycle{
		worker: 11, job: 12, desktop: &hiddenDesktopFoundation{}, responsePath: "owned",
		done: make(chan struct{}),
	}
	if err := lifecycle.Close(); err == nil {
		t.Fatal("injected cleanup errors were lost")
	}
	for _, name := range []string{"job", "process", "wait", "handle", "desktop", "path"} {
		if calls[name] == 0 {
			t.Fatalf("cleanup action %q was skipped", name)
		}
	}
}
