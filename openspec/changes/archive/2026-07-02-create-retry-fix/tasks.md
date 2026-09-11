## 1. Implementation

- [x] 1.1 Replace the dead `foreground_method == "create_splice"` guard with actual production create/list foreground
  method handling, or remove the dead retry branch entirely.
- [x] 1.2 Keep the retry one-shot and scoped to first-screenshot foreground/render races.
- [x] 1.3 Ensure result items populate `activation_retry` when the retry path runs.

## 2. Offline Tests

- [x] 2.1 Add a `tests/test_mcp_server.py` case where the first screenshot misses a create-form label and the second
  attempt locates it after activation.
- [x] 2.2 Assert the result includes `activation_retry` for the retried item.
- [x] 2.3 Assert no production branch depends exclusively on `create_splice`.

## 3. Live Verification

- [x] 3.1 Include this path in the card-level `python -m qa_mcp.regression --include-write` smoke where feasible.
- [x] 3.2 Retain offline and live summaries under `.artifacts/openspec/create-retry-fix/2026-07-02/`.

Evidence: `.artifacts/openspec/create-retry-fix/2026-07-02/live-regression/20260702T054219Z/report.txt` reports GREEN
8/8; focused offline tests simulate the first-screenshot miss and verify `activation_retry`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient managed form label write | `write_form_fields_by_label` create-form activation retry | Offline simulated first-screenshot miss with retry; card-level live write regression remains the final smoke | `source_preflight`, `qa_testclient_scenario`, `scenario_log` | `.artifacts/openspec/create-retry-fix/2026-07-02/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| BSL diagnostics | no BSL files changed | N/A because this change edits Python MCP/server code only | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/bsl-mcp` | no BSL module is modified | no BSL behavioral surface |
