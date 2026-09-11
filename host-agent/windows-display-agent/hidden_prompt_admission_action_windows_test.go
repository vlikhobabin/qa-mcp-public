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
	"strconv"
	"strings"
	"testing"
	"time"

	"golang.org/x/sys/windows"
)

type hiddenPromptS5WorkerResult struct {
	Status     string                            `json:"status"`
	Diagnostic string                            `json:"diagnostic,omitempty"`
	Inventory  hiddenPromptS5InventoryDiagnostic `json:"inventory"`
	Receipt    hiddenPromptS5Receipt             `json:"receipt"`
	Isolation  hiddenWindowIsolationReceipt      `json:"isolation"`
}

type hiddenPromptS5NativeEvidence struct {
	Schema, Status, CandidateSHA256, PlatformVersion string
	TargetHash                                       string
	ExecuteHashes                                    []string
	Receipts                                         []hiddenPromptS5Receipt
	Inventories                                      []hiddenPromptS5InventoryDiagnostic
	Isolation                                        []hiddenWindowIsolationReceipt
	Runs, AddressedConfirmations, AddressedMessages  int
	CleanupComplete, RawUIRetained                   bool
}

func hiddenPromptS5FreshEPFs() ([]string, error) {
	paths := []string{
		strings.TrimSpace(os.Getenv("QA_MCP_S5_EPF_RUN1")),
		strings.TrimSpace(os.Getenv("QA_MCP_S5_EPF_RUN2")),
	}
	if paths[0] == "" && paths[1] == "" {
		return nil, nil
	}
	if paths[0] == "" || paths[1] == "" {
		return nil, errors.New("two fresh EPF inputs are required")
	}
	hashes := make(map[string]struct{}, len(paths))
	for index, path := range paths {
		path = filepath.Clean(path)
		if !filepath.IsAbs(path) || !strings.EqualFold(filepath.Ext(path), ".epf") {
			return nil, errors.New("fresh EPF identity is invalid")
		}
		data, err := os.ReadFile(path)
		if err != nil {
			return nil, err
		}
		sum := sha256.Sum256(data)
		hash := hex.EncodeToString(sum[:])
		if _, exists := hashes[hash]; exists {
			return nil, errors.New("fresh EPF content is duplicated")
		}
		hashes[hash] = struct{}{}
		paths[index] = path
	}
	if strings.EqualFold(paths[0], paths[1]) {
		return nil, errors.New("fresh EPF path is duplicated")
	}
	return paths, nil
}

func hiddenPromptS5Post(main, prompt hiddenWindowIdentity, desktop string, job windows.Handle, markerHash string) func() (hiddenPromptS5PostState, error) {
	member := func(pid uint32) bool { return hiddenWorkerPIDInJob(pid, uint64(job)) }
	return func() (hiddenPromptS5PostState, error) {
		deadline := time.Now().Add(30 * time.Second)
		for time.Now().Before(deadline) {
			isolation, firstWindows, err := inventoryHiddenWindowIsolation(desktop, job)
			if err != nil {
				return hiddenPromptS5PostState{}, err
			}
			prompts := make([]hiddenWindowIdentity, 0, 1)
			for _, item := range firstWindows {
				if strings.EqualFold(item.ClassName, hiddenPromptS5Class) {
					prompts = append(prompts, item)
				}
			}
			if len(prompts) != 0 {
				if len(prompts) != 1 || prompts[0] != prompt {
					return hiddenPromptS5PostState{}, errors.New("security prompt was replaced")
				}
				time.Sleep(100 * time.Millisecond)
				continue
			}
			firstRows, err := observeHiddenDirectAfterReadmission(main, firstWindows, member, observeHiddenDirectUIA)
			if err != nil {
				time.Sleep(100 * time.Millisecond)
				continue
			}
			time.Sleep(250 * time.Millisecond)
			_, secondWindows, err := inventoryHiddenWindowIsolation(desktop, job)
			if err != nil {
				return hiddenPromptS5PostState{}, err
			}
			secondRows, err := observeHiddenDirectAfterReadmission(main, secondWindows, member, observeHiddenDirectUIA)
			if err != nil {
				time.Sleep(100 * time.Millisecond)
				continue
			}
			observation, err := admitHiddenDirectObservation(main, firstWindows, secondWindows, markerHash, firstRows, secondRows, member)
			if err == nil {
				return hiddenPromptS5PostState{Observation: observation, OperatorWindowCount: isolation.JobOwnedOperatorWindowCount}, nil
			}
			time.Sleep(100 * time.Millisecond)
		}
		return hiddenPromptS5PostState{}, errors.New("exact S4 post-state was not observed")
	}
}

func observeAndConfirmHiddenPromptS5(response hiddenWorkerLifecycleResponse, markerHash string) hiddenPromptS5WorkerResult {
	job, desktop := windows.Handle(response.WorkerJobHandle), os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_DESKTOP")
	member := func(pid uint32) bool { return hiddenWorkerPIDInJob(pid, uint64(job)) }
	deadline := time.Now().Add(60 * time.Second)
	var lastInventory hiddenPromptS5InventoryDiagnostic
	lastStatus, diagnostic := "main_not_ready", ""
	for time.Now().Before(deadline) {
		isolation, firstWindows, err := inventoryHiddenWindowIsolation(desktop, job)
		if err != nil {
			return hiddenPromptS5WorkerResult{Status: "window_inventory_failed"}
		}
		main, err := admitExactHiddenWindow(firstWindows, hiddenWindowHash(desktop), response.ListenerPID, "V8TopLevelFrameSDI", 0, member)
		if err != nil {
			lastStatus = "main_not_ready"
			time.Sleep(100 * time.Millisecond)
			continue
		}
		prompt, err := admitExactHiddenWindow(firstWindows, hiddenWindowHash(desktop), response.ListenerPID, hiddenPromptS5Class, main.HWND, member)
		if err != nil {
			lastStatus = "prompt_not_ready"
			time.Sleep(100 * time.Millisecond)
			continue
		}
		pattern, controls, inventory, err := observeHiddenPromptS5Controls(prompt)
		lastInventory = inventory
		if err != nil {
			lastStatus, diagnostic = "prompt_inventory_not_ready", "inventory_invalid"
			time.Sleep(100 * time.Millisecond)
			continue
		}
		first := hiddenPromptS5Snapshot{Main: main, Prompt: prompt, StableSamples: 2, CandidateCount: 1, NewAfterLaunch: true, PatternHash: pattern, Controls: controls}
		time.Sleep(250 * time.Millisecond)
		_, secondWindows, err := inventoryHiddenWindowIsolation(desktop, job)
		if err != nil {
			return hiddenPromptS5WorkerResult{Status: "window_readmission_failed"}
		}
		secondMain, mainErr := admitHiddenDirectMainWindow(secondWindows, main, member)
		secondPrompt, promptErr := admitExactHiddenWindow(secondWindows, hiddenWindowHash(desktop), response.ListenerPID, hiddenPromptS5Class, main.HWND, member)
		secondPattern, secondControls, secondInventory, controlErr := observeHiddenPromptS5Controls(secondPrompt)
		if mainErr != nil || promptErr != nil || controlErr != nil {
			return hiddenPromptS5WorkerResult{Status: "prompt_readmission_failed", Inventory: secondInventory}
		}
		second := hiddenPromptS5Snapshot{Main: secondMain, Prompt: secondPrompt, StableSamples: 2, CandidateCount: 1, NewAfterLaunch: true, PatternHash: secondPattern, Controls: secondControls}
		ledger := &hiddenPromptS5Ledger{}
		receipt, confirmErr := admitAndConfirmHiddenPromptS5(main, map[uintptr]struct{}{}, first, second, member, ledger, confirmHiddenPromptS5Windows, hiddenPromptS5Post(main, prompt, desktop, job, markerHash))
		if confirmErr != nil {
			return hiddenPromptS5WorkerResult{Status: receipt.Status, Inventory: secondInventory, Receipt: receipt, Isolation: isolation}
		}
		return hiddenPromptS5WorkerResult{Status: "passed", Inventory: secondInventory, Receipt: receipt, Isolation: isolation}
	}
	return hiddenPromptS5WorkerResult{Status: lastStatus, Diagnostic: diagnostic, Inventory: lastInventory}
}

func TestHiddenPromptS5Worker(t *testing.T) {
	if os.Getenv("QA_MCP_INTERNAL_HIDDEN_LIFECYCLE_MODE") != "worker" {
		t.Skip("internal S5 hidden worker")
	}
	output, markerHash := os.Getenv("QA_MCP_S5_WORKER_RESULT"), os.Getenv("QA_MCP_S5_MARKER_SHA256")
	if !filepath.IsAbs(output) || !validHiddenWindowHash(markerHash) {
		t.Fatal("S5 worker evidence identity is invalid")
	}
	hiddenWorkerPublishResponse = func(path string, data []byte) error {
		if err := publishHiddenWorkerResponse(path, data); err != nil {
			return err
		}
		var response hiddenWorkerLifecycleResponse
		if json.Unmarshal(data, &response) != nil || response.WorkerPID != uint32(os.Getpid()) || response.WorkerJobHandle == 0 {
			return os.ErrInvalid
		}
		result := observeAndConfirmHiddenPromptS5(response, markerHash)
		encoded, _ := json.Marshal(result)
		return os.WriteFile(output, append(encoded, '\n'), 0o600)
	}
	if err := runHiddenWorkerLifecycleWorker(); err != nil {
		t.Fatal(err)
	}
}

func TestHiddenPromptS5Native(t *testing.T) {
	platform, target := strings.TrimSpace(os.Getenv("QA_MCP_S5_PLATFORM_EXE")), strings.TrimSpace(os.Getenv("QA_MCP_S5_TARGET"))
	markerHash := strings.TrimSpace(os.Getenv("QA_MCP_S5_MARKER_SHA256"))
	executePaths, err := hiddenPromptS5FreshEPFs()
	if err != nil {
		t.Fatal(err)
	}
	if platform == "" || target == "" || len(executePaths) == 0 || markerHash == "" {
		t.Skip("exact ignored S5 Windows inputs are unavailable")
	}
	if !filepath.IsAbs(platform) || !filepath.IsAbs(target) ||
		!strings.Contains(strings.ToLower(platform), `\8.3.27.2214\`) || !strings.EqualFold(filepath.Clean(target), `C:\1C_BASES\vanessa_client`) || !validHiddenWindowHash(markerHash) {
		t.Fatal("exact S5 platform, target, execute path or marker identity is invalid")
	}
	evidence := hiddenPromptS5NativeEvidence{Schema: "qa-mcp.s5-native-prompt.v1", Status: "passed", PlatformVersion: "8.3.27.2214", Runs: 2}
	for run := 0; run < evidence.Runs; run++ {
		executePath := executePaths[run]
		identity, err := newHiddenDesktopProcessIdentity("s5-native-"+strconv.Itoa(run)+"-"+strconv.FormatInt(time.Now().UnixNano(), 10), "s5-native-token")
		if err != nil {
			t.Fatal(err)
		}
		port := freeHiddenWorkerPort(t)
		args := []string{"ENTERPRISE", "/F" + target}
		if user := os.Getenv("QA_MCP_S5_USER"); user != "" {
			args = append(args, "/N"+user)
		}
		if password := os.Getenv("QA_MCP_S5_PASSWORD"); password != "" {
			args = append(args, "/P"+password)
		}
		args = append(args, "/AppAutoCheckVersion-", "/TESTCLIENT", "-TPort", strconv.Itoa(port), "/Execute", executePath, "/DisableStartupDialogs", "/DisableStartupMessages")
		file, err := os.CreateTemp("", "qa-mcp-s5-worker-result-*.json")
		if err != nil {
			t.Fatal(err)
		}
		resultPath := file.Name()
		file.Close()
		os.Remove(resultPath)
		defer os.Remove(resultPath)
		environment := append(os.Environ(), "QA_MCP_S5_WORKER_RESULT="+resultPath, "QA_MCP_S5_MARKER_SHA256="+markerHash)
		request := hiddenWorkerLifecycleRequest{Identity: identity, WorkerToken: "s5-native-token", WorkerArgs: []string{"-test.run=^TestHiddenPromptS5Worker$", "-test.count=1"}, ChildExecutable: platform, ChildArgs: args, Environment: environment, Port: port, Timeout: 100 * time.Second}
		lifecycle, err := startHiddenWorkerLifecycle(context.Background(), request)
		if err != nil {
			t.Fatal(err)
		}
		defer lifecycle.Close()
		response, job, responsePath := lifecycle.Response, lifecycle.job, lifecycle.responsePath
		deadline := time.Now().Add(70 * time.Second)
		var result hiddenPromptS5WorkerResult
		for time.Now().Before(deadline) {
			data, readErr := os.ReadFile(resultPath)
			if readErr == nil && json.Unmarshal(data, &result) == nil {
				break
			}
			time.Sleep(100 * time.Millisecond)
		}
		if result.Status != "passed" || validateHiddenPromptS5Receipt(result.Receipt) != nil || result.Isolation.JobOwnedOperatorWindowCount != 0 {
			t.Fatalf("exact S5 prompt run %d failed: %s (%s) inventory=%s/%t/%t/%d/%d/%d", run+1, result.Status, result.Diagnostic,
				result.Inventory.Code, result.Inventory.Complete, result.Inventory.HashesValid, result.Inventory.RowCount,
				result.Inventory.ExactPIDCount, result.Inventory.TargetMatchCount)
		}
		if err := lifecycle.Close(); err != nil {
			t.Fatal(err)
		}
		assertHiddenWorkerResourcesGone(t, request, response.WorkerPID, response.ChildPID, response.ListenerPID, job, responsePath)
		evidence.Receipts = append(evidence.Receipts, result.Receipt)
		evidence.Inventories = append(evidence.Inventories, result.Inventory)
		evidence.Isolation = append(evidence.Isolation, result.Isolation)
		evidence.AddressedConfirmations++
		evidence.AddressedMessages += int(result.Receipt.KeyMessages)
	}
	binary, err := os.ReadFile(os.Args[0])
	if err != nil {
		t.Fatal(err)
	}
	sum := sha256.Sum256(binary)
	evidence.CandidateSHA256, evidence.TargetHash = hex.EncodeToString(sum[:]), hiddenWindowHash(strings.ToLower(filepath.Clean(target)))
	for _, executePath := range executePaths {
		data, readErr := os.ReadFile(executePath)
		if readErr != nil {
			t.Fatal(readErr)
		}
		executeSum := sha256.Sum256(data)
		evidence.ExecuteHashes = append(evidence.ExecuteHashes, hex.EncodeToString(executeSum[:]))
	}
	evidence.CleanupComplete = true
	if directory := strings.TrimSpace(os.Getenv("QA_MCP_S5_RECEIPT_DIR")); directory != "" {
		encoded, _ := json.Marshal(evidence)
		if err := os.WriteFile(filepath.Join(directory, "native-prompt.json"), append(encoded, '\n'), 0o600); err != nil {
			t.Fatal(err)
		}
	}
}

func TestHiddenPromptS5FreshEPFInputs(t *testing.T) {
	run1 := filepath.Join(t.TempDir(), "run1.epf")
	run2 := filepath.Join(t.TempDir(), "run2.epf")
	if err := os.WriteFile(run1, []byte("fresh-run-1"), 0o600); err != nil {
		t.Fatal(err)
	}
	if err := os.WriteFile(run2, []byte("fresh-run-2"), 0o600); err != nil {
		t.Fatal(err)
	}

	t.Setenv("QA_MCP_S5_EPF_RUN1", run1)
	t.Setenv("QA_MCP_S5_EPF_RUN2", "")
	if _, err := hiddenPromptS5FreshEPFs(); err == nil {
		t.Fatal("one fresh EPF must fail closed")
	}
	t.Setenv("QA_MCP_S5_EPF_RUN2", run1)
	if _, err := hiddenPromptS5FreshEPFs(); err == nil {
		t.Fatal("duplicate fresh EPF path must fail closed")
	}
	duplicate := filepath.Join(t.TempDir(), "duplicate.epf")
	if err := os.WriteFile(duplicate, []byte("fresh-run-1"), 0o600); err != nil {
		t.Fatal(err)
	}
	t.Setenv("QA_MCP_S5_EPF_RUN2", duplicate)
	if _, err := hiddenPromptS5FreshEPFs(); err == nil {
		t.Fatal("duplicate fresh EPF content must fail closed")
	}
	t.Setenv("QA_MCP_S5_EPF_RUN2", run2)
	paths, err := hiddenPromptS5FreshEPFs()
	if err != nil {
		t.Fatal(err)
	}
	if len(paths) != 2 || paths[0] != filepath.Clean(run1) || paths[1] != filepath.Clean(run2) {
		t.Fatalf("unexpected exact fresh EPF inputs: %#v", paths)
	}
}
