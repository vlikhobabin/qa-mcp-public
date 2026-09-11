## 1. OpenSpec And Planning

- [x] 1.1 Create proposal, design, delta spec and tasks for
  `host-agent-testclient-persistence-fresh-session-context`.
- [x] 1.2 Run `openspec validate host-agent-testclient-persistence-fresh-session-context --strict`
  and `git diff --check -- openspec/changes/host-agent-testclient-persistence-fresh-session-context openspec/board`.
- [x] 1.3 Run the 1C verification matrix checker in preflight mode and retain
  output under `.artifacts/openspec/host-agent-testclient-persistence-fresh-session-context/20260708T121735Z/`.

## 2. Test-First Host-Agent Launch Plumbing

- [x] 2.1 Add RED Go coverage for bounded launch-context metadata that
  distinguishes direct `exec` from an interactive-session launch method.
- [x] 2.2 Add RED Go coverage for structured fail-closed behavior when the
  Windows interactive session token cannot be prepared where this is testable
  offline.
- [x] 2.3 Record the RED command and one-line failure summary in verification
  notes or retained artifacts.

## 3. Implementation

- [x] 3.1 Introduce a small host-agent TestClient process launcher boundary so
  common request validation, redaction and readiness classification remain
  unchanged.
- [x] 3.2 Keep the non-Windows launcher on the existing `exec` path for Linux
  tests and all-in-one behavior.
- [x] 3.3 Implement the Windows launcher with active console session discovery,
  `WTSQueryUserToken`, `DuplicateTokenEx`, `CreateProcessAsUserW`, an
  interactive desktop of `winsta0\\default`, a Unicode environment block and a
  wait channel backed by the process handle.
- [x] 3.4 Return bounded launch-context metadata including launch method,
  environment key names and session id when available, without exposing token
  handles, raw environment values or secrets.
- [x] 3.5 Bump the host-agent version and Python default compatibility set for
  the interactive-session launch contract.

## 4. Runtime Gap Evidence

- [x] 4.1 Retain an artifact recording the unavailable Windows .205 persistence
  proof as a qa-mcp provider gap with owner
  `/opt/ai-dev-suite-for-1c/qa-mcp`.
- [x] 4.2 Do not run or fabricate the real Windows persistence proof in this
  environment.

## 5. Verification And Handoff

- [x] 5.1 Run focused Go tests for TestClient launch plumbing.
- [x] 5.2 Run full `go test ./...` under `host-agent/windows-display-agent`.
- [x] 5.3 Run `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-fresh-session.test.exe .`
  under `host-agent/windows-display-agent`.
- [x] 5.4 Run `openspec validate host-agent-testclient-persistence-fresh-session-context --strict`
  and `git diff --check`.
- [x] 5.5 Run the matrix checker in archive-gate mode and retain output under
  `.artifacts/openspec/host-agent-testclient-persistence-fresh-session-context/20260708T121735Z/`.
- [x] 5.6 Sync the `qa-mcp-windows-host-agent-security` delta spec into the main
  spec and run scoped plus all-spec validation.
- [x] 5.7 Archive the change after tasks, verification and spec sync are
  complete.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | host-agent-launched Windows TestClient on .205 [redacted third-party configuration] | Real-host smoke: launch through running host-agent, wait >60s, confirm `V8TopLevelFrameSDI`, TPort reachable from container, then protocol read attach | Sanitized smoke transcript or provider-gap report | `.artifacts/openspec/host-agent-testclient-persistence-fresh-session-context/20260708T121735Z/windows-host-persistence-provider-gap.md` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Real Windows .205 host unavailable in this session; runtime persistence remains unproven. |
| Delivery or runtime apply | Windows host-agent `/testclient/launch` process creation | Go unit tests for launch method metadata, launcher boundary behavior, fail-closed token/session errors where feasible, and Windows cross-compile | `go test ./...` output, focused test output and Windows cross-compile summary | `.artifacts/openspec/host-agent-testclient-persistence-fresh-session-context/20260708T121735Z/host-agent-fresh-session-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Offline tests cannot prove real GUI persistence. |
| Native protocol claim | TestClient wire frames and replay templates | No protocol semantic change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No new native TestClient protocol claim is made. | None for corpus coverage. |
| Business data mutation | Object writes, posting, delete/fill/import/export | No business mutation is part of this lifecycle change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change launches/attaches to TestClient and checks liveness only. | None beyond process availability. |

## Provider Gap Records

| provider_id | owner_path | matrix_row | missing_evidence_type | impact | current_workaround | source_card | sanitized_evidence | sensitivity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| qa-mcp | `/opt/ai-dev-suite-for-1c/qa-mcp` | QA/TestClient UI automation | qa_testclient_bundle | Blocks proof that a host-agent-launched `/TESTCLIENT` on the real Windows .205 [redacted third-party configuration] host persists >60s with a visible `V8TopLevelFrameSDI` and reachable TPort after the fresh-session launch change. | Operator can run the retained Windows-host smoke later on the real host and replace this provider-gap artifact with a sanitized proof bundle. | `openspec/board/2.todo/host-agent-testclient-persistence-fresh-session-context.md` | `.artifacts/openspec/host-agent-testclient-persistence-fresh-session-context/20260708T121735Z/windows-host-persistence-provider-gap.md` | no credentials, screenshots or live data copied |

## Verification Notes

- Matrix preflight:
  `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py openspec/changes/host-agent-testclient-persistence-fresh-session-context/tasks.md --workspace . --mode preflight --output .artifacts/openspec/host-agent-testclient-persistence-fresh-session-context/20260708T121735Z/matrix-preflight.json --json`
  passed with 4 matrix rows and 1 explicit provider gap.
- RED Go:
  `cd host-agent/windows-display-agent && go test ./... -run "TestTestClientLaunch(ResultIncludesInteractiveSessionMetadata|ContextFailureDoesNotFallbackToDirectExec)"`
  failed before implementation with undefined launch-context and launcher seam
  symbols; retained at
  `.artifacts/openspec/host-agent-testclient-persistence-fresh-session-context/20260708T121735Z/host-agent-fresh-session-tests.md`.
- GREEN Go focused:
  `cd host-agent/windows-display-agent && go test ./... -run "TestTestClientLaunch(ResultIncludesInteractiveSessionMetadata|ContextFailureDoesNotFallbackToDirectExec)"`
  passed.
- GREEN Go full: `cd host-agent/windows-display-agent && go test ./...` passed
  with `ok qa-mcp-host-agent 7.953s`.
- GREEN Windows cross-compile:
  `cd host-agent/windows-display-agent && GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-fresh-session.test.exe .`
  passed.
- GREEN Python compatibility:
  `uv run --with pytest --with pyyaml pytest tests/test_display_backend.py -k 'remote_handshake_accepts_default_compatible_versions or remote_handshake_accepts_focus_independent_host_agent_version or remote_handshake_sha_pin_still_exact'`
  passed with 9 selected tests.
- Runtime provider gap:
  `.artifacts/openspec/host-agent-testclient-persistence-fresh-session-context/20260708T121735Z/windows-host-persistence-provider-gap.md`
  records that the real Windows .205 persistence proof was not run because the
  host is unavailable here. Runtime persistence remains unproven.
- Minimum OpenSpec verification:
  `openspec status --change host-agent-testclient-persistence-fresh-session-context --json`,
  `openspec instructions apply --change host-agent-testclient-persistence-fresh-session-context --json`,
  `openspec validate host-agent-testclient-persistence-fresh-session-context --strict`
  and `git diff --check` passed.
- Matrix archive gate:
  `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py openspec/changes/host-agent-testclient-persistence-fresh-session-context/tasks.md --workspace . --mode archive --output .artifacts/openspec/host-agent-testclient-persistence-fresh-session-context/20260708T121735Z/matrix-archive-gate.json --json`
  passed with 4 matrix rows and 1 explicit provider gap.
- Suite regression: `uv run --with pytest --with pyyaml pytest` passed with
  790 tests, retained at
  `.artifacts/ai-run/trc_6ccd68f813bd4cd692e589a48a622313/run_2ce01e9d338e4e6cb0d9cd41b97d420c/`.
- Suite drift gate: component-local `scripts/check_suite_source_of_truth_drift.py`
  is absent, so the suite fallback
  `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/check_suite_source_of_truth_drift.py`
  was run and passed, retained at
  `.artifacts/ai-run/trc_6ccd68f813bd4cd692e589a48a622313/run_e0c5d350246a4ddeacf8f398c2c99409/`.
- Suite smoke: `uv run --with pytest --with pyyaml pytest -m smoke` passed with
  3 selected tests, retained at
  `.artifacts/ai-run/trc_6ccd68f813bd4cd692e589a48a622313/run_bbbdc92e15c6411ab07d0248f070b841/`.
- Main spec sync validations passed for
  `openspec validate qa-mcp-windows-host-agent-security --strict` and
  `openspec validate --all`.
