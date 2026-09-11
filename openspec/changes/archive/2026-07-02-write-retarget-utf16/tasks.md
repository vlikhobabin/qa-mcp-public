## 1. Implementation

- [x] 1.1 Replace ASCII-only native write field retargeting with the ASCII/UTF-16 helper for form writes, table-cell
  writes and choice/date paths that retarget `EditField` leaves.
- [x] 1.2 Mark only known commit/focus-change frames as allowed missing-leaf cases.
- [x] 1.3 Return a structured `retarget_failed` result before sending an expected frame whose target leaf cannot be
  retargeted.

## 2. Offline Tests

- [x] 2.1 Add a frame-level test proving a UTF-16LE Cyrillic `EditField` leaf changes from the base field to the target
  field in a write SET frame.
- [x] 2.2 Add a missing-leaf failure test proving the unsafe frame is not sent.
- [x] 2.3 Keep existing focus-change and table-cell write tests green.

## 3. Live Verification

- [x] 3.1 Run the card-level live write regression after all CR-03 changes:
  `python -m qa_mcp.regression --include-write`.
- [x] 3.2 Retain the regression summary under `.artifacts/openspec/write-retarget-utf16/2026-07-02/` and record the
  platform version in the card.

Evidence: `.artifacts/openspec/write-retarget-utf16/2026-07-02/live-regression/20260702T054219Z/report.txt` reports
GREEN 8/8 on platform 8.3.27.2130, including `ui.write_by_label` and `data_post.write_persisted`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient protocol write | `NativeWriteSession.write`, `set_table_cell`, field leaf retargeting | Offline UTF-16 frame retarget tests plus live write regression row for a Cyrillic field | `source_preflight`, `qa_testclient_scenario`, `scenario_log`, `data_assertion` | `.artifacts/openspec/write-retarget-utf16/2026-07-02/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| BSL diagnostics | no BSL files changed | N/A because this change edits Python protocol code only | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/bsl-mcp` | no BSL module is modified | no BSL behavioral surface |
