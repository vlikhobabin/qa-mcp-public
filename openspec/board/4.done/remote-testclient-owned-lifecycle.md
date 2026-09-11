# Remote TestClient launches have owned cleanup lifecycle

## Status
4.done

## Owner
Codex

## OpenSpec Stage
archived; independent review passed; published

## Source
- Root card: `../openspec/board/3.inprogress/s50-finans-extension-e2e-090-own-remote-qa-client-lifecycle.md`
- S50 [redacted third-party configuration] remote QA lifecycle gap.

## Problem
Remote-client `launch_test_client` can ask the Windows host-agent to start a
1C TestClient, but the MCP result marks the launched process as unowned and
`stop_test_client` is blocked as a local-only tool. The provider can therefore
create a host process that its public cleanup surface cannot stop.

## Acceptance
- [x] A remotely launched client receives a provider-owned lifecycle handle.
- [x] `stop_test_client` routes cleanup through the same host agent that
  performed the launch.
- [x] Repeated stop calls are idempotent and return a typed final state.
- [x] Cleanup is scoped to the exact launched process and cannot target other
  1C sessions.
- [x] Launch, attach, stop, and post-stop process absence are covered by a
  Windows host-agent integration test.
- [x] Failure evidence remains bounded and excludes credentials, infobase
  contents, screenshots, and raw runtime logs.

## Change Set
- `remote-testclient-owned-lifecycle`:
  `openspec/changes/archive/2026-07-31-remote-testclient-owned-lifecycle/`

## Change 1: `remote-testclient-owned-lifecycle`

### Why
Remote launch and cleanup must be one provider-owned lifecycle; otherwise
qa-mcp cannot safely automate Windows-host TestClient sessions end-to-end.

### Goal
Add exact-process host-agent cleanup for host-agent-launched TestClients and
route MCP `stop_test_client` through it in remote-client mode.

### Scope
- Python MCP lifecycle result and stop routing for remote-client mode.
- Remote display backend host-agent stop client.
- Windows host-agent owned launch tracking and authenticated stop endpoint.
- Focused offline Python/Go coverage plus Windows runtime evidence or a
  provider-gap record.

### Acceptance
- As in the card Acceptance.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-31-remote-testclient-owned-lifecycle/`
- Root S50-090 coordination card.
- Archived predecessor cards:
  `remote-client-host-agent-testclient-launch`,
  `host-agent-launched-testclient-persistence`,
  `host-agent-testclient-launch-persistence-dwell`.

## Verify
- RED Python:
  `uv run --with pytest --with pyyaml pytest tests/test_display_backend.py::test_remote_testclient_stop_posts_lifecycle_handle tests/test_mcp_server.py::test_launch_test_client_remote_routes_to_host_agent_and_attaches tests/test_mcp_server.py::test_stop_test_client_remote_routes_to_host_agent tests/test_mcp_server.py::test_stop_test_client_remote_preserves_idempotent_final_state tests/test_mcp_server.py::test_stop_test_client_remote_refuses_attach_only_pid -q`
  -> failed before implementation with missing backend stop method, unowned
  remote launch, and local-only remote stop.
- RED Go:
  `go test ./... -run 'TestTestClient(StopStopsOwnedLaunchAndIsIdempotent|StopRefusesUnknownPIDWithoutKilling|StopRequiresAuth)$'`
  -> failed before implementation because `/testclient/stop` was absent and
  launch did not report ownership.
- GREEN Python:
  `uv run --with pytest --with pyyaml pytest tests/test_display_backend.py tests/test_mcp_server.py -q`
  -> 159 passed before review; 161 passed after the review-cycle rescue.
- Full Python:
  `uv run --with pytest --with pyyaml pytest -q`
  -> 866 passed before review; 868 passed after the review-cycle rescue.
- GREEN Go:
  `go test ./...` under `host-agent/windows-display-agent`
  -> passed before review and after the review-cycle rescue.
- Final Go:
  `go test -count=1 ./...` under `host-agent/windows-display-agent`
  -> passed after the broker/PID investigation.
- Review cycle 1:
  `.runtime/changerail/reviews/remote-testclient-owned-lifecycle.json`
  -> `no-go` with blockers R1 (legacy/protocol-compatible host-agent launch
  results were inferred as owned) and R2 (started-but-not-ready host-agent
  launches were not retained as owned cleanup records).
- Rescue RED Python:
  `uv run --with pytest --with pyyaml pytest tests/test_mcp_server.py::test_launch_test_client_remote_legacy_host_agent_result_stays_unowned tests/test_mcp_server.py::test_launch_test_client_remote_not_ready_exposes_cleanup_handle -q`
  -> failed before rescue: legacy launch result was inferred as owned, and
  not-ready launch failure did not expose `pid`/cleanup handle.
- Rescue RED Go:
  `go test ./... -run 'TestTestClientLaunchReportsNotListeningProcessInsteadOfReady$'`
  -> failed before rescue because a live not-listening process returned
  `owns_process=false` and had no lifecycle handle.
- Rescue GREEN:
  targeted rescue Python tests -> 2 passed; targeted not-listening Go test ->
  passed; `python3 -m compileall -q src/qa_mcp/mcp_server.py src/qa_mcp/protocol/display_backend.py`
  -> passed.
- Windows compile:
  `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-owned-lifecycle.test.exe .`
  -> passed.
- Windows live proof, original stop:
  `ssh "$QA_MCP_WINDOWS_USER@$QA_MCP_WINDOWS_HOST" powershell -NoProfile -ExecutionPolicy Bypass -File ...\live-proof.ps1`
  -> blocked on `HISTORICAL-LAB-HOST` against `C:\1C_BASES\demo10413`
  before any owned PID was returned. The retained bounded evidence is
  `.runtime/changerail/evidence/remote-testclient-owned-lifecycle/windows-live-proof-205.json`.
- Windows manual launch probe:
  a temporary scheduled task on `HISTORICAL-LAB-HOST` can launch the demo
  TestClient on a fresh TPort and cleanup the process; this isolates the
  earlier blocker to the host-agent broker/PID ownership path rather than the
  demo infobase or platform installation.
- Windows fake-platform lifecycle proof:
  `.runtime/changerail/evidence/remote-testclient-owned-lifecycle/windows-live-proof-fake-platform-205.json`
  also fails in the same broker/PID ownership phase before a listener appears,
  so the failure is not specific to real 1C credentials or infobase contents.
- Windows cleanup:
  read-only post-check on `HISTORICAL-LAB-HOST` confirmed no proof ports, no proof
  scheduled tasks, no `1cv8*` processes, and no temp proof stage remained.
- Windows broker/root-cause investigation:
  exact socket-broker probe on `HISTORICAL-LAB-HOST` proved the broker script,
  base64 JSON payload, PID acknowledgement, listener PID and `OpenProcess`
  all succeed when the proof script supplies the Cyrillic username through
  UTF-8 base64. Evidence:
  `.runtime/changerail/evidence/remote-testclient-owned-lifecycle/socket-broker-probe-205.json`.
- Windows proof fix:
  the failed live proof used a UTF-8-without-BOM PowerShell 5.1 script with
  embedded `Администратор`, which corrupted `/N` under the host code page.
  The proof script was changed to keep defaults ASCII-safe and reconstruct the
  username from UTF-8 base64. A source-bound dirty-local host-agent bundle
  (`sha256=e178aebf0741a9cf85a4d10b385465bce03f86e4824ee7f1db7a95796436c992`)
  then passed full launch/attach/status/stop/repeat-stop/post-stop absence on
  `.205`: sanitized evidence
  `.runtime/changerail/evidence/remote-testclient-owned-lifecycle/windows-live-proof-current-205-username-fixed.json`.
- Windows proof hardening:
  host-agent transient PowerShell helper scripts now set
  `$ProgressPreference = 'SilentlyContinue'` so first-use ScheduledTasks
  progress records do not appear as `#< CLIXML` stderr noise or unbounded
  launch diagnostics. Covered by
  `TestInteractiveTaskPowerShellScriptsSuppressProgressCLIXML`.
- Windows final cleanup:
  read-only post-check on `HISTORICAL-LAB-HOST` confirmed no listener on proof
  ports, no non-checker process with the proof `-TPort`, no temporary
  scheduled tasks, and no temporary stage directories.
- Final verification after proof fix:
  `go test -count=1 ./...` under `host-agent/windows-display-agent`
  -> passed (`ok qa-mcp-host-agent`, 16.461s).
- Final Python:
  `uv run --with pytest --with pyyaml pytest -q` -> 868 passed.
- Final OpenSpec:
  `openspec validate --all --strict` -> 19 passed, 0 failed.
- Final whitespace:
  `git diff --check` -> passed.
- Review cycle 2:
  `.runtime/changerail/reviews/remote-testclient-owned-lifecycle.json`
  -> `no-go` with blockers R1 (a consumed one-shot process-exit signal could
  leave a stale owned record able to terminate a PID-reused unrelated process)
  and R2 (retained proof JSONs still included raw host-agent log-tail data).
- Cycle 2 rescue RED/green:
  `go test -count=1 ./... -run 'Test(TestClientStopTreatsCompletedRecordAsStaleWithoutKilling|TestClientLaunchReportsEarlyExitInsteadOfReady|TestClientReadinessDoesNotTreatListeningPortAsAliveAfterExit|TestClientReadinessRequiresPortPersistenceDwell|TestClientReadinessDwellHonorsLaunchTimeout|TestClientLaunchReportsNotListeningProcessInsteadOfReady|TestClientStopStopsOwnedLaunchAndIsIdempotent|TestClientStopRefusesUnknownPIDWithoutKilling)$'`
  under `host-agent/windows-display-agent` -> passed after replacing the
  consumable process-exit channel with durable completion plus retained exact
  terminate callbacks.
- Rescue artifact build:
  `bin/ai-build-windows-host-agent build --output-dir .runtime/changerail/evidence/remote-testclient-owned-lifecycle/windows-host-agent-current --allow-dirty`
  -> rebuilt source-bound dirty-local bundle with
  `sha256=95b2622a198bac49947f2264a45020d1166b31b6eab938169981599dd410872f`.
- Windows live proof after cycle 2 rescue:
  `.runtime/changerail/evidence/remote-testclient-owned-lifecycle/windows-live-proof-current-205-rescue3.json`
  on `HISTORICAL-LAB-HOST` passed launch/attach/status/stop/repeat-stop/post-stop
  absence with the rebuilt bundle; retained cleanup evidence records only
  structured booleans and no raw host-agent log tail.
- Windows cleanup after cycle 2 rescue:
  read-only post-check on `HISTORICAL-LAB-HOST` confirmed no listener on proof
  ports `18114`/`15554`, no temporary scheduled task, and no temporary stage
  directory.
- Final Go after cycle 2 rescue:
  `go test -count=1 ./...` under `host-agent/windows-display-agent` -> passed
  (`ok qa-mcp-host-agent`, 16.575s).
- Final Python after cycle 2 rescue:
  `uv run --with pytest --with pyyaml pytest -q` -> 868 passed.
- Final artifact verify after cycle 2 rescue:
  `python3 tools/release/windows_host_agent_artifact.py verify --bundle-dir .runtime/changerail/evidence/remote-testclient-owned-lifecycle/windows-host-agent-current --allow-dirty`
  -> verified
  `sha256=95b2622a198bac49947f2264a45020d1166b31b6eab938169981599dd410872f`.
- Final OpenSpec after cycle 2 rescue:
  `openspec validate --all --strict` -> 19 passed, 0 failed.
- Final whitespace after cycle 2 rescue:
  `git diff --check` -> passed.
- Review cycle 3:
  `.runtime/changerail/reviews/remote-testclient-owned-lifecycle.json`
  -> `no-go` with blocker R1: lifecycle records were still keyed by PID, so a
  delayed PID-only stop after PID reuse could terminate a newer owned launch.
- Cycle 3 rescue focused Go:
  `go test -count=1 ./... -run 'Test(TestClientStop|TestClientLaunchReportsNotListeningProcessInsteadOfReady|TestClientLaunchResultIncludesInteractiveSessionMetadata|InteractiveHostAgentLaunchContextIsBounded)'`
  under `host-agent/windows-display-agent` -> passed after adding opaque
  lifecycle IDs and PID-reuse regressions.
- Cycle 3 rescue focused Python:
  `uv run --with pytest --with pyyaml pytest tests/test_display_backend.py::test_remote_testclient_stop_posts_lifecycle_handle tests/test_mcp_server.py::test_launch_test_client_remote_routes_to_host_agent_and_attaches tests/test_mcp_server.py::test_stop_test_client_remote_routes_to_host_agent tests/test_mcp_server.py::test_stop_test_client_remote_preserves_idempotent_final_state tests/test_mcp_server.py::test_stop_test_client_remote_refuses_attach_only_pid tests/test_mcp_server.py::test_stop_test_client_remote_refuses_pid_only_even_when_same_pid_is_active tests/test_mcp_server.py::test_stop_test_client_remote_refuses_mismatched_lifecycle_ids tests/test_mcp_server.py::test_launch_test_client_remote_not_ready_exposes_cleanup_handle -q`
  -> 8 passed.
- Cycle 3 rescue Python endpoint matrix:
  `uv run --with pytest --with pyyaml pytest tests/test_display_backend.py tests/test_mcp_server.py -q`
  -> 164 passed.
- Cycle 3 rescue compile:
  `python3 -m compileall -q src/qa_mcp/mcp_server.py src/qa_mcp/protocol/display_backend.py`
  -> passed; `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-lifecycle-handle.test.exe .`
  under `host-agent/windows-display-agent` -> passed.
- Final Go after cycle 3 rescue:
  `go test -count=1 ./...` under `host-agent/windows-display-agent` -> passed
  (`ok qa-mcp-host-agent`, 15.892s).
- Rescue artifact build after cycle 3:
  `bin/ai-build-windows-host-agent build --output-dir .runtime/changerail/evidence/remote-testclient-owned-lifecycle/windows-host-agent-current --allow-dirty`
  -> rebuilt source-bound dirty-local bundle with
  `sha256=d129c74d11178a0dfa393dbae11a5bf84a7321cb44f9d0047ac3479d106759bb`.
- Windows live proof after cycle 3 rescue:
  `.runtime/changerail/evidence/remote-testclient-owned-lifecycle/windows-live-proof-current-205-rescue5.json`
  on `HISTORICAL-LAB-HOST` passed host-agent `0.1.10-testclient-lifecycle-handle`
  launch/attach/status/stop-with-lifecycle-handle/repeat-stop/post-stop absence;
  retained evidence records lifecycle id presence booleans and no raw
  host-agent log tail.
- Windows cleanup after cycle 3 rescue:
  read-only post-check on `HISTORICAL-LAB-HOST` confirmed no listeners on proof
  ports `18116`/`15556`, no temporary scheduled task, and no temporary stage
  directory.
- Final Python after cycle 3 rescue:
  `uv run --with pytest --with pyyaml pytest -q` -> 871 passed.
- Final artifact verify after cycle 3 rescue:
  `python3 tools/release/windows_host_agent_artifact.py verify --bundle-dir .runtime/changerail/evidence/remote-testclient-owned-lifecycle/windows-host-agent-current --allow-dirty`
  -> verified
  `sha256=d129c74d11178a0dfa393dbae11a5bf84a7321cb44f9d0047ac3479d106759bb`.
- Final OpenSpec after cycle 3 rescue:
  `openspec validate --all --strict` -> 19 passed, 0 failed.
- Final whitespace after cycle 3 rescue:
  `git diff --check` -> passed.
- Review cycle 4:
  `.runtime/changerail/reviews/remote-testclient-owned-lifecycle.json`
  -> `no-go` with blocker R1: remote stop could still dispatch an opaque
  lifecycle handle to a protocol-compatible `0.1.9` host-agent whose stop route
  ignored unknown lifecycle fields and remained PID-only.
- Cycle 4 rescue focused Python:
  `uv run --with pytest --with pyyaml pytest tests/test_display_backend.py::test_testclient_lifecycle_stop_support_is_capability_specific tests/test_display_backend.py::test_remote_testclient_stop_posts_lifecycle_handle tests/test_display_backend.py::test_remote_testclient_stop_rejects_protocol_compatible_pid_only_lifecycle_route tests/test_mcp_server.py::test_stop_test_client_remote_routes_to_host_agent tests/test_mcp_server.py::test_stop_test_client_remote_refuses_pid_only_even_when_same_pid_is_active tests/test_mcp_server.py::test_stop_test_client_remote_refuses_mismatched_lifecycle_ids tests/test_mcp_server.py::test_stop_test_client_remote_reports_unsupported_lifecycle_host_agent -q`
  -> 7 passed.
- Cycle 4 rescue Python endpoint matrix:
  `uv run --with pytest --with pyyaml pytest tests/test_display_backend.py tests/test_mcp_server.py -q`
  -> 167 passed.
- Cycle 4 rescue compile/static:
  `python3 -m compileall -q src/qa_mcp/mcp_server.py src/qa_mcp/protocol/display_backend.py`
  -> passed; `openspec validate --all --strict` -> 19 passed, 0 failed;
  `git diff --check` -> passed.
- Final Python after cycle 4 rescue:
  `uv run --with pytest --with pyyaml pytest -q` -> 874 passed.
- Final Go after cycle 4 rescue:
  `go test -count=1 ./...` under `host-agent/windows-display-agent` -> passed
  (`ok qa-mcp-host-agent`, 16.714s).
- Final artifact verify after cycle 4 rescue:
  `python3 tools/release/windows_host_agent_artifact.py verify --bundle-dir .runtime/changerail/evidence/remote-testclient-owned-lifecycle/windows-host-agent-current --allow-dirty`
  -> verified the unchanged Windows host-agent binary
  `sha256=d129c74d11178a0dfa393dbae11a5bf84a7321cb44f9d0047ac3479d106759bb`.
  The retained cycle-3 Windows proof remains source-relevant because cycle-4
  rescue changed only Python compatibility fail-closed behavior before posting
  stop to legacy host-agents.
- Windows target note:
  `User@192.0.2.200` was reachable as `HISTORICAL-LAB-HOST` but lacked known
  file-infobase markers for `demo10413`, `demo_1_0_41_3`, `private-lab-infobase`, and
  `vanessa_client`; failed probe evidence is retained at
  `.runtime/changerail/evidence/remote-testclient-owned-lifecycle/windows-live-proof.json`.
- OpenSpec:
  `openspec validate remote-testclient-owned-lifecycle --strict` -> passed.
- OpenSpec all:
  before archive, `openspec validate --all --strict` -> 20 passed, 0 failed;
  after archive, `openspec validate --all --strict` -> 19 passed, 0 failed.
- Archive:
  `openspec archive remote-testclient-owned-lifecycle --yes --skip-specs`
  -> archived as `2026-07-31-remote-testclient-owned-lifecycle`.
- Whitespace:
  `git -C qa-mcp diff --check` -> passed.

## Result
Published in the scoped ChangeRail delivery commit.

Independent review cycle 5 recorded `go` with 6/6 acceptance criteria passed,
0 blockers, and one non-blocking major follow-up: `RemoteAgentBackend.handshake`
drops advertised `/version` capabilities, so a future protocol-compatible
host-agent that explicitly advertises lifecycle-handle stop support would still
be refused. Current `0.1.10-testclient-lifecycle-handle` behavior and the
`0.1.9` fail-closed safety fix are unaffected.

## Next
- Track the review-cycle-5 major finding as a separate follow-up card.

## Log
- 2026-07-31 created from root S50-090 during `$changerail-deliver --no-push`.
- 2026-07-31T05:12:52Z delivery started from root S50-090.
- 2026-07-31 implemented owned remote TestClient lifecycle routing, host-agent
  `/testclient/stop`, offline regression tests, spec sync, and Windows live
  proof.
- 2026-07-31 archived OpenSpec change after completed tasks and strict
  validation.
- 2026-07-31 independent review cycle 1 returned `no-go`; fixed R1/R2 by
  requiring explicit host-agent ownership, preserving cleanup handles for live
  readiness-failed launches, and adding rescue regressions.
- 2026-07-31 stopped before review cycle 2 because the Windows live proof
  is blocked in the host-agent broker before an owned TestClient PID exists;
  cleanup on `HISTORICAL-LAB-HOST` verified clean.
- 2026-07-31 resolved the Windows proof blocker: the proof script embedded a
  Cyrillic username in UTF-8 without BOM, which Windows PowerShell 5.1 decoded
  through the host code page. Reworked the proof input to reconstruct the
  username from UTF-8 base64, suppressed PowerShell progress CLIXML in
  transient task helper scripts, rebuilt the host-agent, and retained green
  `.205` launch/attach/stop/post-stop evidence.
- 2026-07-31 independent review cycle 2 returned `no-go`; fixed the stale
  completion/PID-reuse safety gap with durable process completion and retained
  exact terminate callbacks, removed raw host-agent log tails from retained
  proof evidence, rebuilt the Windows host-agent bundle, and retained a new
  green `.205` proof.
- 2026-07-31 independent review cycle 3 returned `no-go`; fixed the remaining
  PID-reuse blocker by requiring an opaque host-agent lifecycle handle id for
  remote stop, preserving same-PID tombstones by lifecycle id, adding Go/Python
  PID-only and mismatched-handle refusal regressions, rebuilding host-agent
  `0.1.10`, and retaining a new green `.205` proof.
- 2026-07-31 independent review cycle 4 returned `no-go`; fixed the
  protocol-compatible `0.1.9` PID-only stop route by making remote TestClient
  stop capability-specific and refusing unsupported lifecycle-stop host-agents
  before posting `/testclient/stop`.
- 2026-07-31 independent review cycle 5 returned `go` with one non-blocking
  major follow-up for future advertised capability passthrough.
- 2026-07-31 `$changerail-pub`: committed scoped card delivery after fresh
  `go` review and prepared push to `origin/main`.
