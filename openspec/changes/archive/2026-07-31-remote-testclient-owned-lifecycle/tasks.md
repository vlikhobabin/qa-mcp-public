## 1. Host-Agent Lifecycle

- [x] 1.1 Add host-agent owned TestClient launch tracking keyed by exact PID.
- [x] 1.2 Add authenticated `/testclient/stop` with exact-owned PID refusal,
  idempotent final states, and bounded sanitized response fields.
- [x] 1.3 Add Go tests for owned stop, repeated stop, unknown PID refusal, and
  stop-route authentication.

## 2. Python MCP Lifecycle

- [x] 2.1 Add remote display-backend client support for the host-agent stop
  route.
- [x] 2.2 Mark successful remote host-agent launches as provider-owned
  lifecycle handles while keeping manual attachments unowned.
- [x] 2.3 Route remote-client `stop_test_client` through the host-agent for
  owned handles and return structured refusal/final-state results.
- [x] 2.4 Add Python tests for launch ownership, remote stop routing, repeated
  stop, and attach-only refusal.

## 3. Specs, Evidence And Verification

- [x] 3.1 Sync delta specs into main specs after implementation.
- [x] 3.2 Run focused Python and Go verification for the changed lifecycle
  paths.
- [x] 3.3 Run strict OpenSpec validation and whitespace checks.
- [x] 3.4 Retain Windows host-agent launch/attach/stop/process-absence proof
  when the authorized Windows host is reachable, or record a bounded runtime
  provider gap.

## 4. Review-Cycle Rescue

- [x] 4.1 Fix review R1 by removing Python-side lifecycle ownership inference
  for legacy or protocol-compatible host-agent launch results that do not
  explicitly report `owns_process: true`.
- [x] 4.2 Fix review R2 by recording started host-agent TestClient processes
  before readiness errors are returned, and by exposing bounded cleanup handles
  for live not-ready launches.
- [x] 4.3 Add rescue regression tests for legacy unowned launch results,
  not-ready cleanup-handle propagation, and host-agent not-listening stop.
- [x] 4.4 Sync rescue semantics into main and archived specs.
- [x] 4.5 Suppress Windows PowerShell progress output in transient TestClient
  task helper scripts so first-use ScheduledTasks progress records cannot
  surface as `#< CLIXML` launch diagnostics.
- [x] 4.6 Resolve the Windows live-proof blocker by keeping the proof script
  ASCII-safe for PowerShell 5.1 and reconstructing the Cyrillic test username
  from UTF-8 base64 before issuing the host-agent launch request.
- [x] 4.7 Fix review-cycle 2 R1 by replacing the consumable process-exit
  channel with durable completion state and retaining the exact terminate
  callback for the launched process.
- [x] 4.8 Add a stale/completed lifecycle regression proving a completed owned
  record cannot terminate an unrelated PID-reused process.
- [x] 4.9 Fix review-cycle 2 R2 by removing raw host-agent log tails from the
  proof collector and retained lifecycle evidence, keeping only structured
  cleanup booleans.
- [x] 4.10 Fix review-cycle 3 R1 by keying host-agent lifecycle records by an
  opaque lifecycle id instead of PID and requiring that id for remote stop.
- [x] 4.11 Add Go and Python regressions proving PID-only stale cleanup cannot
  stop a newer same-PID lifecycle.
- [x] 4.12 Sync lifecycle-handle stop semantics into main and archived specs and
  update retained Windows proof collection to call stop with the returned
  lifecycle handle.
- [x] 4.13 Fix review-cycle 4 R1 by making remote TestClient stop capability
  specific and rejecting protocol-compatible PID-only host-agents before the
  stop request is posted.
- [x] 4.14 Add Python regressions proving a `0.1.9` protocol-compatible
  host-agent cannot receive `/testclient/stop` and that the MCP tool returns a
  structured unsupported-lifecycle diagnostic.
- [x] 4.15 Sync compatibility fail-closed semantics into main and archived specs
  and the board evidence.
