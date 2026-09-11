## 1. Test-first supervision contract

- [x] 1.1 Add Go fake-helper tests for launch/readiness/status, diagnostics/resync proxying, crash/restart/backoff, restart counter, owned stop, auth-before-body, bounded output, and disabled solo mode; run them RED and retain the failure summary.
- [x] 1.2 Add pytest doctor tests for disabled, ready, and configured-not-ready BSL supervision states; run them RED and retain the failure summary.
- [x] 1.3 Add a contract-consumption test against the delivered bsl-mcp `ai1c.bsl-agent-workstation-supervision.v1` shape without modifying that repository.

## 2. Native helper supervision

- [x] 2.1 Implement fixed-command helper configuration, loopback-only validation, health/status polling, lifecycle state, restart backoff, and owned-process stop.
- [x] 2.2 Add authenticated bounded diagnostics and resync proxy routes and include sanitized helper state in host-agent health.
- [x] 2.3 Add the separate `qa_mcp_doctor` supervision check and bump host-agent compatibility without regressing prior versions.
- [x] 2.4 Document W-B configuration, supervision state, diagnostic routes, and the real Windows provider gap.

## 3. Verification and evidence

- [x] 3.1 Run focused Go/pytest tests, full host-agent Go tests, full component pytest, strict OpenSpec validation, and diff checks; retain offline evidence.
- [x] 3.2 Run the suite regression gate (`uv ... pytest`, source-of-truth drift check, pytest smoke) or record a scoped project-local reason when a suite helper is unavailable.
- [x] 3.3 Record real Windows control-event/restart and real local bsl-agent diagnostic round-trip as supervised provider gaps; do not claim those AC as PASS.
- [x] 3.4 Confirm no TestClient protocol evidence index update is needed because this change makes no protocol claim.

## 4. Cycle-1 no-go rescue

- [x] 4.1 Measure replacement launch after helper kill and enforce a deadline
  derived from the configured restart backoff plus documented scheduler
  tolerance; keep real Windows restart evidence `unverifiable`.
- [x] 4.2 Rerun focused and full verification, retain cycle-2 evidence, sync
  the unchanged requirement deltas idempotently, and re-archive.

## Verification Notes

- Cycle-2 timing coverage separates replacement launch from readiness: after
  killing the owned fake helper, the test requires a new PID and incremented
  restart counter within the configured 250 ms backoff plus 100 ms process
  reaping/scheduler tolerance, then waits independently for ready health.
- Ten repeated focused runs passed on Linux. Native Windows kill/restart and
  the real local bsl-agent diagnostic round-trip remain `unverifiable` stand
  gaps and are not promoted to PASS.
- Cycle-2 full PASS: Go test/race/vet, Windows AMD64 cross-build, full pytest
  (803), smoke pytest (3), canonical suite drift (0 findings), strict change,
  capability and workspace OpenSpec validation, matrix preflight/archive gates
  and `git diff --check` passed. Retained command/output paths are listed in
  `.artifacts/openspec/native-helper-supervision-bsl-agent/2026-07-11-cycle2/offline-verification.txt`.
- Spec sync was idempotent: both security delta requirements and the doctor
  delta requirement were already present in their canonical main specs;
  scoped strict validation and `openspec validate --all` passed.

- RED Go: `go test ./... -run 'TestBSLHelper' -count=1` failed to compile
  because the supervision contract constants, config, supervisor, proxy bound,
  and `Config.BSLHelper` did not exist.
- RED pytest: `uv run --with pytest pytest tests/test_doctor.py -k
  bsl_agent_supervision -q` failed 3 tests because the doctor check did not
  exist.
- The contract-consumption test read
  `/opt/ai-dev-suite-for-1c/bsl-mcp/config/bsl-agent-workstation-contract.v1.json`
  and passed against the fixed schema, protocol, binary, and endpoint names.
- No native TestClient request/response behavior changed, so protocol capture,
  frame ranges, replay, and evidence-index updates are N/A.
- Real Windows control events, native helper restart, and real workspace
  diagnostics remain `unverifiable` provider gaps for the supervised stand.
- Fix cycle 1: the first full pytest run found 3 existing no-host-agent doctor
  paths passing `health=None`; `_bsl_agent_check` now returns the existing
  skipped health-unavailable result, and the repeated full suite passed 803.
- PASS: focused Go/doctor tests, all host-agent Go tests, Windows AMD64
  cross-build, full component pytest (803), source-of-truth drift (0 findings),
  smoke (3), strict OpenSpec validation, and `git diff --check`.
- Fix cycle 2: self-verification compared the consumer to the real bsl-mcp
  response struct and added a RED malformed-status regression. The supervisor
  now requires HTTP 200 plus exact `schema`, `status=ready`, `ready=true`, and a
  non-empty version from both health/status before declaring readiness.
