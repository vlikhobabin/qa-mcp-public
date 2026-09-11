package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"sync"
)

const (
	hiddenDirectS6Schema          = "qa-mcp.internal-hidden-direct-execute-receipt.v1"
	hiddenDirectS6Observed        = "exact_direct_execute_observed"
	hiddenDirectS6PromptConfirmed = "exact_direct_execute_prompt_confirmed"
)

type hiddenDirectCleanupIdentity struct {
	RunIDHash       string `json:"run_id_hash"`
	WorkerTokenHash string `json:"worker_token_hash"`
	DesktopHash     string `json:"desktop_hash"`
	Port            int    `json:"port"`
	WorkerPID       uint32 `json:"worker_pid"`
	ChildPID        uint32 `json:"child_pid"`
	ListenerPID     uint32 `json:"listener_pid"`
}

func (value hiddenDirectCleanupIdentity) valid() bool {
	return validHiddenWindowHash(value.RunIDHash) && validHiddenWindowHash(value.WorkerTokenHash) &&
		validHiddenWindowHash(value.DesktopHash) && validTCPPort(value.Port) && value.WorkerPID != 0 &&
		value.ChildPID != 0 && value.ListenerPID != 0 && value.WorkerPID != value.ChildPID
}

func (value hiddenDirectCleanupIdentity) hash() string {
	return hiddenWindowHash(fmt.Sprintf("%s|%s|%s|%d|%d|%d|%d", value.RunIDHash, value.WorkerTokenHash,
		value.DesktopHash, value.Port, value.WorkerPID, value.ChildPID, value.ListenerPID))
}

type hiddenDirectS6Receipt struct {
	Schema              string                         `json:"schema"`
	Status              string                         `json:"status"`
	Cleanup             hiddenDirectCleanupIdentity    `json:"cleanup"`
	CleanupIdentityHash string                         `json:"cleanup_identity_hash"`
	Observation         hiddenDirectObservationReceipt `json:"observation"`
	Prompt              *hiddenPromptS5Receipt         `json:"prompt"`
}

type hiddenDirectS6Ledger struct {
	mu       sync.Mutex
	consumed map[string]struct{}
}

func (ledger *hiddenDirectS6Ledger) available(binding string) bool {
	ledger.mu.Lock()
	defer ledger.mu.Unlock()
	_, used := ledger.consumed[binding]
	return !used
}

func (ledger *hiddenDirectS6Ledger) consume(binding string) bool {
	ledger.mu.Lock()
	defer ledger.mu.Unlock()
	if _, used := ledger.consumed[binding]; used {
		return false
	}
	if ledger.consumed == nil {
		ledger.consumed = make(map[string]struct{})
	}
	ledger.consumed[binding] = struct{}{}
	return true
}

type hiddenDirectS6Lease struct {
	receipt     hiddenDirectS6Receipt
	fingerprint string
	ledger      *hiddenDirectS6Ledger
}

func bindHiddenDirectS6Receipt(request hiddenWorkerLifecycleRequest, workerPID uint32, response hiddenWorkerLifecycleResponse,
	observation hiddenDirectObservationReceipt, prompt *hiddenPromptS5Receipt, ledger *hiddenDirectS6Ledger) (hiddenDirectS6Receipt, *hiddenDirectS6Lease, error) {
	if ledger == nil || validateHiddenWorkerLifecycleResponse(request, response, workerPID) != nil {
		return hiddenDirectS6Receipt{}, nil, errors.New("direct-execute lifecycle identity is invalid")
	}
	cleanup := hiddenDirectCleanupIdentity{response.RunIDHash, response.WorkerTokenHash, response.DesktopHash,
		response.Port, response.WorkerPID, response.ChildPID, response.ListenerPID}
	receipt := hiddenDirectS6Receipt{Schema: hiddenDirectS6Schema, Status: hiddenDirectS6Observed,
		Cleanup: cleanup, CleanupIdentityHash: cleanup.hash(), Observation: observation, Prompt: prompt}
	if prompt != nil {
		receipt.Status = hiddenDirectS6PromptConfirmed
	}
	if err := admitHiddenDirectS6Receipt(receipt, cleanup); err != nil {
		return receipt, nil, err
	}
	if !ledger.available(receipt.CleanupIdentityHash) {
		return receipt, nil, errors.New("direct-execute cleanup identity was already consumed")
	}
	return receipt, &hiddenDirectS6Lease{receipt: receipt, fingerprint: hiddenDirectS6Fingerprint(receipt), ledger: ledger}, nil
}

func admitHiddenDirectS6Receipt(value hiddenDirectS6Receipt, expected hiddenDirectCleanupIdentity) error {
	if value.Schema != hiddenDirectS6Schema || !expected.valid() || value.Cleanup != expected ||
		value.CleanupIdentityHash != expected.hash() || validateHiddenDirectObservationReceipt(value.Observation) != nil {
		return errors.New("direct-execute receipt identity is invalid")
	}
	if value.Prompt == nil {
		if value.Status != hiddenDirectS6Observed {
			return errors.New("direct-execute prompt-free status is invalid")
		}
		return nil
	}
	if value.Status != hiddenDirectS6PromptConfirmed || validateHiddenPromptS5Receipt(*value.Prompt) != nil ||
		value.Prompt.MainIdentityHash != value.Observation.MainIdentityHash {
		return errors.New("direct-execute prompt receipt is invalid")
	}
	return nil
}

func hiddenDirectS6Fingerprint(value hiddenDirectS6Receipt) string {
	encoded, err := json.Marshal(value)
	if err != nil {
		return ""
	}
	return hiddenWindowHash(string(encoded))
}

func (lease *hiddenDirectS6Lease) Stop(value hiddenDirectS6Receipt, cleanup func() error) error {
	if lease == nil || cleanup == nil || lease.ledger == nil || hiddenDirectS6Fingerprint(value) != lease.fingerprint ||
		admitHiddenDirectS6Receipt(value, lease.receipt.Cleanup) != nil {
		return errors.New("direct-execute stop receipt is stale or changed")
	}
	if !lease.ledger.consume(value.CleanupIdentityHash) {
		return errors.New("direct-execute cleanup identity was already consumed")
	}
	return cleanup()
}
