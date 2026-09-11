//go:build windows

package main

import (
	"bytes"
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"io"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"testing"
	"time"

	"golang.org/x/sys/windows"
)

type hiddenDirectNativeEvidence struct {
	Schema, Status, CandidateSHA256, PlatformVersion string
	TargetHash, ExecuteHash                          string
	Receipt                                          hiddenDirectObservationReceipt
	Isolation                                        hiddenWindowIsolationReceipt
	WorkerPID, ChildPID, ListenerPID                 uint32
	CleanupComplete, RawUIRetained                   bool
}

var (
	hiddenDirectOpenProcess        = windows.OpenProcess
	hiddenDirectWaitProcess        = windows.WaitForSingleObject
	hiddenDirectCloseProcess       = windows.CloseHandle
	hiddenDirectProcessInJob       = hiddenWorkerPIDInJob
	hiddenDirectListenerForPort    = hiddenWorkerPIDListeningOnPort
	hiddenDirectInventoryIsolation = inventoryHiddenWindowIsolationClassified
	hiddenDirectObserveUIA         = observeHiddenDirectUIA
	hiddenDirectWorkerNow          = time.Now
	hiddenDirectWorkerSleep        = time.Sleep
	hiddenDirectReportPreReceipt   = func(value hiddenDirectPreReceiptDiagnostic) error {
		return validateHiddenDirectPreReceiptDiagnostic(value)
	}
)

func hiddenDirectProcessLiveness(pid uint32) hiddenDirectLivenessStatus {
	handle, err := hiddenDirectOpenProcess(windows.SYNCHRONIZE, false, pid)
	if err != nil {
		return hiddenDirectLivenessUnknown
	}
	wait, waitErr := hiddenDirectWaitProcess(handle, 0)
	closeErr := hiddenDirectCloseProcess(handle)
	if waitErr != nil || closeErr != nil {
		return hiddenDirectLivenessUnknown
	}
	if wait == uint32(windows.WAIT_OBJECT_0) {
		return hiddenDirectLivenessExited
	}
	if wait == uint32(windows.WAIT_TIMEOUT) {
		return hiddenDirectLivenessLive
	}
	return hiddenDirectLivenessUnknown
}

func newHiddenDirectExactLivenessFence(response hiddenWorkerLifecycleResponse, job windows.Handle) func() hiddenDirectLivenessSnapshot {
	return func() hiddenDirectLivenessSnapshot {
		listenerPID, exactPort := hiddenDirectListenerForPort(uint16(response.Port))
		return hiddenDirectLivenessSnapshot{
			Child: hiddenDirectProcessLiveness(response.ChildPID), Listener: hiddenDirectProcessLiveness(response.ListenerPID),
			ChildInJob: hiddenDirectProcessInJob(response.ChildPID, uint64(job)), ListenerInJob: hiddenDirectProcessInJob(response.ListenerPID, uint64(job)),
			ExactPort: exactPort && listenerPID == response.ListenerPID,
		}
	}
}

func observeHiddenDirectWindowsFencedSample(response hiddenWorkerLifecycleResponse, job windows.Handle, desktop string) hiddenDirectFencedSample {
	return observeHiddenDirectFencedSample(newHiddenDirectExactLivenessFence(response, job), func() (hiddenWindowIsolationReceipt, []hiddenWindowIdentity, hiddenDirectInventoryFailure, error) {
		return hiddenDirectInventoryIsolation(desktop, job)
	})
}

func writeHiddenDirectPreReceiptDiagnostic(path string, value hiddenDirectPreReceiptDiagnostic) error {
	if validateHiddenDirectPreReceiptDiagnostic(value) != nil || !filepath.IsAbs(path) {
		return os.ErrInvalid
	}
	data, err := json.Marshal(value)
	if err != nil {
		return err
	}
	return os.WriteFile(path, append(data, '\n'), 0o600)
}

func readHiddenDirectPreReceiptDiagnostic(path string) (hiddenDirectPreReceiptDiagnostic, error) {
	var value hiddenDirectPreReceiptDiagnostic
	data, err := os.ReadFile(path)
	if err == nil {
		decoder := json.NewDecoder(bytes.NewReader(data))
		decoder.DisallowUnknownFields()
		if err = decoder.Decode(&value); err == nil {
			if trailingErr := decoder.Decode(&struct{}{}); trailingErr != io.EOF {
				err = os.ErrInvalid
			}
		}
	}
	if err != nil || validateHiddenDirectPreReceiptDiagnostic(value) != nil {
		return hiddenDirectPreReceiptDiagnostic{}, os.ErrInvalid
	}
	return value, nil
}

func hiddenDirectFileHash(path string) (string, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return "", err
	}
	sum := sha256.Sum256(data)
	return hex.EncodeToString(sum[:]), nil
}

func writeHiddenDirectNativeEvidence(t *testing.T, value hiddenDirectNativeEvidence) {
	t.Helper()
	directory := strings.TrimSpace(os.Getenv("QA_MCP_S4_RECEIPT_DIR"))
	if directory == "" {
		return
	}
	data, err := json.Marshal(value)
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(directory, "native-observation.json"), append(data, '\n'), 0o600); err != nil {
		t.Fatal(err)
	}
}

func observeHiddenDirectInWorker(response hiddenWorkerLifecycleResponse, markerHash string) hiddenDirectWorkerObservation {
	job := windows.Handle(response.WorkerJobHandle)
	member := func(pid uint32) bool { return hiddenDirectProcessInJob(pid, uint64(job)) }
	desktop := os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_DESKTOP")
	expected := hiddenWindowIdentity{PID: response.ListenerPID, ClassName: "V8TopLevelFrameSDI", DesktopHash: hiddenWindowHash(desktop)}
	return observeHiddenDirectInWorkerLoop(markerHash, func() hiddenDirectFencedSample {
		return observeHiddenDirectWindowsFencedSample(response, job, desktop)
	}, expected, member, hiddenDirectObserveUIA, hiddenDirectReportPreReceipt, hiddenDirectWorkerNow, hiddenDirectWorkerSleep, func(string, hiddenDirectMainStatus, hiddenDirectMainStatus, bool, hiddenDirectInventoryCause) {})
}

func TestHiddenDirectWindowsFenceLivenessAndHandleClose(t *testing.T) {
	oldOpen, oldWait, oldClose := hiddenDirectOpenProcess, hiddenDirectWaitProcess, hiddenDirectCloseProcess
	oldInJob, oldPort, oldInventory := hiddenDirectProcessInJob, hiddenDirectListenerForPort, hiddenDirectInventoryIsolation
	defer func() {
		hiddenDirectOpenProcess, hiddenDirectWaitProcess, hiddenDirectCloseProcess = oldOpen, oldWait, oldClose
		hiddenDirectProcessInJob, hiddenDirectListenerForPort, hiddenDirectInventoryIsolation = oldInJob, oldPort, oldInventory
	}()
	response := hiddenWorkerLifecycleResponse{ChildPID: 101, ListenerPID: 102, Port: 15471, WorkerJobHandle: 103}
	hiddenDirectOpenProcess = func(_ uint32, _ bool, pid uint32) (windows.Handle, error) { return windows.Handle(pid), nil }
	hiddenDirectProcessInJob = func(uint32, uint64) bool { return true }
	hiddenDirectListenerForPort = func(uint16) (uint32, bool) { return response.ListenerPID, true }
	inventoryCalls := 0
	hiddenDirectInventoryIsolation = func(string, windows.Handle) (hiddenWindowIsolationReceipt, []hiddenWindowIdentity, hiddenDirectInventoryFailure, error) {
		inventoryCalls++
		return hiddenWindowIsolationReceipt{}, []hiddenWindowIdentity{{HWND: 1}}, "", nil
	}
	for name, configure := range map[string]func(){
		"live": func() {
			hiddenDirectWaitProcess = func(windows.Handle, uint32) (uint32, error) { return uint32(windows.WAIT_TIMEOUT), nil }
			hiddenDirectCloseProcess = func(windows.Handle) error { return nil }
		},
		"exited": func() {
			hiddenDirectWaitProcess = func(windows.Handle, uint32) (uint32, error) { return uint32(windows.WAIT_OBJECT_0), nil }
			hiddenDirectCloseProcess = func(windows.Handle) error { return nil }
		},
		"unknown": func() {
			hiddenDirectWaitProcess = func(windows.Handle, uint32) (uint32, error) { return 99, nil }
			hiddenDirectCloseProcess = func(windows.Handle) error { return nil }
		},
		"handle close failure": func() {
			hiddenDirectWaitProcess = func(windows.Handle, uint32) (uint32, error) { return uint32(windows.WAIT_TIMEOUT), nil }
			hiddenDirectCloseProcess = func(windows.Handle) error { return errors.New("injected close failure") }
		},
	} {
		t.Run(name, func(t *testing.T) {
			inventoryCalls = 0
			configure()
			result := observeHiddenDirectWindowsFencedSample(response, windows.Handle(response.WorkerJobHandle), `Winsta0\qa-mcp-test`)
			if name == "live" {
				if result.Status != hiddenDirectFenceObserved || inventoryCalls != 1 {
					t.Fatalf("live fence rejected: %#v calls=%d", result, inventoryCalls)
				}
			} else if result.Status == hiddenDirectFenceObserved || inventoryCalls != 0 {
				t.Fatalf("hostile fence admitted: %#v calls=%d", result, inventoryCalls)
			}
		})
	}
}

func TestHiddenDirectWorkerExecutesBothConnectedFencedBoundaries(t *testing.T) {
	oldOpen, oldWait, oldClose := hiddenDirectOpenProcess, hiddenDirectWaitProcess, hiddenDirectCloseProcess
	oldInJob, oldPort, oldInventory := hiddenDirectProcessInJob, hiddenDirectListenerForPort, hiddenDirectInventoryIsolation
	oldUIA, oldReport, oldNow, oldSleep := hiddenDirectObserveUIA, hiddenDirectReportPreReceipt, hiddenDirectWorkerNow, hiddenDirectWorkerSleep
	defer func() {
		hiddenDirectOpenProcess, hiddenDirectWaitProcess, hiddenDirectCloseProcess = oldOpen, oldWait, oldClose
		hiddenDirectProcessInJob, hiddenDirectListenerForPort, hiddenDirectInventoryIsolation = oldInJob, oldPort, oldInventory
		hiddenDirectObserveUIA, hiddenDirectReportPreReceipt, hiddenDirectWorkerNow, hiddenDirectWorkerSleep = oldUIA, oldReport, oldNow, oldSleep
	}()
	main, inventory, rows, markerHash, _ := hiddenDirectObservationFixture()
	desktop := `Winsta0\qa-mcp-0123456789abcdef`
	response := hiddenWorkerLifecycleResponse{ChildPID: 4100, ListenerPID: main.PID, Port: 15471, WorkerJobHandle: 77}
	t.Setenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_DESKTOP", desktop)
	openCalls, waitCalls, closeCalls, portCalls := 0, 0, 0, 0
	hiddenDirectOpenProcess = func(_ uint32, _ bool, pid uint32) (windows.Handle, error) {
		openCalls++
		return windows.Handle(pid), nil
	}
	hiddenDirectWaitProcess = func(windows.Handle, uint32) (uint32, error) { waitCalls++; return uint32(windows.WAIT_TIMEOUT), nil }
	hiddenDirectCloseProcess = func(windows.Handle) error { closeCalls++; return nil }
	jobCalls := 0
	hiddenDirectProcessInJob = func(pid uint32, _ uint64) bool {
		jobCalls++
		return pid == response.ChildPID || pid == response.ListenerPID
	}
	hiddenDirectListenerForPort = func(port uint16) (uint32, bool) {
		portCalls++
		return response.ListenerPID, port == uint16(response.Port)
	}
	inventoryCalls, uiaCalls := 0, 0
	hiddenDirectInventoryIsolation = func(current string, job windows.Handle) (hiddenWindowIsolationReceipt, []hiddenWindowIdentity, hiddenDirectInventoryFailure, error) {
		inventoryCalls++
		if current != desktop || job != windows.Handle(response.WorkerJobHandle) {
			return hiddenWindowIsolationReceipt{}, nil, "", os.ErrInvalid
		}
		return hiddenWindowIsolationReceipt{}, append([]hiddenWindowIdentity(nil), inventory...), "", nil
	}
	hiddenDirectObserveUIA = func(hwnd uintptr, pid uint32) ([]hiddenDirectUIARow, error) {
		uiaCalls++
		if hwnd != main.HWND || pid != main.PID {
			return nil, os.ErrInvalid
		}
		return append([]hiddenDirectUIARow(nil), rows...), nil
	}
	var diagnostics []hiddenDirectPreReceiptDiagnostic
	hiddenDirectReportPreReceipt = func(value hiddenDirectPreReceiptDiagnostic) error {
		diagnostics = append(diagnostics, value)
		return validateHiddenDirectPreReceiptDiagnostic(value)
	}
	base := time.Unix(0, 0)
	hiddenDirectWorkerNow = func() time.Time { return base }
	hiddenDirectWorkerSleep = func(time.Duration) {}
	result := observeHiddenDirectInWorker(response, markerHash)
	if result.Status != "passed" || inventoryCalls != 2 || uiaCalls != 2 || openCalls != 8 || waitCalls != 8 || closeCalls != 8 || portCalls != 4 || jobCalls != 12 || len(diagnostics) != 0 || result.Receipt.ActionCount != 0 {
		t.Fatalf("connected boundaries mismatch: result=%#v inventory=%d uia=%d fence=%d/%d/%d/%d job=%d/12 diagnostics=%#v", result, inventoryCalls, uiaCalls, openCalls, waitCalls, closeCalls, portCalls, jobCalls, diagnostics)
	}
}

func TestHiddenDirectWorkerReportsBothConnectedFenceRefusals(t *testing.T) {
	for _, test := range []struct {
		name, stage, status string
		refuseAt            int
		reporterFails       bool
		wantUIA             int
	}{
		{name: "first boundary", stage: "first_window_inventory", status: "window_inventory_failed", refuseAt: 1},
		{name: "first boundary reporter failure", stage: "first_window_inventory", status: "pre_receipt_diagnostic_failed", refuseAt: 1, reporterFails: true},
		{name: "second boundary", stage: "second_window_inventory", status: "second_window_inventory_failed", refuseAt: 2, wantUIA: 1},
		{name: "second boundary reporter failure", stage: "second_window_inventory", status: "pre_receipt_diagnostic_failed", refuseAt: 2, reporterFails: true, wantUIA: 1},
	} {
		t.Run(test.name, func(t *testing.T) {
			oldOpen, oldWait, oldClose := hiddenDirectOpenProcess, hiddenDirectWaitProcess, hiddenDirectCloseProcess
			oldInJob, oldPort, oldInventory := hiddenDirectProcessInJob, hiddenDirectListenerForPort, hiddenDirectInventoryIsolation
			oldUIA, oldReport, oldNow, oldSleep := hiddenDirectObserveUIA, hiddenDirectReportPreReceipt, hiddenDirectWorkerNow, hiddenDirectWorkerSleep
			defer func() {
				hiddenDirectOpenProcess, hiddenDirectWaitProcess, hiddenDirectCloseProcess = oldOpen, oldWait, oldClose
				hiddenDirectProcessInJob, hiddenDirectListenerForPort, hiddenDirectInventoryIsolation = oldInJob, oldPort, oldInventory
				hiddenDirectObserveUIA, hiddenDirectReportPreReceipt, hiddenDirectWorkerNow, hiddenDirectWorkerSleep = oldUIA, oldReport, oldNow, oldSleep
			}()
			main, inventory, rows, markerHash, _ := hiddenDirectObservationFixture()
			desktop := `Winsta0\qa-mcp-0123456789abcdef`
			response := hiddenWorkerLifecycleResponse{ChildPID: 4100, ListenerPID: main.PID, Port: 15471, WorkerJobHandle: 77}
			t.Setenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_DESKTOP", desktop)
			openCalls, waitCalls, closeCalls, portCalls := 0, 0, 0, 0
			hiddenDirectOpenProcess = func(_ uint32, _ bool, pid uint32) (windows.Handle, error) {
				openCalls++
				return windows.Handle(pid), nil
			}
			hiddenDirectWaitProcess = func(windows.Handle, uint32) (uint32, error) { waitCalls++; return uint32(windows.WAIT_TIMEOUT), nil }
			hiddenDirectCloseProcess = func(windows.Handle) error { closeCalls++; return nil }
			hiddenDirectProcessInJob = func(pid uint32, _ uint64) bool { return pid == response.ChildPID || pid == response.ListenerPID }
			hiddenDirectListenerForPort = func(port uint16) (uint32, bool) {
				portCalls++
				return response.ListenerPID, port == uint16(response.Port)
			}
			inventoryCalls, uiaCalls := 0, 0
			hiddenDirectInventoryIsolation = func(current string, job windows.Handle) (hiddenWindowIsolationReceipt, []hiddenWindowIdentity, hiddenDirectInventoryFailure, error) {
				inventoryCalls++
				if current != desktop || job != windows.Handle(response.WorkerJobHandle) {
					return hiddenWindowIsolationReceipt{}, nil, "", os.ErrInvalid
				}
				if inventoryCalls == test.refuseAt {
					return hiddenWindowIsolationReceipt{}, nil, hiddenDirectInventoryFailureHiddenOpen, errors.New("injected inventory refusal")
				}
				return hiddenWindowIsolationReceipt{}, append([]hiddenWindowIdentity(nil), inventory...), "", nil
			}
			hiddenDirectObserveUIA = func(hwnd uintptr, pid uint32) ([]hiddenDirectUIARow, error) {
				uiaCalls++
				if hwnd != main.HWND || pid != main.PID {
					return nil, os.ErrInvalid
				}
				return append([]hiddenDirectUIARow(nil), rows...), nil
			}
			var diagnostics []hiddenDirectPreReceiptDiagnostic
			hiddenDirectReportPreReceipt = func(value hiddenDirectPreReceiptDiagnostic) error {
				diagnostics = append(diagnostics, value)
				if test.reporterFails {
					return errors.New("injected diagnostic refusal")
				}
				return validateHiddenDirectPreReceiptDiagnostic(value)
			}
			base := time.Unix(0, 0)
			hiddenDirectWorkerNow = func() time.Time { return base }
			hiddenDirectWorkerSleep = func(time.Duration) {}
			result := observeHiddenDirectInWorker(response, markerHash)
			wantFenceCalls, wantPortCalls := test.refuseAt*4, test.refuseAt*2
			wantDiagnostic := hiddenDirectPreReceiptDiagnosticFor(test.stage)
			if result.Status != test.status || inventoryCalls != test.refuseAt || uiaCalls != test.wantUIA || openCalls != wantFenceCalls || waitCalls != wantFenceCalls || closeCalls != wantFenceCalls || portCalls != wantPortCalls || len(diagnostics) != 1 || diagnostics[0] != wantDiagnostic || result.Receipt.ActionCount != 0 {
				t.Fatalf("connected refusal mismatch: result=%#v inventory=%d uia=%d fence=%d/%d/%d/%d diagnostics=%#v", result, inventoryCalls, uiaCalls, openCalls, waitCalls, closeCalls, portCalls, diagnostics)
			}
		})
	}
}

func TestHiddenDirectPreReceiptDiagnosticFileRejectsMalformed(t *testing.T) {
	path := filepath.Join(t.TempDir(), "pre-receipt.json")
	want := hiddenDirectPreReceiptDiagnosticFor("first_window_inventory")
	if err := writeHiddenDirectPreReceiptDiagnostic(path, want); err != nil {
		t.Fatal(err)
	}
	got, err := readHiddenDirectPreReceiptDiagnostic(path)
	if err != nil || got != want {
		t.Fatalf("diagnostic round trip failed: %#v %v", got, err)
	}
	encoded, err := json.Marshal(want)
	if err != nil {
		t.Fatal(err)
	}
	for name, hostile := range map[string]any{
		"raw_error": "private failure", "endpoint": "private endpoint", "desktop": "private desktop",
		"handle": uint64(77), "pid": uint32(88), "port": 15471, "ui_value": "private UI", "dynamic_identity": "private identity",
	} {
		t.Run(name, func(t *testing.T) {
			var value map[string]any
			if err := json.Unmarshal(encoded, &value); err != nil {
				t.Fatal(err)
			}
			value[name] = hostile
			data, err := json.Marshal(value)
			if err != nil {
				t.Fatal(err)
			}
			if err = os.WriteFile(path, data, 0o600); err != nil {
				t.Fatal(err)
			}
			if got, err = readHiddenDirectPreReceiptDiagnostic(path); err == nil || got != (hiddenDirectPreReceiptDiagnostic{}) {
				t.Fatalf("hostile diagnostic admitted: %#v %v", got, err)
			}
		})
	}
	if err = os.WriteFile(path, append(encoded, []byte(` {}`)...), 0o600); err != nil {
		t.Fatal(err)
	}
	if got, err = readHiddenDirectPreReceiptDiagnostic(path); err == nil || got != (hiddenDirectPreReceiptDiagnostic{}) {
		t.Fatalf("trailing diagnostic admitted: %#v %v", got, err)
	}
}

func TestHiddenDirectObservationWorker(t *testing.T) {
	if os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_MODE") != "worker" {
		t.Skip("internal S4 hidden worker")
	}
	output, markerHash := os.Getenv("QA_MCP_S4_WORKER_OBSERVATION"), os.Getenv("QA_MCP_S4_MARKER_SHA256")
	if !filepath.IsAbs(output) || !validHiddenWindowHash(markerHash) {
		t.Fatal("S4 worker observation identity is invalid")
	}
	hiddenWorkerPublishResponse = func(path string, data []byte) error {
		return publishHiddenWorkerResponse(path, data)
	}
	hiddenDirectReportPreReceipt = func(value hiddenDirectPreReceiptDiagnostic) error {
		return writeHiddenDirectPreReceiptDiagnostic(output+".pre-receipt.json", value)
	}
	hiddenWorkerTransferredObserver = func(response hiddenWorkerLifecycleResponse, job windows.Handle) error {
		if response.WorkerPID != uint32(os.Getpid()) || response.WorkerJobHandle != uint64(job) {
			return os.ErrInvalid
		}
		result := observeHiddenDirectInWorker(response, markerHash)
		encoded, _ := json.Marshal(result)
		return os.WriteFile(output, append(encoded, '\n'), 0o600)
	}
	if err := runHiddenWorkerLifecycleWorker(); err != nil {
		t.Fatal(err)
	}
}

func TestHiddenDirectObservationNative(t *testing.T) {
	platform := strings.TrimSpace(os.Getenv("QA_MCP_S4_PLATFORM_EXE"))
	target := strings.TrimSpace(os.Getenv("QA_MCP_S4_TARGET"))
	executePath := strings.TrimSpace(os.Getenv("QA_MCP_S4_EPF"))
	markerHash := strings.TrimSpace(os.Getenv("QA_MCP_S4_MARKER_SHA256"))
	if platform == "" || target == "" || executePath == "" || markerHash == "" {
		t.Skip("exact ignored S4 Windows inputs are unavailable")
	}
	if !filepath.IsAbs(platform) || !filepath.IsAbs(target) || !filepath.IsAbs(executePath) ||
		!strings.Contains(strings.ToLower(platform), `\8.3.27.2214\`) || !strings.EqualFold(filepath.Clean(target), `C:\1C_BASES\vanessa_client`) || !validHiddenWindowHash(markerHash) {
		t.Fatal("exact S4 platform, target, execute path or marker identity is invalid")
	}
	identity, err := newHiddenDesktopProcessIdentity("s4-native-"+strconv.FormatInt(time.Now().UnixNano(), 10), "s4-native-token")
	if err != nil {
		t.Fatal(err)
	}
	port := freeHiddenWorkerPort(t)
	args := []string{"ENTERPRISE", "/F" + target}
	if user := os.Getenv("QA_MCP_S4_USER"); user != "" {
		args = append(args, "/N"+user)
	}
	if password := os.Getenv("QA_MCP_S4_PASSWORD"); password != "" {
		args = append(args, "/P"+password)
	}
	args = append(args, "/AppAutoCheckVersion-", "/TESTCLIENT", "-TPort", strconv.Itoa(port), "/Execute", executePath, "/DisableStartupDialogs", "/DisableStartupMessages")
	observationFile, err := os.CreateTemp("", "qa-mcp-s4-worker-observation-*.json")
	if err != nil {
		t.Fatal(err)
	}
	observationPath := observationFile.Name()
	observationFile.Close()
	os.Remove(observationPath)
	defer os.Remove(observationPath)
	defer os.Remove(observationPath + ".pre-receipt.json")
	environment := append(os.Environ(), "QA_MCP_S4_WORKER_OBSERVATION="+observationPath, "QA_MCP_S4_MARKER_SHA256="+markerHash)
	request := hiddenWorkerLifecycleRequest{Identity: identity, WorkerToken: "s4-native-token", WorkerArgs: []string{"-test.run=^TestHiddenDirectObservationWorker$", "-test.count=1"}, ChildExecutable: platform, ChildArgs: args, Environment: environment, Port: port, Timeout: 90 * time.Second}
	lifecycle, err := startHiddenWorkerLifecycle(context.Background(), request)
	if err != nil {
		t.Fatal(err)
	}
	defer lifecycle.Close()
	response, job, responsePath := lifecycle.Response, lifecycle.job, lifecycle.responsePath
	deadline := time.Now().Add(65 * time.Second)
	var workerObservation hiddenDirectWorkerObservation
	for time.Now().Before(deadline) {
		data, readErr := os.ReadFile(observationPath)
		if readErr == nil && json.Unmarshal(data, &workerObservation) == nil {
			break
		}
		time.Sleep(100 * time.Millisecond)
	}
	receipt, isolation := workerObservation.Receipt, workerObservation.Isolation
	if workerObservation.Status != "passed" || validateHiddenDirectObservationReceipt(receipt) != nil || isolation.JobOwnedOperatorWindowCount != 0 || receipt.ActionCount != 0 {
		t.Fatalf("exact passive direct-execute observation failed: %s", workerObservation.Status)
	}
	candidateHash, hashErr := hiddenDirectFileHash(os.Args[0])
	if hashErr != nil {
		t.Fatal(hashErr)
	}
	if err := lifecycle.Close(); err != nil {
		t.Fatal(err)
	}
	assertHiddenWorkerResourcesGone(t, request, response.WorkerPID, response.ChildPID, response.ListenerPID, job, responsePath)
	writeHiddenDirectNativeEvidence(t, hiddenDirectNativeEvidence{
		Schema: "qa-mcp.s4-native-observation.v1", Status: "passed", CandidateSHA256: candidateHash, PlatformVersion: "8.3.27.2214",
		TargetHash: hiddenWindowHash(strings.ToLower(filepath.Clean(target))), ExecuteHash: hiddenWindowHash(strings.ToLower(filepath.Clean(executePath))),
		Receipt: receipt, Isolation: isolation, WorkerPID: response.WorkerPID, ChildPID: response.ChildPID, ListenerPID: response.ListenerPID, CleanupComplete: true,
	})
}
