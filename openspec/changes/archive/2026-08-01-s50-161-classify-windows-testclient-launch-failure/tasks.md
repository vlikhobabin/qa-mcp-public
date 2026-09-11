## 1. Regression First

- [x] 1.1 Add focused Go tests that fail against the current combined
  shell-broker/PID error path and cover broker-before-ack, acknowledged early
  exit, live PID-handoff failure, and differing listener-owner PID.
- [x] 1.2 Record why those tests execute the shared production classification
  and owner-resolution state machines and would fail if broker/PID handling
  were collapsed into platform failure or a numeric PID were reused for cleanup.

## 2. Windows Launcher Classification

- [x] 2.1 Implement bounded broker acknowledgement provenance and make the live
  requested-TPort owner authoritative for lifecycle ownership.
- [x] 2.2 Return typed, secret-safe early-exit versus PID-handoff metadata
  without creating a lifecycle handle for failed launch.
- [x] 2.3 Keep exact transient-task cleanup and active-session validation intact.

## 3. Verification

- [x] 3.1 Run focused/full Go tests, Windows cross-build, focused Python remote
  launch tests, formatting/lint checks required by the changed surface, strict
  OpenSpec validation, public/secret scan and diff check.
- [x] 3.2 Build the Windows host-agent artifact and retain `.200` hostname,
  negative early-exit classification, positive launch/PID ownership, and exact
  cleanup evidence under ignored runtime state.

## Regression Evidence

- RED: `go test ./... -run 'TestClassifyTestClientBrokerProcessObservation' -count=1`
  failed to compile because the production observation/classifier contract did
  not exist.
- GREEN: focused classifier/endpoint tests and `go test ./... -count=1` passed.
  The tests feed the same broker acknowledgement, requested-TPort owner,
  process-liveness and handle-error fields used by the Windows launcher; they
  fail if a dead acknowledged PID is collapsed into start failure or if a
  differing live listener PID is not selected.
- Python propagation: `./.venv/bin/python -m pytest -q tests/test_mcp_server.py
  -k 'launch_test_client_remote'` passed (`9 passed, 132 deselected`) and fails
  if the MCP layer rewrites or attaches a PID-handoff failure.
- Final gates: `go test ./... -count=1`, `go vet ./...`, the Windows cross-test
  build, and the full Python suite (`907 passed`) completed successfully. The
  repository-wide Ruff command still reports 35 pre-existing findings outside
  this card's changed lines; scoped changed-surface lint and Python compile
  checks pass.
- Review-cycle regressions: cycle 1 found that a live acknowledged PID could be
  adopted after listener-owner timeout. Cycle 2 then found that reopening that
  numeric PID after the wait could target a recycled same-session process and
  that the first regression guard was only a source sentinel. The cycle-2 RED
  focused test failed to compile because the shared acknowledged-process lease
  and listener resolution state machine did not exist. GREEN behaviorally
  exercises listener ownership, acknowledged-process exit, exact timeout
  termination and cleanup failure through the same production state machine.
  On Windows the broker PID is opened and session-checked immediately, and the
  retained process handle—not a later PID lookup—supplies liveness and cleanup
  across the caller-bounded owner wait.
- Review cycle 3 found that the initial handle open still followed registration
  completion and exact-task cleanup. The next focused RED failed to compile
  because acknowledgement-to-lease orchestration did not exist. GREEN routes
  production through a behavior-tested seam that asserts handle acquisition is
  the first post-acknowledgement operation, ahead of registration/task cleanup,
  and terminates only that retained lease if a later continuation fails.
- Windows boundary proof:
  `.runtime/changerail/evidence/s50-161-fix-windows-disposable-infobase-testclient-launch/20260801T193000Z/`
  records `testclient-exited-early`, acknowledged PID metadata and
  `readiness:"exited_early"` for the invalid-file target, followed by a positive
  listener-owned lifecycle for the restored base. The official Windows-GUI
  bundle, manifest and sidecar verify together at SHA-256
  `4af511830e771d3e585ada5319564570095ac80007f8722866dde7a8d43d7f47`.
