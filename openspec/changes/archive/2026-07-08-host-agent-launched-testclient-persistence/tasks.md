## 1. Host-Agent Launch Context And Readiness

- [x] 1.1 Add failing Go coverage for bounded TestClient launch-context
  environment construction.
- [x] 1.2 Add failing Go coverage for early-exit, not-listening and ready
  launch classifications.
- [x] 1.3 Implement the bounded GUI child environment for host-agent-spawned
  TestClient processes without exposing raw environment values in responses.
- [x] 1.4 Implement launch wait/classification so `/testclient/launch` returns
  success only for live process plus listening TPort, and structured failures
  for early exit or not-listening timeout.
- [x] 1.5 Implement `/testclient/status` PID liveness reporting and keep TPort
  reporting independent from process liveness.
- [x] 1.6 Bump host-agent version and Python default compatibility for the
  honest-readiness contract.

## 2. Python Remote-Client Launch Contract

- [x] 2.1 Add failing pytest coverage showing a host-agent
  `testclient-exited-early` response is returned by `launch_test_client` as a
  structured failure with no active attachment.
- [x] 2.2 Add failing pytest coverage showing a host-agent
  `testclient-not-listening` response is returned as a structured failure with
  no active attachment.
- [x] 2.3 Add or adjust pytest coverage so successful remote launch still
  requires the container-side TPort probe before recording `attached:true`.
- [x] 2.4 Implement Python remote-client handling so host-agent readiness
  errors are preserved and the active attachment is recorded only after both
  host-agent and container liveness pass.
- [x] 2.5 Confirm existing local Linux/Xvfb launch behavior remains unchanged.

## 3. Runtime Gap Evidence

- [x] 3.1 Retain an artifact recording the unavailable Windows .205 runtime
  persistence proof as a qa-mcp provider gap with owner
  `/opt/ai-dev-suite-for-1c/qa-mcp`.
- [x] 3.2 Retain focused Go and pytest command summaries under
  `.artifacts/openspec/host-agent-launched-testclient-persistence/20260708T063311Z/`.
- [x] 3.3 Run the 1C verification matrix checker in preflight and archive-gate
  modes, retaining outputs under the same artifact root.

## 4. Verification And OpenSpec Handoff

- [x] 4.1 Run focused Go tests for the host-agent launch/status behavior.
- [x] 4.2 Run focused pytest tests for remote-client launch behavior and local
  launch regression coverage.
- [x] 4.3 Run `go test ./...` under `host-agent/windows-display-agent`.
- [x] 4.4 Run `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-persistence.test.exe .`
  under `host-agent/windows-display-agent`.
- [x] 4.5 Run `openspec validate host-agent-launched-testclient-persistence --strict`
  and `git diff --check`.
- [x] 4.6 Sync the `qa-mcp-windows-host-agent-security` and
  `qa-mcp-tool-endpoint-contract` requirement deltas into main specs.
- [x] 4.7 Archive the change after tasks, verification and spec sync are
  complete.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | host-agent-launched Windows TestClient on .205 [redacted third-party configuration] | Real-host smoke: launch through running host-agent, wait >60s, confirm `V8TopLevelFrameSDI`, TPort reachable from container, then protocol read attach | Sanitized smoke transcript or provider-gap report | `.artifacts/openspec/host-agent-launched-testclient-persistence/20260708T063311Z/windows-host-persistence-provider-gap.md` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Real host unavailable in this session; runtime persistence remains unproven. |
| Delivery or runtime apply | Windows host-agent `/testclient/launch` and `/testclient/status` | Go unit tests for environment construction, early-exit/not-listening/ready classification, status liveness and redaction | `go test ./...` output and retained summary | `.artifacts/openspec/host-agent-launched-testclient-persistence/20260708T063311Z/host-agent-launch-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Offline process fakes cannot prove real GUI persistence. |
| QA/TestClient UI automation | Python remote-client `launch_test_client` attachment behavior | Pytest coverage for host-agent early-exit propagation, host-agent success plus container TPort proof, and unchanged local launch path | `pytest` output and retained summary | `.artifacts/openspec/host-agent-launched-testclient-persistence/20260708T063311Z/python-remote-launch-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Offline tests prove classification and routing, not real Windows GUI state. |
| Native protocol claim | TestClient wire frames and replay templates | No protocol semantic change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No new native TestClient protocol claim is made. | None for corpus coverage. |
| Business data mutation | Object writes, posting, delete/fill/import/export | No business mutation is part of this lifecycle change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change launches/attaches to TestClient and checks liveness only. | None beyond process availability. |

## Provider Gap Records

| provider_id | owner_path | matrix_row | missing_evidence_type | impact | current_workaround | source_card | sanitized_evidence | sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qa-mcp | `/opt/ai-dev-suite-for-1c/qa-mcp` | QA/TestClient UI automation | qa_testclient_bundle | Blocks proof that a host-agent-launched `/TESTCLIENT` on the real Windows .205 [redacted third-party configuration] host persists >60s with a visible `V8TopLevelFrameSDI` and reachable TPort. | Operator can run the retained Windows-host smoke later on the real host and replace this provider-gap artifact with a sanitized proof bundle. | `openspec/board/2.todo/host-agent-launched-testclient-persistence.md` | `.artifacts/openspec/host-agent-launched-testclient-persistence/20260708T063311Z/windows-host-persistence-provider-gap.md` | no credentials, screenshots or live data copied |

## Verification Notes

- RED Go: `cd host-agent/windows-display-agent && go test ./... -run "TestTestClientLaunch(ContextRepairsScheduledTaskEnvironment|ReportsEarlyExitInsteadOfReady|ReportsNotListeningProcessInsteadOfReady|ReportsReadyOnlyWhenProcessAndPortLive)|TestTestClientStatusReportsPIDLiveness"` failed before implementation with `undefined: testClientLaunchEnvironment`; retained at `.artifacts/ai-run/trc_e5293e75e83a4862aa9d819228f4f3d3/run_bf3cf775520445bf8d7d7b4325cda48b/`.
- GREEN Go focused: `cd host-agent/windows-display-agent && go test ./... -run "TestTestClientLaunch(ContextRepairsScheduledTaskEnvironment|ReportsEarlyExitInsteadOfReady|ReportsNotListeningProcessInsteadOfReady|ReportsReadyOnlyWhenProcessAndPortLive)|TestTestClientStatusReportsPIDLiveness|TestVersionAndHealth"` passed; retained at `.artifacts/ai-run/trc_e5293e75e83a4862aa9d819228f4f3d3/run_14c995413a1f4a88b9662a6bb200637f/`.
- RED pytest: `uv run --with pytest --with pyyaml pytest tests/test_mcp_server.py -k 'launch_test_client_remote_preserves_host_agent_not_ready or launch_test_client_remote_requires_container_reachability_after_host_ready'` failed before implementation with `DisplayBackendError.__init__() got an unexpected keyword argument 'payload'`; retained at `.artifacts/ai-run/trc_e5293e75e83a4862aa9d819228f4f3d3/run_781ec03580364eb7956fefa0a925b9dc/`.
- GREEN pytest focused: `uv run --with pytest --with pyyaml pytest tests/test_mcp_server.py tests/test_display_backend.py -k 'launch_test_client_remote_preserves_host_agent_not_ready or launch_test_client_remote_requires_container_reachability_after_host_ready or remote_handshake_accepts_default_compatible_versions or remote_testclient_launch_posts_semantic_payload'` passed with 10 selected tests; retained at `.artifacts/ai-run/trc_e5293e75e83a4862aa9d819228f4f3d3/run_8b95541e928444378eed3b678433793b/`.
- FINAL Go focused: `cd host-agent/windows-display-agent && go test ./... -run "TestTestClientLaunch(ContextRepairsScheduledTaskEnvironment|ReportsEarlyExitInsteadOfReady|ReportsNotListeningProcessInsteadOfReady|ReportsReadyOnlyWhenProcessAndPortLive|StartsDetachedAndRedactsSecrets)|TestTestClientReadinessDoesNotTreatListeningPortAsAliveAfterExit|TestTestClientStatusReportsPIDLiveness|TestVersionAndHealth"` passed with `ok qa-mcp-host-agent 1.557s`.
- FINAL Go full: `cd host-agent/windows-display-agent && go test ./...` passed with `ok qa-mcp-host-agent 7.798s`.
- FINAL Windows cross-compile: `cd host-agent/windows-display-agent && GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-persistence.test.exe .` passed.
- FINAL pytest focused: `uv run --with pytest --with pyyaml pytest tests/test_mcp_server.py tests/test_display_backend.py -k 'launch_test_client_remote or remote_handshake_accepts_default_compatible_versions or remote_testclient_launch_posts_semantic_payload'` passed with `12 passed, 115 deselected in 1.20s`.
- Matrix preflight and archive checks passed with one explicit provider gap; retained at `.artifacts/openspec/host-agent-launched-testclient-persistence/20260708T063311Z/matrix-preflight.json` and `.artifacts/openspec/host-agent-launched-testclient-persistence/20260708T063311Z/matrix-archive-gate.json`.
- Main spec sync validations passed for `qa-mcp-windows-host-agent-security`, `qa-mcp-tool-endpoint-contract`, and `openspec validate --all`.
- `git diff --check` passed after implementation and spec sync.
- Runtime Windows persistence proof was not run. The retained provider gap is `.artifacts/openspec/host-agent-launched-testclient-persistence/20260708T063311Z/windows-host-persistence-provider-gap.md`.
