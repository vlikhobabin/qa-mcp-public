## 1. Planning And Matrix Preflight

- [x] 1.1 Create proposal, design, delta specs and tasks for
  `host-agent-testclient-launch-persistence-dwell`.
- [x] 1.2 Run `openspec validate host-agent-testclient-launch-persistence-dwell --strict`
  and `git diff --check -- openspec/changes/host-agent-testclient-launch-persistence-dwell openspec/board`.
- [x] 1.3 Run the 1C verification matrix checker in preflight mode and retain
  output under `.artifacts/openspec/host-agent-testclient-launch-persistence-dwell/20260708T125349Z/`.

## 2. Test-First Host-Agent Dwell Coverage

- [x] 2.1 Add RED Go coverage where a fake TestClient process binds the
  requested TPort, keeps it briefly reachable, exits during the persistence
  dwell, and must classify as `exited_early` rather than `ready`.
- [x] 2.2 Add or confirm GREEN Go coverage where a fake process persists
  through the dwell and still classifies as `ready`.
- [x] 2.3 Add or confirm coverage that the launch wait remains bounded by
  `timeout_seconds`.
- [x] 2.4 Record the RED command and one-line failure summary in verification
  notes or retained artifacts.

## 3. Implementation

- [x] 3.1 Add a bounded persistence dwell to `waitForTestClientReadiness` after
  the first alive-plus-listening observation.
- [x] 3.2 During the dwell, continue honoring context cancellation, process
  exit, launch deadline and TPort listening state.
- [x] 3.3 Preserve existing result labels and HTTP error mapping:
  `ready`, `exited_early`, `not_listening` and `canceled`.
- [x] 3.4 Keep already-listening TPort reuse semantics unchanged.

## 4. Runtime Gap Evidence

- [x] 4.1 Retain an artifact recording that live Windows .205 dwell
  confirmation was not run in this offline session, with owner
  `/opt/ai-dev-suite-for-1c/qa-mcp`.
- [x] 4.2 Do not run or fabricate the real Windows .205 persistence proof.

## 5. Verification And Handoff

- [x] 5.1 Run focused Go tests for TestClient readiness dwell behavior.
- [x] 5.2 Run full `go test ./...` under `host-agent/windows-display-agent`.
- [x] 5.3 Run `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-dwell.test.exe .`
  under `host-agent/windows-display-agent`.
- [x] 5.4 Run the suite regression gate or record a scoped exception:
  `uv run --with pytest --with pyyaml pytest`,
  `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/check_suite_source_of_truth_drift.py`,
  and `uv run --with pytest --with pyyaml pytest -m smoke`.
- [x] 5.5 Run `openspec status --change host-agent-testclient-launch-persistence-dwell --json`,
  `openspec instructions apply --change host-agent-testclient-launch-persistence-dwell --json`,
  `openspec validate host-agent-testclient-launch-persistence-dwell --strict`
  and `git diff --check`.
- [x] 5.6 Run the matrix checker in archive-gate mode and retain output under
  `.artifacts/openspec/host-agent-testclient-launch-persistence-dwell/20260708T125349Z/`.
- [x] 5.7 Sync the `qa-mcp-windows-host-agent-security` and
  `qa-mcp-tool-endpoint-contract` delta specs into the main specs and run
  scoped plus all-spec validation.
- [x] 5.8 Archive the change after tasks, verification and spec sync are
  complete.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | host-agent-launched Windows TestClient on real .205 host | Real-host smoke: launch through running host-agent, wait longer than the dwell, confirm the TestClient remains alive and TPort reachable, then attach/read through qa-mcp | Sanitized smoke transcript or provider-gap report | `.artifacts/openspec/host-agent-testclient-launch-persistence-dwell/20260708T125349Z/windows-host-dwell-provider-gap.md` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Real Windows .205 host unavailable in this session; runtime persistence remains unproven. |
| Delivery or runtime apply | Windows host-agent TestClient readiness classifier | Go unit tests for bind-then-exit-during-dwell, persistent ready, timeout boundedness and existing early-exit/not-listening behavior | `go test ./...` output and retained summary | `.artifacts/openspec/host-agent-testclient-launch-persistence-dwell/20260708T125349Z/host-agent-dwell-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Offline tests prove classifier timing, not real Windows GUI persistence. |
| Native protocol claim | TestClient wire frames and replay templates | No protocol semantic change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No native TestClient protocol claim is made. | None for corpus coverage. |
| Business data mutation | Object writes, posting, delete/fill/import/export | No business mutation is part of this launch-readiness change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change launches/checks TestClient process and TPort liveness only. | None beyond process availability. |

## Provider Gap Records

| provider_id | owner_path | matrix_row | missing_evidence_type | impact | current_workaround | source_card | sanitized_evidence | sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qa-mcp | `/opt/ai-dev-suite-for-1c/qa-mcp` | QA/TestClient UI automation | qa_testclient_bundle | Blocks proof that a host-agent-launched `/TESTCLIENT` on the real Windows .205 host persists past the new readiness dwell with a reachable TPort. | Operator can run the retained Windows-host smoke later on the real host and replace this provider-gap artifact with a sanitized proof bundle. | `openspec/board/2.todo/host-agent-testclient-launch-persistence-dwell.md` | `.artifacts/openspec/host-agent-testclient-launch-persistence-dwell/20260708T125349Z/windows-host-dwell-provider-gap.md` | no credentials, screenshots or live data copied |

## Verification Notes

- Matrix preflight:
  `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py openspec/changes/host-agent-testclient-launch-persistence-dwell/tasks.md --workspace . --mode preflight --output .artifacts/openspec/host-agent-testclient-launch-persistence-dwell/20260708T125349Z/matrix-preflight.json --json`
  passed with 4 matrix rows and 1 explicit provider gap.
- RED Go:
  `cd host-agent/windows-display-agent && go test ./... -run TestTestClientReadinessRequiresPortPersistenceDwell`
  failed before implementation with `readiness = "ready", want exited_early`;
  retained at
  `.artifacts/openspec/host-agent-testclient-launch-persistence-dwell/20260708T125349Z/host-agent-dwell-tests.md`.
- GREEN Go focused:
  `cd host-agent/windows-display-agent && go test ./... -run "TestTestClientLaunch(ReportsEarlyExitInsteadOfReady|ReportsNotListeningProcessInsteadOfReady|ReportsReadyOnlyWhenProcessAndPortLive|StartsDetachedAndRedactsSecrets)|TestTestClientReadiness(DoesNotTreatListeningPortAsAliveAfterExit|RequiresPortPersistenceDwell|DwellHonorsLaunchTimeout)"`
  passed with `ok qa-mcp-host-agent 2.942s`.
- GREEN Go full:
  `cd host-agent/windows-display-agent && go test ./...` passed with
  `ok qa-mcp-host-agent 9.369s`.
- GREEN Windows cross-compile:
  `cd host-agent/windows-display-agent && GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-dwell.test.exe .`
  passed.
- Suite regression:
  `uv run --with pytest --with pyyaml pytest` passed with
  `790 passed in 49.97s`.
- Suite drift gate:
  `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/check_suite_source_of_truth_drift.py`
  passed with `result: OK (0 finding(s))`.
- Suite smoke:
  `uv run --with pytest --with pyyaml pytest -m smoke` passed with
  `3 passed, 787 deselected in 2.80s`.
- Minimum OpenSpec verification:
  `openspec status --change host-agent-testclient-launch-persistence-dwell --json`,
  `openspec instructions apply --change host-agent-testclient-launch-persistence-dwell --json`,
  `openspec validate host-agent-testclient-launch-persistence-dwell --strict`
  and `git diff --check` passed.
- Matrix archive gate:
  `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py openspec/changes/host-agent-testclient-launch-persistence-dwell/tasks.md --workspace . --mode archive --output .artifacts/openspec/host-agent-testclient-launch-persistence-dwell/20260708T125349Z/matrix-archive-gate.json --json`
  passed with 4 matrix rows and 1 explicit provider gap.
- Main spec sync validations passed for
  `openspec validate qa-mcp-windows-host-agent-security --strict`,
  `openspec validate qa-mcp-tool-endpoint-contract --strict`, and
  `openspec validate --all`.
- Runtime Windows .205 dwell proof was not run. The retained provider gap is
  `.artifacts/openspec/host-agent-testclient-launch-persistence-dwell/20260708T125349Z/windows-host-dwell-provider-gap.md`.
