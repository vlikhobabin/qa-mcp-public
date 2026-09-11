//go:build windows

package main

import (
	"context"
	"encoding/json"
	"net"
	"os"
	"path/filepath"
	"strconv"
	"strings"
	"testing"
	"time"
	"unsafe"

	"golang.org/x/sys/windows"
)

var (
	hiddenWindowTestCreate  = windows.NewLazySystemDLL("user32.dll").NewProc("CreateWindowExW")
	hiddenWindowTestDestroy = windows.NewLazySystemDLL("user32.dll").NewProc("DestroyWindow")
)

type hiddenWindowNativeEvidence struct {
	Receipt         hiddenWindowIsolationReceipt `json:"receipt"`
	CleanupComplete bool                         `json:"cleanup_complete"`
}

func writeHiddenWindowNativeEvidence(t *testing.T, name string, receipt hiddenWindowIsolationReceipt) {
	t.Helper()
	directory := os.Getenv("QA_MCP_S3_RECEIPT_DIR")
	if directory == "" {
		return
	}
	data, err := json.Marshal(hiddenWindowNativeEvidence{Receipt: receipt, CleanupComplete: true})
	if err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(filepath.Join(directory, name+".json"), data, 0o600); err != nil {
		t.Fatal(err)
	}
}

func TestHiddenWindowIsolationNativeHelper(t *testing.T) {
	if os.Getenv("QA_MCP_S3_TEST_MODE") != "synthetic-child" {
		t.Skip("internal S3 helper")
	}
	port, err := strconv.Atoi(os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_PORT"))
	if err != nil {
		t.Fatal(err)
	}
	class, _ := windows.UTF16PtrFromString("Static")
	root, _, callErr := hiddenWindowTestCreate.Call(0, uintptr(unsafe.Pointer(class)), 0, 0x00cf0000, 0, 0, 100, 100, 0, 0, 0, 0)
	if root == 0 {
		t.Fatalf("synthetic root failed: %v", callErr)
	}
	defer hiddenWindowTestDestroy.Call(root)
	popup, _, callErr := hiddenWindowTestCreate.Call(0, uintptr(unsafe.Pointer(class)), 0, 0x80000000, 0, 0, 50, 50, root, 0, 0, 0)
	if popup == 0 {
		t.Fatalf("synthetic popup failed: %v", callErr)
	}
	defer hiddenWindowTestDestroy.Call(popup)
	listener, err := net.Listen("tcp4", "127.0.0.1:"+strconv.Itoa(port))
	if err != nil {
		t.Fatal(err)
	}
	defer listener.Close()
	time.Sleep(30 * time.Second)
}

func hiddenWindowNativeRequest(t *testing.T, childExecutable string, childArgs, environment []string, timeout time.Duration) hiddenWorkerLifecycleRequest {
	t.Helper()
	identity, err := newHiddenDesktopProcessIdentity("s3-native-"+strconv.FormatInt(time.Now().UnixNano(), 10), "s3-native-token")
	if err != nil {
		t.Fatal(err)
	}
	return hiddenWorkerLifecycleRequest{Identity: identity, WorkerToken: "s3-native-token", WorkerArgs: []string{"-test.run=^TestHiddenWorkerLifecycleNativeHelper$", "-test.count=1"}, ChildExecutable: childExecutable, ChildArgs: childArgs, Environment: environment, Port: freeHiddenWorkerPort(t), Timeout: timeout}
}

func TestHiddenWindowIsolationSyntheticNative(t *testing.T) {
	executable, err := os.Executable()
	if err != nil {
		t.Fatal(err)
	}
	environment := append(os.Environ(), "QA_MCP_S3_TEST_MODE=synthetic-child")
	request := hiddenWindowNativeRequest(t, executable, []string{"-test.run=^TestHiddenWindowIsolationNativeHelper$", "-test.count=1"}, environment, 15*time.Second)
	lifecycle, err := startHiddenWorkerLifecycle(context.Background(), request)
	if err != nil {
		t.Fatal(err)
	}
	defer lifecycle.Close()
	response, job, path := lifecycle.Response, lifecycle.job, lifecycle.responsePath
	receipt, inventory, err := inventoryHiddenWindowIsolation(request.Identity.Desktop, lifecycle.job)
	if err != nil || receipt.JobOwnedHiddenWindowCount < 2 || receipt.JobOwnedOperatorWindowCount != 0 || receipt.GlobalInputCalls != 0 || receipt.DesktopSwitchCalls != 0 {
		t.Fatalf("synthetic isolation failed: %#v %v", receipt, err)
	}
	member := func(pid uint32) bool { return hiddenWorkerPIDInJob(pid, uint64(lifecycle.job)) }
	root, err := admitExactHiddenWindow(inventory, hiddenWindowHash(request.Identity.Desktop), response.ListenerPID, "Static", 0, member)
	if err != nil {
		t.Fatal(err)
	}
	popup, err := admitExactHiddenWindow(inventory, hiddenWindowHash(request.Identity.Desktop), response.ListenerPID, "static", root.HWND, member)
	if err != nil || popup.OwnerHWND != root.HWND {
		t.Fatalf("synthetic owner topology failed: %#v %v", popup, err)
	}
	if err := lifecycle.Close(); err != nil {
		t.Fatal(err)
	}
	assertHiddenWorkerResourcesGone(t, request, response.WorkerPID, response.ChildPID, response.ListenerPID, job, path)
	writeHiddenWindowNativeEvidence(t, "synthetic", receipt)
}

func TestHiddenWindowIsolationRealTestClientNative(t *testing.T) {
	platform, target := strings.TrimSpace(os.Getenv("QA_MCP_S3_PLATFORM_EXE")), strings.TrimSpace(os.Getenv("QA_MCP_S3_TARGET"))
	if platform == "" || target == "" {
		t.Skip("exact ignored Windows target is unavailable")
	}
	if !filepath.IsAbs(platform) || !filepath.IsAbs(target) || !strings.Contains(strings.ToLower(platform), `\8.3.27.2214\`) || !strings.EqualFold(filepath.Clean(target), `C:\1C_BASES\vanessa_client`) {
		t.Fatal("exact platform or target identity mismatch")
	}
	args := []string{"ENTERPRISE", "/F" + target}
	if user := os.Getenv("QA_MCP_S3_USER"); user != "" {
		args = append(args, "/N"+user)
	}
	if password := os.Getenv("QA_MCP_S3_PASSWORD"); password != "" {
		args = append(args, "/P"+password)
	}
	args = append(args, "/AppAutoCheckVersion-", "/TESTCLIENT", "-TPort", "0", "/DisableStartupDialogs", "/DisableStartupMessages")
	request := hiddenWindowNativeRequest(t, platform, args, os.Environ(), 90*time.Second)
	for index := range request.ChildArgs {
		if index > 0 && request.ChildArgs[index-1] == "-TPort" {
			request.ChildArgs[index] = strconv.Itoa(request.Port)
		}
	}
	lifecycle, err := startHiddenWorkerLifecycle(context.Background(), request)
	if err != nil {
		t.Fatal(err)
	}
	defer lifecycle.Close()
	response, job, path := lifecycle.Response, lifecycle.job, lifecycle.responsePath
	receipt, inventory, err := inventoryHiddenWindowIsolation(request.Identity.Desktop, lifecycle.job)
	if err != nil || len(inventory) == 0 || receipt.JobOwnedHiddenWindowCount == 0 || receipt.JobOwnedOperatorWindowCount != 0 || len(receipt.ClassHashes) == 0 || receipt.GlobalInputCalls != 0 || receipt.DesktopSwitchCalls != 0 {
		t.Fatalf("real TestClient isolation failed: counts=%d/%d hashes=%d %v", receipt.JobOwnedHiddenWindowCount, receipt.JobOwnedOperatorWindowCount, len(receipt.ClassHashes), err)
	}
	if err := lifecycle.Close(); err != nil {
		t.Fatal(err)
	}
	assertHiddenWorkerResourcesGone(t, request, response.WorkerPID, response.ChildPID, response.ListenerPID, job, path)
	writeHiddenWindowNativeEvidence(t, "real-testclient", receipt)
}
