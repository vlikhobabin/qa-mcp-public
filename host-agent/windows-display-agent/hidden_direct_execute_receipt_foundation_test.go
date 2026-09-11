package main

import (
	"encoding/json"
	"errors"
	"strings"
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

func s6Fixture(t *testing.T, withPrompt bool) (hiddenDirectS6Receipt, *hiddenDirectS6Lease, hiddenDirectCleanupIdentity) {
	t.Helper()
	identity, err := newHiddenDesktopProcessIdentity("s6-run", "s6-token")
	if err != nil {
		t.Fatal(err)
	}
	request := hiddenWorkerLifecycleRequest{Identity: identity, WorkerToken: "s6-token", ChildExecutable: "/opt/1cv8c", Environment: []string{"PATH=/opt"}, Port: 15473, Timeout: time.Second}
	response := hiddenWorkerLifecycleResponse{Schema: hiddenWorkerLifecycleSchema, Code: "ready", RunIDHash: identity.RunIDHash, WorkerTokenHash: identity.WorkerTokenHash, DesktopHash: hiddenDesktopProcessHash(identity.Desktop), Port: request.Port, WorkerPID: 11, ChildPID: 12, ListenerPID: 12, WorkerJobHandle: 13}
	observation := hiddenDirectObservationReceipt{Schema: hiddenDirectObservationSchema, Status: hiddenDirectObservationObserved, MainIdentityHash: strings.Repeat("a", 64), ExpectedMarkerHash: strings.Repeat("b", 64), TopologyHash: strings.Repeat("c", 64), MarkerMatchCount: 1, ControlCount: 3}
	var prompt *hiddenPromptS5Receipt
	if withPrompt {
		prompt = &hiddenPromptS5Receipt{Schema: hiddenPromptS5Schema, Status: hiddenPromptS5Confirmed, MainIdentityHash: observation.MainIdentityHash, PromptIdentityHash: strings.Repeat("d", 64), PatternHash: strings.Repeat("e", 64), TopologyHash: strings.Repeat("f", 64), ActionPathHash: hiddenPromptS5ActionPathHash, RootGeometryHash: strings.Repeat("1", 64), ActionGeometryHash: strings.Repeat("2", 64), ControlCount: 3, InvokeCount: 1, ActionAttempts: 1, FocusCalls: 1, KeyMessages: 2, PromptClosed: true}
	}
	ledger := &hiddenDirectS6Ledger{}
	receipt, lease, err := bindHiddenDirectS6Receipt(request, response.WorkerPID, response, observation, prompt, ledger)
	if err != nil {
		t.Fatal(err)
	}
	return receipt, lease, receipt.Cleanup
}

func TestHiddenDirectS6BindsPublishedPromptFreeAndPromptReceipts(t *testing.T) {
	for _, prompted := range []bool{false, true} {
		receipt, _, expected := s6Fixture(t, prompted)
		if err := admitHiddenDirectS6Receipt(receipt, expected); err != nil {
			t.Fatalf("prompt=%t: %v", prompted, err)
		}
		want := hiddenDirectS6Observed
		if prompted {
			want = hiddenDirectS6PromptConfirmed
		}
		if receipt.Status != want || receipt.CleanupIdentityHash != expected.hash() {
			t.Fatalf("unexpected binding: %#v", receipt)
		}
	}
}

func TestHiddenDirectS6RejectsMalformedNestedReceiptBeforeCallback(t *testing.T) {
	exact, _, expected := s6Fixture(t, true)
	hostiles := []hiddenDirectS6Receipt{
		func() hiddenDirectS6Receipt { value := exact; value.Schema = "changed"; return value }(),
		func() hiddenDirectS6Receipt { value := exact; value.Status = "changed"; return value }(),
		func() hiddenDirectS6Receipt { value := exact; value.CleanupIdentityHash = "bad"; return value }(),
		func() hiddenDirectS6Receipt { value := exact; value.Observation.Schema = "changed"; return value }(),
		func() hiddenDirectS6Receipt { value := exact; value.Observation.Status = "changed"; return value }(),
		func() hiddenDirectS6Receipt { value := exact; value.Observation.ControlCount = 0; return value }(),
		func() hiddenDirectS6Receipt { value := exact; value.Observation.TopologyHash = "bad"; return value }(),
		func() hiddenDirectS6Receipt { value := exact; value.Prompt.Status = "changed"; return value }(),
		func() hiddenDirectS6Receipt { value := exact; value.Prompt.ActionAttempts = 0; return value }(),
		func() hiddenDirectS6Receipt {
			value := exact
			value.Prompt.MainIdentityHash = strings.Repeat("9", 64)
			return value
		}(),
	}
	for index, hostile := range hostiles {
		if err := admitHiddenDirectS6Receipt(hostile, expected); err == nil {
			t.Fatalf("hostile %d admitted", index)
		}
	}
}

func TestHiddenDirectS6RejectsForeignCleanupAndPostBindMutation(t *testing.T) {
	receipt, lease, expected := s6Fixture(t, false)
	foreign := []hiddenDirectCleanupIdentity{
		func() hiddenDirectCleanupIdentity {
			value := expected
			value.RunIDHash = strings.Repeat("9", 64)
			return value
		}(),
		func() hiddenDirectCleanupIdentity {
			value := expected
			value.WorkerTokenHash = strings.Repeat("9", 64)
			return value
		}(),
		func() hiddenDirectCleanupIdentity {
			value := expected
			value.DesktopHash = strings.Repeat("9", 64)
			return value
		}(),
		func() hiddenDirectCleanupIdentity { value := expected; value.Port++; return value }(),
		func() hiddenDirectCleanupIdentity { value := expected; value.WorkerPID++; return value }(),
		func() hiddenDirectCleanupIdentity { value := expected; value.ChildPID++; return value }(),
		func() hiddenDirectCleanupIdentity { value := expected; value.ListenerPID++; return value }(),
	}
	for index, value := range foreign {
		if err := admitHiddenDirectS6Receipt(receipt, value); err == nil {
			t.Fatalf("foreign identity %d admitted", index)
		}
	}
	mutated := receipt
	mutated.Observation.ControlCount++
	calls := 0
	if err := lease.Stop(mutated, func() error { calls++; return nil }); err == nil || calls != 0 {
		t.Fatalf("mutated receipt stopped: calls=%d err=%v", calls, err)
	}
}

func TestHiddenDirectS6ConsumesSharedLedgerBeforeSingleCleanup(t *testing.T) {
	receipt, lease, _ := s6Fixture(t, false)
	second := &hiddenDirectS6Lease{receipt: receipt, fingerprint: hiddenDirectS6Fingerprint(receipt), ledger: lease.ledger}
	calls := 0
	if err := lease.Stop(receipt, func() error { calls++; return nil }); err != nil {
		t.Fatal(err)
	}
	if err := lease.Stop(receipt, func() error { calls++; return nil }); err == nil {
		t.Fatal("repeated stop admitted")
	}
	if err := second.Stop(receipt, func() error { calls++; return nil }); err == nil {
		t.Fatal("replayed lease admitted")
	}
	if calls != 1 {
		t.Fatalf("cleanup calls=%d", calls)
	}
}

func TestHiddenDirectS6FailedCleanupRemainsConsumed(t *testing.T) {
	receipt, lease, _ := s6Fixture(t, true)
	calls := 0
	if err := lease.Stop(receipt, func() error { calls++; return errors.New("typed cleanup failure") }); err == nil {
		t.Fatal("cleanup failure lost")
	}
	if err := lease.Stop(receipt, func() error { calls++; return nil }); err == nil || calls != 1 {
		t.Fatalf("failed cleanup retried: calls=%d err=%v", calls, err)
	}
}

func TestHiddenDirectS6CanonicalCleanupHash(t *testing.T) {
	identity := hiddenDirectCleanupIdentity{RunIDHash: strings.Repeat("a", 64), WorkerTokenHash: strings.Repeat("b", 64), DesktopHash: strings.Repeat("c", 64), Port: 15473, WorkerPID: 11, ChildPID: 12, ListenerPID: 12}
	if got := identity.hash(); got != "3ae48845756209ad1c84ab79906a090c4bd94126f7913731818ff320e6e5e79b" {
		t.Fatalf("canonical hash=%s", got)
	}
}

func TestHiddenDirectS6JSONBoundaryIsTypedAndSanitized(t *testing.T) {
	receipt, _, _ := s6Fixture(t, true)
	encoded, err := json.Marshal(receipt)
	if err != nil {
		t.Fatal(err)
	}
	text := string(encoded)
	for _, forbidden := range []string{"WorkerJobHandle", "worker_job_handle", "s6-run", "s6-token", "/opt/1cv8c", "credential", "screenshot"} {
		if strings.Contains(text, forbidden) {
			t.Fatalf("serialized receipt retained forbidden %q", forbidden)
		}
	}
	var decoded map[string]any
	if json.Unmarshal(encoded, &decoded) != nil {
		t.Fatal("serialized receipt is not JSON")
	}
	cleanup, ok := decoded["cleanup"].(map[string]any)
	if !ok || len(cleanup) != 7 || cleanup["run_id_hash"] == nil || cleanup["listener_pid"] == nil {
		t.Fatalf("cleanup boundary is not exact: %#v", cleanup)
	}
}

func TestHiddenDirectS6JSONPIDBoundaryMatchesUint32(t *testing.T) {
	receipt, _, expected := s6Fixture(t, false)
	expected.WorkerPID = ^uint32(0)
	receipt.Cleanup = expected
	receipt.CleanupIdentityHash = expected.hash()
	encoded, err := json.Marshal(receipt)
	if err != nil {
		t.Fatal(err)
	}
	var decoded hiddenDirectS6Receipt
	if err := json.Unmarshal(encoded, &decoded); err != nil {
		t.Fatal(err)
	}
	if err := admitHiddenDirectS6Receipt(decoded, expected); err != nil {
		t.Fatalf("uint32 maximum rejected: %v", err)
	}
	hostile := strings.Replace(string(encoded), `"worker_pid":4294967295`, `"worker_pid":4294967296`, 1)
	calls := 0
	if err := json.Unmarshal([]byte(hostile), &decoded); err == nil {
		t.Fatal("PID above uint32 admitted by Go JSON boundary")
	}
	if calls != 0 {
		t.Fatalf("rejected PID invoked cleanup %d times", calls)
	}
}

func TestHiddenDirectS6ConcurrentSharedLedgerInvokesCleanupOnce(t *testing.T) {
	receipt, lease, _ := s6Fixture(t, false)
	const contenders = 32
	leases := make([]*hiddenDirectS6Lease, contenders)
	for index := range leases {
		leases[index] = &hiddenDirectS6Lease{receipt: receipt, fingerprint: hiddenDirectS6Fingerprint(receipt), ledger: lease.ledger}
	}
	start := make(chan struct{})
	var group sync.WaitGroup
	var calls atomic.Int32
	for _, contender := range leases {
		group.Add(1)
		go func(candidate *hiddenDirectS6Lease) {
			defer group.Done()
			<-start
			_ = candidate.Stop(receipt, func() error { calls.Add(1); return nil })
		}(contender)
	}
	close(start)
	group.Wait()
	if got := calls.Load(); got != 1 {
		t.Fatalf("concurrent cleanup calls=%d, want 1", got)
	}
}
