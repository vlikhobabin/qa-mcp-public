//go:build windows

package main

import (
	"context"
	"crypto/sha256"
	"encoding/hex"
	"encoding/json"
	"errors"
	"os"
	"path/filepath"
	"sort"
	"strconv"
	"strings"
	"testing"
	"time"

	"golang.org/x/sys/windows"
)

func hiddenDirectInvestigationHash(values []string) string {
	copyOfValues := append([]string(nil), values...)
	sort.Strings(copyOfValues)
	sum := sha256.Sum256([]byte(strings.Join(copyOfValues, "\x00")))
	return hex.EncodeToString(sum[:])
}

func hiddenDirectInvestigationProcessState(pid uint32) (bool, bool, int32) {
	handle, err := windows.OpenProcess(windows.PROCESS_QUERY_LIMITED_INFORMATION, false, pid)
	if err != nil {
		return false, true, -1
	}
	defer windows.CloseHandle(handle)
	var code uint32
	if windows.GetExitCodeProcess(handle, &code) != nil {
		return false, false, 0
	}
	if code == 259 {
		return true, false, 0
	}
	return false, true, int32(code)
}

func collectHiddenDirectInvestigation(response hiddenWorkerLifecycleResponse) ([]hiddenDirectInvestigationSample, hiddenDirectInvestigationTerminal) {
	started := time.Now()
	job := windows.Handle(response.WorkerJobHandle)
	desktop := os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_DESKTOP")
	member := func(pid uint32) bool { return hiddenWorkerPIDInJob(pid, uint64(job)) }
	samples := make([]hiddenDirectInvestigationSample, 0, hiddenDirectInvestigationSampleLimit)
	for index := 0; index < hiddenDirectInvestigationSampleLimit; index++ {
		alive, exited, exitCode := hiddenDirectInvestigationProcessState(response.ChildPID)
		windowsOnDesktop, inventoryErr := hiddenWindowInventoryOnDesktop(desktop)
		classes, ownerRelation, mainAdmitted := make(map[string]bool), "", false
		jobWindowCount := 0
		for _, item := range windowsOnDesktop {
			if member(item.PID) {
				jobWindowCount++
			}
			if item.ClassName == "V8TopLevelFrameSDI" || item.ClassName == "V8TopLevelFrameSDIsec" || item.ClassName == "V8ConfirmationWindowTaxi" {
				classes[item.ClassName] = true
				if item.OwnerHWND == 0 {
					ownerRelation = "root"
				} else {
					ownerRelation = "owned"
				}
			}
			mainAdmitted = mainAdmitted || (item.ClassName == "V8TopLevelFrameSDI" && item.OwnerHWND == 0 && member(item.PID))
		}
		allowlisted := make([]string, 0, len(classes))
		for className := range classes {
			allowlisted = append(allowlisted, className)
		}
		sort.Strings(allowlisted)
		enumerationError := ""
		if inventoryErr != nil {
			if errors.Is(inventoryErr, windows.ERROR_INVALID_DATA) {
				enumerationError = "ERROR_INVALID_DATA"
			} else {
				enumerationError = "ERROR_OTHER"
			}
		}
		stage := "window_inventory"
		if index == 0 {
			stage = "listener_ready"
		}
		if mainAdmitted {
			stage = "main_window"
		}
		if exited {
			stage = "child_exit"
		}
		samples = append(samples, hiddenDirectInvestigationSample{
			OffsetMilliseconds: uint32(time.Since(started).Milliseconds()), Stage: stage,
			ProcessPID: response.ChildPID, ListenerPID: response.ListenerPID,
			ProcessAlive: alive, ProcessInJob: member(response.ChildPID), ListenerReady: response.ListenerPID != 0,
			DesktopHash: hiddenWindowHash(desktop), TopLevelWindowCount: uint16(jobWindowCount),
			AllowlistedClasses: allowlisted, OwnerRelation: ownerRelation, EnumerationError: enumerationError,
		})
		if mainAdmitted {
			return samples, hiddenDirectInvestigationTerminal{Status: "main_admitted", MainAdmitted: true}
		}
		if exited {
			return samples, hiddenDirectInvestigationTerminal{Status: "process_exited", ProcessExited: true, ExitCodeKnown: true, ExitCode: exitCode}
		}
		time.Sleep(time.Second)
	}
	return samples, hiddenDirectInvestigationTerminal{Status: "main_not_ready"}
}

func TestHiddenDirectInvestigationWorker(t *testing.T) {
	if os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_MODE") != "worker" {
		t.Skip("internal investigation worker")
	}
	hiddenWorkerPublishResponse = func(path string, data []byte) error {
		if err := publishHiddenWorkerResponse(path, data); err != nil {
			return err
		}
		var response hiddenWorkerLifecycleResponse
		if json.Unmarshal(data, &response) != nil {
			return os.ErrInvalid
		}
		samples, terminal := collectHiddenDirectInvestigation(response)
		encoded, _ := json.Marshal(struct {
			Samples  []hiddenDirectInvestigationSample `json:"samples"`
			Terminal hiddenDirectInvestigationTerminal `json:"terminal"`
		}{samples, terminal})
		return os.WriteFile(path+".investigation.json", append(encoded, '\n'), 0o600)
	}
	if err := runHiddenWorkerLifecycleWorker(); err != nil {
		t.Fatal(err)
	}
}

func TestHiddenDirectInvestigationNative(t *testing.T) {
	platform := strings.TrimSpace(os.Getenv("QA_MCP_I1_PLATFORM_EXE"))
	target := strings.TrimSpace(os.Getenv("QA_MCP_I1_TARGET"))
	executePath := strings.TrimSpace(os.Getenv("QA_MCP_I1_EPF"))
	runKind := strings.TrimSpace(os.Getenv("QA_MCP_I1_RUN_KIND"))
	output := strings.TrimSpace(os.Getenv("QA_MCP_I1_RECEIPT"))
	if platform == "" || target == "" || runKind == "" || output == "" {
		t.Skip("exact investigation inputs are unavailable")
	}
	if !filepath.IsAbs(platform) || !filepath.IsAbs(target) || !filepath.IsAbs(output) ||
		!strings.Contains(strings.ToLower(platform), `\8.3.27.2214\`) || !strings.EqualFold(filepath.Clean(target), `C:\1C_BASES\vanessa_client`) ||
		(runKind != "s3-control" && runKind != "s4-diagnostic") || (runKind == "s4-diagnostic" && !filepath.IsAbs(executePath)) {
		t.Fatal("exact investigation identity is invalid")
	}
	identity, err := newHiddenDesktopProcessIdentity("s7-i1-"+strconv.FormatInt(time.Now().UnixNano(), 10), "s7-i1-token")
	if err != nil {
		t.Fatal(err)
	}
	port := freeHiddenWorkerPort(t)
	args := []string{"ENTERPRISE", "/F" + target}
	if user := os.Getenv("QA_MCP_I1_USER"); user != "" {
		args = append(args, "/N"+user)
	}
	args = append(args, "/AppAutoCheckVersion-", "/TESTCLIENT", "-TPort", strconv.Itoa(port))
	if runKind == "s4-diagnostic" {
		args = append(args, "/Execute", executePath)
	}
	args = append(args, "/DisableStartupDialogs", "/DisableStartupMessages")
	request := hiddenWorkerLifecycleRequest{Identity: identity, WorkerToken: "s7-i1-token", WorkerArgs: []string{"-test.run=^TestHiddenDirectInvestigationWorker$", "-test.count=1"}, ChildExecutable: platform, ChildArgs: args, Environment: os.Environ(), Port: port, Timeout: 90 * time.Second}
	lifecycle, err := startHiddenWorkerLifecycle(context.Background(), request)
	if err != nil {
		t.Fatal(err)
	}
	response, job, responsePath := lifecycle.Response, lifecycle.job, lifecycle.responsePath
	timelinePath := responsePath + ".investigation.json"
	defer os.Remove(timelinePath)
	var payload struct {
		Samples  []hiddenDirectInvestigationSample `json:"samples"`
		Terminal hiddenDirectInvestigationTerminal `json:"terminal"`
	}
	deadline := time.Now().Add(70 * time.Second)
	for time.Now().Before(deadline) {
		data, readErr := os.ReadFile(timelinePath)
		if readErr == nil && json.Unmarshal(data, &payload) == nil {
			break
		}
		time.Sleep(100 * time.Millisecond)
	}
	if len(payload.Samples) == 0 {
		t.Fatal("investigation timeline is unavailable")
	}
	if err := lifecycle.Close(); err != nil {
		t.Fatal(err)
	}
	assertHiddenWorkerResourcesGone(t, request, response.WorkerPID, response.ChildPID, response.ListenerPID, job, responsePath)
	fixtureHash := hiddenDirectInvestigationHash(nil)
	if runKind == "s4-diagnostic" {
		fixtureHash, err = hiddenDirectFileHash(executePath)
		if err != nil {
			t.Fatal(err)
		}
	}
	receipt := hiddenDirectInvestigationReceipt{
		Schema: hiddenDirectInvestigationSchema, RunKind: runKind,
		ArgvSHA256: hiddenDirectInvestigationHash(args), EnvironmentHash: hiddenDirectInvestigationHash(os.Environ()), FixtureSHA256: fixtureHash,
		Samples: payload.Samples, Terminal: payload.Terminal,
		Cleanup: hiddenDirectInvestigationCleanup{Complete: true, ProtectedStateUnchanged: true},
	}
	if err := validateHiddenDirectInvestigationReceipt(receipt); err != nil {
		t.Fatal(err)
	}
	encoded, _ := json.Marshal(receipt)
	if err := os.WriteFile(output, append(encoded, '\n'), 0o600); err != nil {
		t.Fatal(err)
	}
}
