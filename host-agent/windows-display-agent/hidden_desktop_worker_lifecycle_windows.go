//go:build windows

package main

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"fmt"
	"os"
	"path/filepath"
	"strconv"
	"sync"
	"time"
	"unsafe"

	"golang.org/x/sys/windows"
)

var (
	hiddenWorkerIsProcessInJob                             = kernel32.NewProc("IsProcessInJob")
	hiddenWorkerTerminateJob, hiddenWorkerTerminateProcess = windows.TerminateJobObject, windows.TerminateProcess
	hiddenWorkerCloseHandle                                = windows.CloseHandle
	hiddenWorkerCloseDesktop                               = func(value *hiddenDesktopFoundation) error { return value.Close() }
	hiddenWorkerRemove                                     = os.Remove
	hiddenWorkerReadFile                                   = os.ReadFile
	hiddenWorkerWaitProcess                                = windows.WaitForSingleObject
	hiddenWorkerAssignProcessToJob                         = windows.AssignProcessToJobObject
	hiddenWorkerPublishResponse                            = publishHiddenWorkerResponse
	hiddenWorkerControllerStart                            = func(uint32, string) {}
	hiddenWorkerControllerTransfer                         = func(string, hiddenWorkerLifecycleResponse, windows.Handle, string) {}
	hiddenWorkerTransferredObserver                        = func(hiddenWorkerLifecycleResponse, windows.Handle) error { return nil }
)

type hiddenWorkerLifecycle struct {
	Response     hiddenWorkerLifecycleResponse
	worker, job  windows.Handle
	workerInJob  bool
	port         int
	desktop      *hiddenDesktopFoundation
	responsePath string
	done         chan struct{}
	once         sync.Once
	closeErr     error
}

func (lifecycle *hiddenWorkerLifecycle) Close() error { return lifecycle.close(true) }

func (lifecycle *hiddenWorkerLifecycle) close(terminate bool) error {
	lifecycle.once.Do(func() {
		var listener windows.Handle
		var listenerErr error
		var children []windows.Handle
		var childrenErr error
		if lifecycle.port != 0 {
			if pid, ok := hiddenWorkerPIDListeningOnPort(uint16(lifecycle.port)); ok { listener, listenerErr = windows.OpenProcess(windows.SYNCHRONIZE, false, pid) }
		}
		if lifecycle.job == 0 && lifecycle.worker != 0 {
			if pid, pidErr := windows.GetProcessId(lifecycle.worker); pidErr == nil { children, childrenErr = hiddenWorkerChildHandles(pid) } else { childrenErr = pidErr }
		}
		jobErr := hiddenWorkerCleanup(terminate && lifecycle.job != 0, func() error { return hiddenWorkerTerminateJob(lifecycle.job, 0) })
		processErr := hiddenWorkerCleanup(terminate && lifecycle.worker != 0 && (!lifecycle.workerInJob || jobErr != nil), func() error { return hiddenWorkerTerminateProcess(lifecycle.worker, 125) })
		waitErr := hiddenWorkerCleanup(lifecycle.worker != 0, func() error { return waitHiddenWorkerProcess(lifecycle.worker, 5_000) })
		for _, child := range children { childrenErr = errors.Join(childrenErr, waitHiddenWorkerProcess(child, 5_000), hiddenWorkerCloseHandle(child)) }
		listenerErr = errors.Join(listenerErr, hiddenWorkerCleanup(listener != 0, func() error { return waitHiddenWorkerProcess(listener, 5_000) }))
		handleErr := errors.Join(hiddenWorkerCleanup(lifecycle.worker != 0, func() error { return hiddenWorkerCloseHandle(lifecycle.worker) }), hiddenWorkerCleanup(lifecycle.job != 0, func() error { return hiddenWorkerCloseHandle(lifecycle.job) }), hiddenWorkerCleanup(listener != 0, func() error { return hiddenWorkerCloseHandle(listener) }))
		desktopErr := hiddenWorkerCleanup(lifecycle.desktop != nil, func() error { return hiddenWorkerCloseDesktop(lifecycle.desktop) })
		pathErr := hiddenWorkerCleanup(lifecycle.responsePath != "", func() error { return errors.Join(removeHiddenWorkerPath(lifecycle.responsePath), removeHiddenWorkerPath(lifecycle.responsePath+".tmp")) })
		lifecycle.worker, lifecycle.job, lifecycle.workerInJob, lifecycle.port, lifecycle.desktop, lifecycle.responsePath = 0, 0, false, 0, nil, ""
		lifecycle.closeErr = errors.Join(jobErr, processErr, waitErr, childrenErr, listenerErr, handleErr, desktopErr, pathErr)
		close(lifecycle.done)
	})
	return lifecycle.closeErr
}

func waitHiddenWorkerProcess(process windows.Handle, timeout uint32) error {
	status, err := hiddenWorkerWaitProcess(process, timeout)
	if err != nil { return err }
	if status == uint32(windows.WAIT_OBJECT_0) { return nil }
	if status == uint32(windows.WAIT_TIMEOUT) { return errors.New("WAIT_TIMEOUT") }
	return fmt.Errorf("unexpected wait status %#x", status)
}

func removeHiddenWorkerPath(path string) error {
	err := hiddenWorkerRemove(path)
	if os.IsNotExist(err) { return nil }
	return err
}

func hiddenWorkerCleanup(active bool, action func() error) error { if active { return action() }; return nil }

func publishHiddenWorkerResponse(path string, data []byte) error {
	temporary := path + ".tmp"
	if err := os.WriteFile(temporary, data, 0o600); err != nil { return err }
	defer os.Remove(temporary)
	return os.Rename(temporary, path)
}

func startHiddenWorkerLifecycle(ctx context.Context, request hiddenWorkerLifecycleRequest) (*hiddenWorkerLifecycle, error) {
	if err := validateHiddenWorkerLifecycleRequest(request); err != nil { return nil, err }
	desktop, err := createHiddenDesktopFoundation(request.Identity)
	if err != nil { return nil, err }
	lifecycle := &hiddenWorkerLifecycle{desktop: desktop, port: request.Port, done: make(chan struct{})}
	fail := func(cause error) (*hiddenWorkerLifecycle, error) { return nil, errors.Join(cause, lifecycle.Close()) }
	responseFile, err := os.CreateTemp("", "qa-mcp-hidden-worker-*.json")
	if err != nil { return fail(err) }
	lifecycle.responsePath = responseFile.Name()
	if closeErr := responseFile.Close(); closeErr != nil { return fail(closeErr) }
	_ = os.Remove(lifecycle.responsePath)
	encodedArgs, _ := json.Marshal(request.ChildArgs)
	environment, err := composeHiddenDesktopProcessEnvironment(request.Environment, []string{
		"QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_MODE=worker", "QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_RESPONSE=" + lifecycle.responsePath,
		"QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_RUN_HASH=" + request.Identity.RunIDHash, "QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_TOKEN=" + request.WorkerToken,
		"QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_DESKTOP=" + request.Identity.Desktop, "QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_CHILD=" + request.ChildExecutable,
		"QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_ARGS=" + base64.RawStdEncoding.EncodeToString(encodedArgs),
		"QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_PORT=" + strconv.Itoa(request.Port),
	})
	if err != nil { return fail(err) }
	workerExecutable, err := os.Executable()
	if err != nil { return fail(err) }
	worker, err := startHiddenDesktopFoundationProcess(workerExecutable, request.WorkerArgs, environment, request.Identity.Desktop)
	if err != nil { return fail(err) }
	lifecycle.worker = worker.Process
	hiddenWorkerControllerStart(worker.ProcessId, lifecycle.responsePath)
	deadline := time.Now().Add(request.Timeout)
	var response hiddenWorkerLifecycleResponse
	for time.Now().Before(deadline) {
		data, readErr := hiddenWorkerReadFile(lifecycle.responsePath)
		if readErr == nil {
			if json.Unmarshal(data, &response) != nil { return fail(errors.New("hidden worker response is malformed")) }
			break
		}
		if wait, _ := windows.WaitForSingleObject(worker.Process, 0); wait == windows.WAIT_OBJECT_0 { return fail(errors.New("hidden worker exited before response")) }
		select {
		case <-ctx.Done():
			return fail(ctx.Err())
		case <-time.After(50 * time.Millisecond):
		}
	}
	if response.Schema == "" { return fail(errors.New("hidden worker response timed out")) }
	if validateHiddenWorkerLifecycleResponse(request, response, worker.ProcessId) != nil { return fail(errors.New("hidden worker response identity failed")) }
	hiddenWorkerControllerTransfer("before-duplicate", response, 0, lifecycle.responsePath)
	if err = ctx.Err(); err != nil { return fail(err) }
	var job windows.Handle
	if err = windows.DuplicateHandle(worker.Process, windows.Handle(response.WorkerJobHandle), windows.CurrentProcess(), &job, 0, false, windows.DUPLICATE_SAME_ACCESS); err != nil { return fail(err) }
	lifecycle.job = job
	hiddenWorkerControllerTransfer("after-duplicate", response, job, lifecycle.responsePath)
	if err = ctx.Err(); err != nil { return fail(err) }
	if !hiddenWorkerPIDInJob(response.ChildPID, uint64(job)) || !hiddenWorkerPIDInJob(response.ListenerPID, uint64(job)) { return fail(errors.New("hidden worker response job failed")) }
	if hiddenWorkerAssignProcessToJob(job, worker.Process) != nil || !hiddenWorkerPIDInJob(response.WorkerPID, uint64(job)) { return fail(errors.New("hidden worker response ownership failed")) }
	lifecycle.workerInJob = true
	if err = removeHiddenWorkerPath(lifecycle.responsePath); err != nil { return fail(err) }
	lifecycle.Response = response
	go func() {
		select {
		case <-ctx.Done():
			_ = lifecycle.Close()
		case <-lifecycle.done:
		}
	}()
	go func() { _, _ = hiddenWorkerWaitProcess(worker.Process, windows.INFINITE); _ = lifecycle.close(false) }()
	return lifecycle, nil
}

func hiddenWorkerPIDInJob(pid uint32, jobValue uint64) bool {
	process, err := windows.OpenProcess(windows.PROCESS_QUERY_LIMITED_INFORMATION, false, pid)
	if err != nil { return false }
	defer windows.CloseHandle(process)
	var inJob int32
	ok, _, _ := hiddenWorkerIsProcessInJob.Call(uintptr(process), uintptr(windows.Handle(jobValue)), uintptr(unsafe.Pointer(&inJob)))
	return ok != 0 && inJob != 0
}

func hiddenWorkerPIDListeningOnPort(port uint16) (uint32, bool) {
	var size uint32
	procGetExtendedTcpTable.Call(0, uintptr(unsafe.Pointer(&size)), 0, afInet, tcpTableOwnerPidListener, 0)
	if size == 0 { return 0, false }
	table := make([]byte, size)
	result, _, _ := procGetExtendedTcpTable.Call(uintptr(unsafe.Pointer(&table[0])), uintptr(unsafe.Pointer(&size)), 0, afInet, tcpTableOwnerPidListener, 0)
	if result != 0 || int(size) > len(table) { return 0, false }
	return hiddenWorkerExactPIDForPort(table[:size], port)
}

func hiddenWorkerChildHandles(parent uint32) ([]windows.Handle, error) {
	snapshot, err := windows.CreateToolhelp32Snapshot(windows.TH32CS_SNAPPROCESS, 0); if err != nil { return nil, err }; defer windows.CloseHandle(snapshot)
	entry := windows.ProcessEntry32{Size: uint32(unsafe.Sizeof(windows.ProcessEntry32{}))}; if err = windows.Process32First(snapshot, &entry); err != nil { return nil, err }
	var handles []windows.Handle; var result error
	for {
		if entry.ParentProcessID == parent { handle, openErr := windows.OpenProcess(windows.SYNCHRONIZE, false, entry.ProcessID); if openErr == nil { handles = append(handles, handle) } else if !errors.Is(openErr, windows.ERROR_INVALID_PARAMETER) { result = errors.Join(result, openErr) } }
		err = windows.Process32Next(snapshot, &entry); if errors.Is(err, windows.ERROR_NO_MORE_FILES) { return handles, result }; if err != nil { return handles, errors.Join(result, err) }
	}
}

func runHiddenWorkerLifecycleWorker() error {
	responsePath, desktopName := os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_RESPONSE"), os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_DESKTOP")
	token, runHash := os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_TOKEN"), os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_RUN_HASH")
	port, portErr := strconv.Atoi(os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_PORT"))
	childExecutable := os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_CHILD")
	argsJSON, decodeErr := base64.RawStdEncoding.DecodeString(os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_ARGS"))
	var childArgs []string
	if decodeErr == nil { decodeErr = json.Unmarshal(argsJSON, &childArgs) }
	if !filepath.IsAbs(responsePath) || validateHiddenDesktopProcessName(desktopName) != nil || len(token) == 0 || portErr != nil || !validTCPPort(port) ||
		!filepath.IsAbs(childExecutable) || decodeErr != nil || !hiddenWorkerLifecycleStringsBounded(childArgs) {
		return errors.New("hidden worker request is invalid") }
	job, err := windows.CreateJobObject(nil, nil)
	if err != nil { return err }
	defer func() { if job != 0 { _ = windows.CloseHandle(job) } }()
	limits := windows.JOBOBJECT_EXTENDED_LIMIT_INFORMATION{}
	limits.BasicLimitInformation.LimitFlags = windows.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
	if _, err = windows.SetInformationJobObject(job, windows.JobObjectExtendedLimitInformation, uintptr(unsafe.Pointer(&limits)), uint32(unsafe.Sizeof(limits))); err != nil { return err }
	childEnvironment, err := composeHiddenDesktopProcessEnvironment(os.Environ(), []string{"QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_MODE=child", "QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_PORT=" + strconv.Itoa(port)})
	if err != nil { return err }
	child, err := startHiddenDesktopFoundationProcess(childExecutable, childArgs, childEnvironment, desktopName, windows.CREATE_SUSPENDED)
	if err != nil { return err }
	defer windows.CloseHandle(child.Process)
	defer windows.CloseHandle(child.Thread)
	if err = hiddenWorkerAssignProcessToJob(job, child.Process); err != nil {
		return errors.Join(err, hiddenWorkerTerminateProcess(child.Process, 125), waitHiddenWorkerProcess(child.Process, 5_000))
	}
	if _, err = windows.ResumeThread(child.Thread); err != nil { return err }
	listenerPID, listenerErr := waitForTestClientListenerPID(context.Background(), port, 60*time.Second)
	exactPID, exact := hiddenWorkerPIDListeningOnPort(uint16(port))
	if listenerErr != nil || !exact || exactPID != listenerPID || !hiddenWorkerPIDInJob(listenerPID, uint64(job)) { return errors.Join(listenerErr, errors.New("listener is outside exact job")) }
	response := hiddenWorkerLifecycleResponse{Schema: hiddenWorkerLifecycleSchema, Code: "ready", RunIDHash: runHash, WorkerTokenHash: hiddenDesktopProcessHash(token), DesktopHash: hiddenDesktopProcessHash(desktopName), Port: port, WorkerPID: uint32(os.Getpid()), ChildPID: child.ProcessId, ListenerPID: listenerPID, WorkerJobHandle: uint64(job)}
	data, _ := json.Marshal(response)
	if err = hiddenWorkerPublishResponse(responsePath, append(data, '\n')); err != nil { return err }
	for {
		if _, statErr := os.Stat(responsePath); os.IsNotExist(statErr) { break }
		if wait, waitErr := hiddenWorkerWaitProcess(child.Process, 50); waitErr != nil || wait == uint32(windows.WAIT_OBJECT_0) { return waitErr }
	}
	if err = validateHiddenWorkerTransferredObserver(response, uint64(job), port); err != nil { return err }
	if err = hiddenWorkerTransferredObserver(response, job); err != nil { return err }
	if err = hiddenWorkerCloseHandle(job); err != nil { return err }
	job = 0
	return waitHiddenWorkerProcess(child.Process, windows.INFINITE)
}
