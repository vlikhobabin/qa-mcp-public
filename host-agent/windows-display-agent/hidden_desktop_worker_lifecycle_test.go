package main

import (
	"encoding/binary"
	"encoding/json"
	"go/ast"
	"go/parser"
	"go/token"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
	"testing"
	"time"
)

func validHiddenWorkerLifecycleFixture(t *testing.T) (hiddenWorkerLifecycleRequest, hiddenWorkerLifecycleResponse) {
	t.Helper()
	identity, err := newHiddenDesktopProcessIdentity("s2-run", "s2-worker-token")
	if err != nil {
		t.Fatal(err)
	}
	request := hiddenWorkerLifecycleRequest{
		Identity: identity, WorkerToken: "s2-worker-token",
		ChildExecutable: filepath.Join(t.TempDir(), "child"),
		Environment:     []string{"PATH=/tmp"}, Port: 15471, Timeout: 10 * time.Second,
	}
	response := hiddenWorkerLifecycleResponse{
		Schema: hiddenWorkerLifecycleSchema, Code: "ready",
		RunIDHash: identity.RunIDHash, WorkerTokenHash: identity.WorkerTokenHash,
		DesktopHash: hiddenDesktopProcessHash(identity.Desktop), Port: request.Port,
		WorkerPID: 101, ChildPID: 102, ListenerPID: 103, WorkerJobHandle: 104,
	}
	return request, response
}

func TestHiddenWorkerLifecycleRequestBounds(t *testing.T) {
	valid, _ := validHiddenWorkerLifecycleFixture(t)
	if err := validateHiddenWorkerLifecycleRequest(valid); err != nil {
		t.Fatalf("valid request rejected: %v", err)
	}
	cases := map[string]func(*hiddenWorkerLifecycleRequest){
		"identity":           func(value *hiddenWorkerLifecycleRequest) { value.Identity = hiddenDesktopProcessIdentity{} },
		"raw token mismatch": func(value *hiddenWorkerLifecycleRequest) { value.WorkerToken = "foreign" },
		"relative child":     func(value *hiddenWorkerLifecycleRequest) { value.ChildExecutable = "child.exe" },
		"invalid port":       func(value *hiddenWorkerLifecycleRequest) { value.Port = 0 },
		"short timeout":      func(value *hiddenWorkerLifecycleRequest) { value.Timeout = 0 },
		"long timeout":       func(value *hiddenWorkerLifecycleRequest) { value.Timeout = 3 * time.Minute },
	}
	for name, mutate := range cases {
		t.Run(name, func(t *testing.T) {
			value := valid
			mutate(&value)
			if validateHiddenWorkerLifecycleRequest(value) == nil {
				t.Fatal("hostile request was admitted")
			}
		})
	}
}

func TestHiddenWorkerLifecycleAdmissionFailsClosed(t *testing.T) {
	request, valid := validHiddenWorkerLifecycleFixture(t)
	if err := validateHiddenWorkerLifecycleResponse(request, valid, valid.WorkerPID); err != nil {
		t.Fatalf("valid response rejected: %v", err)
	}
	cases := map[string]func(*hiddenWorkerLifecycleResponse){
		"absent":           func(value *hiddenWorkerLifecycleResponse) { *value = hiddenWorkerLifecycleResponse{} },
		"wrong schema":     func(value *hiddenWorkerLifecycleResponse) { value.Schema = "foreign" },
		"not ready":        func(value *hiddenWorkerLifecycleResponse) { value.Code = "failed" },
		"wrong run":        func(value *hiddenWorkerLifecycleResponse) { value.RunIDHash = strings.Repeat("0", 64) },
		"wrong token":      func(value *hiddenWorkerLifecycleResponse) { value.WorkerTokenHash = strings.Repeat("1", 64) },
		"wrong desktop":    func(value *hiddenWorkerLifecycleResponse) { value.DesktopHash = strings.Repeat("2", 64) },
		"wrong port":       func(value *hiddenWorkerLifecycleResponse) { value.Port++ },
		"foreign worker":   func(value *hiddenWorkerLifecycleResponse) { value.WorkerPID++ },
		"missing child":    func(value *hiddenWorkerLifecycleResponse) { value.ChildPID = 0 },
		"missing listener": func(value *hiddenWorkerLifecycleResponse) { value.ListenerPID = 0 },
		"missing job":      func(value *hiddenWorkerLifecycleResponse) { value.WorkerJobHandle = 0 },
	}
	for name, mutate := range cases {
		t.Run(name, func(t *testing.T) {
			value := valid
			mutate(&value)
			if validateHiddenWorkerLifecycleResponse(request, value, valid.WorkerPID) == nil {
				t.Fatal("foreign response was admitted")
			}
		})
	}
	data, err := json.Marshal(valid)
	if err != nil {
		t.Fatal(err)
	}
	if strings.Contains(string(data), request.WorkerToken) {
		t.Fatal("raw worker token leaked into response")
	}
}

func TestHiddenWorkerLifecycleListenerTableRejectsAmbiguity(t *testing.T) {
	for name, rows := range map[string][][]byte{
		"duplicate same pid": {buildRow(stateListen, 15471, 101), buildRow(stateListen, 15471, 101)},
		"different pids":     {buildRow(stateListen, 15471, 101), buildRow(stateListen, 15471, 202)},
	} {
		t.Run(name, func(t *testing.T) {
			if pid, ok := hiddenWorkerExactPIDForPort(buildTable(rows...), 15471); ok || pid != 0 {
				t.Fatalf("ambiguous listeners were admitted: pid=%d ok=%v", pid, ok)
			}
		})
	}
	truncated := buildTable(buildRow(stateListen, 15471, 101))
	binary.LittleEndian.PutUint32(truncated[:4], 2)
	if pid, ok := hiddenWorkerExactPIDForPort(truncated, 15471); ok || pid != 0 {
		t.Fatalf("incomplete listener table was admitted: pid=%d ok=%v", pid, ok)
	}
}

func TestHiddenWorkerLifecycleWindowsSourceContract(t *testing.T) {
	data, err := os.ReadFile("hidden_desktop_worker_lifecycle_windows.go")
	if err != nil {
		t.Fatal(err)
	}
	text := string(data)
	worker := strings.Index(text, "func runHiddenWorkerLifecycleWorker")
	if worker < 0 {
		t.Fatal("hidden worker implementation is absent")
	}
	create := strings.Index(text[worker:], "startHiddenDesktopFoundationProcess")
	assign := strings.Index(text[worker:], "hiddenWorkerAssignProcessToJob")
	resume := strings.Index(text[worker:], "windows.ResumeThread")
	if create < 0 || assign < create || resume < assign {
		t.Fatalf("child ownership order create=%d assign=%d resume=%d", create, assign, resume)
	}
	foundation, err := os.ReadFile("hidden_desktop_process_foundation_windows.go")
	if err != nil || !strings.Contains(string(foundation), "windows.CREATE_SUSPENDED") || !strings.Contains(text[worker:], "windows.CREATE_SUSPENDED") {
		t.Fatal("S1 process primitive does not retain the S2 suspended-child flag")
	}
	for _, required := range []string{"JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE", "windows.DuplicateHandle", "waitForTestClientListenerPID", "hiddenWorkerPIDInJob"} {
		if !strings.Contains(text, required) {
			t.Fatalf("lifecycle ownership primitive %q is absent", required)
		}
	}
	for _, forbidden := range []string{"windows.OpenProcess", "windows.DuplicateHandle"} {
		if strings.Contains(text[worker:], forbidden) {
			t.Fatalf("worker-side provisional handle primitive %q survived", forbidden)
		}
	}
	for _, forbidden := range []string{"SendInput", "SetCursorPos", "SetForegroundWindow", "SwitchDesktop", "productionObserveDirectExecute", "productionLocalWindowInventory"} {
		if strings.Contains(text, forbidden) {
			t.Fatalf("later or global-input primitive %q entered S2", forbidden)
		}
	}
}

func TestHiddenWorkerTransferredObserverValidation(t *testing.T) {
	_, response := validHiddenWorkerLifecycleFixture(t)
	if err := validateHiddenWorkerTransferredObserver(response, response.WorkerJobHandle, response.Port); err != nil {
		t.Fatal(err)
	}
	for name, mutate := range map[string]func(*hiddenWorkerLifecycleResponse, *uint64, *int){
		"schema":   func(value *hiddenWorkerLifecycleResponse, _ *uint64, _ *int) { value.Schema = "foreign" },
		"code":     func(value *hiddenWorkerLifecycleResponse, _ *uint64, _ *int) { value.Code = "failed" },
		"run":      func(value *hiddenWorkerLifecycleResponse, _ *uint64, _ *int) { value.RunIDHash = "raw" },
		"token":    func(value *hiddenWorkerLifecycleResponse, _ *uint64, _ *int) { value.WorkerTokenHash = "raw" },
		"desktop":  func(value *hiddenWorkerLifecycleResponse, _ *uint64, _ *int) { value.DesktopHash = "raw" },
		"worker":   func(value *hiddenWorkerLifecycleResponse, _ *uint64, _ *int) { value.WorkerPID = 0 },
		"child":    func(value *hiddenWorkerLifecycleResponse, _ *uint64, _ *int) { value.ChildPID = 0 },
		"listener": func(value *hiddenWorkerLifecycleResponse, _ *uint64, _ *int) { value.ListenerPID = 0 },
		"job":      func(_ *hiddenWorkerLifecycleResponse, job *uint64, _ *int) { (*job)++ },
		"port":     func(_ *hiddenWorkerLifecycleResponse, _ *uint64, port *int) { (*port)++ },
	} {
		t.Run(name, func(t *testing.T) {
			current, job, port := response, response.WorkerJobHandle, response.Port
			mutate(&current, &job, &port)
			if validateHiddenWorkerTransferredObserver(current, job, port) == nil {
				t.Fatalf("hostile observer ownership admitted: %#v job=%d port=%d", current, job, port)
			}
		})
	}
}

func TestHiddenWorkerTransferredObserverRunsAfterAckBeforeJobClose(t *testing.T) {
	data, err := os.ReadFile("hidden_desktop_worker_lifecycle_windows.go")
	if err != nil {
		t.Fatal(err)
	}
	text := string(data)
	worker := strings.Index(text, "func runHiddenWorkerLifecycleWorker() error")
	if worker < 0 {
		t.Fatal("worker implementation is absent")
	}
	ack := strings.Index(text[worker:], "os.IsNotExist(statErr)")
	validate := strings.Index(text[worker:], "validateHiddenWorkerTransferredObserver(")
	observe := strings.Index(text[worker:], "hiddenWorkerTransferredObserver(response, job)")
	closeJob := strings.Index(text[worker:], "hiddenWorkerCloseHandle(job)")
	if ack < 0 || validate <= ack || observe <= validate || closeJob <= observe {
		t.Fatalf("observer order is not acknowledgement -> validation -> callback -> job close: %d %d %d %d %d", worker, ack, validate, observe, closeJob)
	}
}

func extractHiddenWorkerFunction(t *testing.T, path, name string) string {
	t.Helper()
	data, err := os.ReadFile(path)
	if err != nil { t.Fatal(err) }
	fset := token.NewFileSet()
	file, err := parser.ParseFile(fset, path, data, 0)
	if err != nil { t.Fatal(err) }
	for _, declaration := range file.Decls {
		function, ok := declaration.(*ast.FuncDecl)
		if ok && function.Name.Name == name {
			return string(data[fset.Position(function.Pos()).Offset:fset.Position(function.End()).Offset])
		}
	}
	t.Fatalf("function %s is absent from %s", name, path)
	return ""
}

func TestHiddenWorkerLifecycleWorkerConnectedTransferredObserverHarness(t *testing.T) {
	worker := extractHiddenWorkerFunction(t, "hidden_desktop_worker_lifecycle_windows.go", "runHiddenWorkerLifecycleWorker")
	validator := extractHiddenWorkerFunction(t, "hidden_desktop_worker_lifecycle.go", "validateHiddenWorkerTransferredObserver")
	directory := t.TempDir()
	if err := os.Mkdir(filepath.Join(directory, "windows"), 0o755); err != nil { t.Fatal(err) }
	if err := os.WriteFile(filepath.Join(directory, "go.mod"), []byte("module lifecycleharness\n\ngo 1.24\n"), 0o600); err != nil { t.Fatal(err) }
	windowsStub := `package windows

import "sync"

type Handle uintptr
type JOBOBJECT_BASIC_LIMIT_INFORMATION struct { LimitFlags uint32 }
type JOBOBJECT_EXTENDED_LIMIT_INFORMATION struct { BasicLimitInformation JOBOBJECT_BASIC_LIMIT_INFORMATION }

const (
	JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x2000
	JobObjectExtendedLimitInformation = 9
	CREATE_SUSPENDED = 4
	WAIT_OBJECT_0 = 0
	WAIT_TIMEOUT = 258
	INFINITE = 0xffffffff
)

var state struct { sync.Mutex; job Handle; open bool; closes int }

func CreateJobObject(_ *byte, _ *uint16) (Handle, error) { state.Lock(); defer state.Unlock(); state.job, state.open = 77, true; return state.job, nil }
func SetInformationJobObject(Handle, int32, uintptr, uint32) (uintptr, error) { return 1, nil }
func ResumeThread(Handle) (uint32, error) { return 1, nil }
func CloseHandle(value Handle) error { state.Lock(); defer state.Unlock(); if value == state.job && state.open { state.open = false; state.closes++ }; return nil }
func JobOpen(value Handle) bool { state.Lock(); defer state.Unlock(); return value == state.job && state.open }
func JobCloseCount() int { state.Lock(); defer state.Unlock(); return state.closes }
`
	if err := os.WriteFile(filepath.Join(directory, "windows", "windows.go"), []byte(windowsStub), 0o600); err != nil { t.Fatal(err) }
	harness := `package lifecycleharness

import (
	"context"
	"encoding/base64"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"sync/atomic"
	"testing"
	"time"
	"unsafe"

	"lifecycleharness/windows"
)

const hiddenWorkerLifecycleSchema = "qa-mcp.internal-hidden-worker-lifecycle.v1"

type hiddenWorkerLifecycleResponse struct {
	Schema, Code, RunIDHash, WorkerTokenHash, DesktopHash string
	Port int; WorkerPID, ChildPID, ListenerPID uint32; WorkerJobHandle uint64
}

type hiddenWorkerProcess struct { Process, Thread windows.Handle; ProcessId uint32 }
type transferredObservation struct { response hiddenWorkerLifecycleResponse; job windows.Handle }

var observerEntered = make(chan transferredObservation, 1)
var observerRelease = make(chan struct{})
var listenerLive atomic.Bool
var listenerPort atomic.Int32
var finalWaits atomic.Int32

func validHiddenWindowHash(value string) bool { return len(value) == 64 }
func validTCPPort(value int) bool { return value > 0 && value < 65536 }
func validateHiddenDesktopProcessName(string) error { return nil }
func hiddenWorkerLifecycleStringsBounded([]string) bool { return true }
func hiddenDesktopProcessHash(string) string { return strings.Repeat("a", 64) }
func composeHiddenDesktopProcessEnvironment([]string, []string) ([]string, error) { return nil, nil }
func startHiddenDesktopFoundationProcess(string, []string, []string, string, uint32) (hiddenWorkerProcess, error) { return hiddenWorkerProcess{Process: 21, Thread: 22, ProcessId: 202}, nil }
var hiddenWorkerAssignProcessToJob = func(windows.Handle, windows.Handle) error { return nil }
var hiddenWorkerTerminateProcess = func(windows.Handle, uint32) error { return nil }
func waitForTestClientListenerPID(_ context.Context, port int, _ time.Duration) (uint32, error) { listenerPort.Store(int32(port)); listenerLive.Store(true); return 303, nil }
func hiddenWorkerPIDListeningOnPort(port uint16) (uint32, bool) { return 303, listenerLive.Load() && int32(port) == listenerPort.Load() }
func hiddenWorkerPIDInJob(uint32, uint64) bool { return true }
var hiddenWorkerPublishResponse = func(string, []byte) error { return nil }
var hiddenWorkerWaitProcess = func(windows.Handle, uint32) (uint32, error) { return windows.WAIT_TIMEOUT, nil }
var hiddenWorkerCloseHandle = windows.CloseHandle
var hiddenWorkerTransferredObserver = func(response hiddenWorkerLifecycleResponse, job windows.Handle) error {
	observerEntered <- transferredObservation{response: response, job: job}
	<-observerRelease
	return nil
}
func waitHiddenWorkerProcess(windows.Handle, uint32) error { finalWaits.Add(1); listenerLive.Store(false); listenerPort.Store(0); return nil }
` + validator + "\n\n" + worker + `

func TestConnectedTransferredObserverBoundary(t *testing.T) {
	responsePath := filepath.Join(t.TempDir(), "acknowledged.json")
	t.Setenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_RESPONSE", responsePath)
	t.Setenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_DESKTOP", "private-desktop")
	t.Setenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_TOKEN", "worker-token")
	t.Setenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_RUN_HASH", strings.Repeat("b", 64))
	t.Setenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_PORT", "15471")
	t.Setenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_CHILD", filepath.Join(t.TempDir(), "child.exe"))
	t.Setenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_ARGS", base64.RawStdEncoding.EncodeToString([]byte("[]")))
	done := make(chan error, 1)
	go func() { done <- runHiddenWorkerLifecycleWorker() }()
	var observed transferredObservation
	select {
	case observed = <-observerEntered:
	case <-time.After(5 * time.Second): t.Fatal("actual worker callback boundary was not reached")
	}
	if observed.response.Port != 15471 || observed.response.ListenerPID != 303 || observed.response.WorkerJobHandle != uint64(observed.job) {
		t.Fatalf("callback lost exact response ownership: %#v job=%d", observed.response, observed.job)
	}
	if !listenerLive.Load() || listenerPort.Load() != int32(observed.response.Port) || !windows.JobOpen(observed.job) || windows.JobCloseCount() != 0 || finalWaits.Load() != 0 {
		t.Fatalf("job/listener cleanup ran while callback blocked: listener=%v listener_port=%d response_port=%d job_open=%v closes=%d waits=%d", listenerLive.Load(), listenerPort.Load(), observed.response.Port, windows.JobOpen(observed.job), windows.JobCloseCount(), finalWaits.Load())
	}
	close(observerRelease)
	select {
	case err := <-done:
		if err != nil { t.Fatal(err) }
	case <-time.After(5 * time.Second): t.Fatal("worker did not complete after callback release")
	}
	if listenerLive.Load() || listenerPort.Load() != 0 || windows.JobOpen(observed.job) || windows.JobCloseCount() != 1 || finalWaits.Load() != 1 {
		t.Fatalf("normal cleanup did not follow callback release: listener=%v listener_port=%d job_open=%v closes=%d waits=%d", listenerLive.Load(), listenerPort.Load(), windows.JobOpen(observed.job), windows.JobCloseCount(), finalWaits.Load())
	}
}
`
	if err := os.WriteFile(filepath.Join(directory, "worker_test.go"), []byte(harness), 0o600); err != nil { t.Fatal(err) }
	command := exec.Command("go", "test", "./...", "-count=1")
	command.Dir = directory
	output, err := command.CombinedOutput()
	if err != nil { t.Fatalf("exact worker harness failed: %v\n%s", err, output) }
}
