## 1. Formalize Existing Implementation

- [x] 1.1 Confirm the existing `RemoteAgentBackend` diff threads a per-call
  timeout through `_request()` and `_json()`.
- [x] 1.2 Confirm `launch_test_client` posts `/testclient/launch` with
  `timeout_seconds + LAUNCH_HTTP_TIMEOUT_MARGIN` and does not shorten a longer
  configured host-agent timeout.
- [x] 1.3 Confirm non-launch host-agent primitives still use the default
  `host_agent_timeout` unless they explicitly pass a per-call timeout.

## 2. Regression Coverage

- [x] 2.1 Confirm the existing launch-payload test asserts the extended launch
  timeout at the `_json()` boundary.
- [x] 2.2 Confirm
  `test_remote_testclient_launch_uses_extended_http_timeout` asserts the
  launch timeout at the `_request()` boundary is greater than the default and
  covers the readiness wait.

## 3. Spec Sync And Verification

- [x] 3.1 Sync the `qa-mcp-tool-endpoint-contract` delta into the main spec.
- [x] 3.2 Run focused pytest coverage for remote TestClient launch timeout
  behavior.
- [x] 3.3 Run the full pytest suite for this repository.
- [x] 3.4 Run OpenSpec validation and `git diff --check`.
- [x] 3.5 Archive the change after tasks, verification and spec sync are
  complete.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | Python remote `launch_test_client` to Windows host-agent `/testclient/launch` on real `.205` / [redacted third-party configuration] host | Record live before/after launch observation from the same default-timeout path | Sanitized runtime evidence summary in this file | `openspec/changes/archive/2026-07-08-remote-launch-http-timeout-covers-readiness-wait/tasks.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Live proof is summarized from the discovery session rather than replayed in this delivery run. |
| Delivery or runtime apply | Python HTTP timeout routing for host-agent launch call | Focused pytest that captures the timeout passed to `_request` / `_json` | `uv run --with pytest --with pyyaml pytest tests/test_display_backend.py -k 'remote_testclient_launch'` output | `.artifacts/ai-run/trc_d773f3c1678b4cccbee4b788145570f9/run_a4af4e1b17dd479c96ea270900605f20/` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Mocked test proves client-side timeout routing, not host GUI readiness. |
| Native protocol claim | TestClient wire frames and replay templates | No protocol semantic change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | This change modifies host-agent HTTP timeout selection only. | None for corpus coverage. |
| Business data mutation | Object writes, posting, delete/fill/import/export | No business mutation is part of this lifecycle timeout change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change launches/attaches to TestClient and does not execute business commands. | None beyond process availability. |

## Verification Notes

- RED pytest ordering: skipped by operator constraint. The fix was already
  implemented during live `.205` E2E discovery before this OpenSpec change was
  opened. Do not fabricate a separate RED run.
- Live regression proof before the fix: remote `launch_test_client` with
  default `host_agent_timeout` failed with `TimeoutError: timed out` while the
  host-agent launch was still waiting to return readiness.
- Live regression proof after the fix: the same default-timeout launch on the
  real `.205` / [redacted third-party configuration] host returned the host-agent readiness verdict in
  about 3 seconds.
- Code review confirmation: `src/qa_mcp/protocol/display_backend.py` defines
  `LAUNCH_HTTP_TIMEOUT_MARGIN = 15.0`, threads optional `timeout` through
  `_request()` and `_json()`, computes `request_timeout = self.timeout if
  timeout is None else max(self.timeout, float(timeout))`, and only passes the
  extended timeout from `RemoteAgentBackend.launch_test_client()`.
- Focused pytest: `uv run --with pytest --with pyyaml pytest
  tests/test_display_backend.py -k 'remote_testclient_launch'` passed with
  `2 passed, 21 deselected`; retained at
  `.artifacts/ai-run/trc_d773f3c1678b4cccbee4b788145570f9/run_a4af4e1b17dd479c96ea270900605f20/`.
- Full pytest: `uv run --with pytest --with pyyaml pytest` passed with
  `788 passed`; retained at
  `.artifacts/ai-run/trc_d773f3c1678b4cccbee4b788145570f9/run_baf56eefc2ed478f98b5f024a987d9e6/`.
- Suite drift: `python3
  /opt/ai-dev-suite-for-1c/agent-core/scripts/check_suite_source_of_truth_drift.py`
  passed with `result: OK (0 finding(s))`; retained at
  `.artifacts/ai-run/trc_d773f3c1678b4cccbee4b788145570f9/run_b21a2efbe19f4ee0b69dd41751a4d73d/`.
- Smoke gate: `uv run --with pytest --with pyyaml pytest -m smoke` passed with
  `3 passed, 785 deselected`; retained at
  `.artifacts/ai-run/trc_d773f3c1678b4cccbee4b788145570f9/run_3ac672f7240644c8870bc16091932f60/`.
- Matrix preflight initially passed with a warning for the placeholder pytest
  evidence path; archive gate initially failed until this file was updated with
  the concrete focused pytest evidence path.
- Matrix archive gate: `python3
  /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py
  openspec/changes/remote-launch-http-timeout-covers-readiness-wait/tasks.md
  --workspace . --mode archive --output
  .artifacts/openspec/remote-launch-http-timeout-covers-readiness-wait/20260708T091225Z/matrix-archive-gate.json
  --json` passed with `ok: true`.
- Spec validation: `openspec validate qa-mcp-tool-endpoint-contract --strict`
  passed; retained at
  `.artifacts/ai-run/trc_d773f3c1678b4cccbee4b788145570f9/run_d4d7c1c6bdc34da092aea34974e57bb3/`.
- Change validation: `openspec validate
  remote-launch-http-timeout-covers-readiness-wait --strict` passed; retained at
  `.artifacts/ai-run/trc_d773f3c1678b4cccbee4b788145570f9/run_07a531277f7a431482382432c0c15353/`.
- Workspace validation: `openspec validate --all` passed with `14 passed, 0
  failed`; retained at
  `.artifacts/ai-run/trc_d773f3c1678b4cccbee4b788145570f9/run_4104362afdc242afad5f35596baa143d/`.
- Diff whitespace: `git diff --check` passed.
- Post-archive matrix gate: `python3
  /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py
  openspec/changes/archive/2026-07-08-remote-launch-http-timeout-covers-readiness-wait/tasks.md
  --workspace . --mode archive --output
  .artifacts/openspec/remote-launch-http-timeout-covers-readiness-wait/20260708T091225Z/matrix-archive-gate.post-archive.json
  --json` passed with `ok: true`.
