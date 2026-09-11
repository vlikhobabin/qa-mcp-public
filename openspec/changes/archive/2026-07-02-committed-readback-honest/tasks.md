## 1. Implementation

- [x] 1.1 Widen `read_field_value_near` or factor a replacement extractor so it decodes Cyrillic, 1-character and
  >40-byte target-field values.
- [x] 1.2 Replace generic `readback.startswith(value)` commit checks in `NativeWriteSession.write` and table-cell write
  paths with a normalized target-field match helper.
- [x] 1.3 Preserve only documented type-specific formatting tolerance, such as date read-back with a time suffix.

## 2. Offline Tests

- [x] 2.1 Add false-positive coverage for requested `"123"` and read-back `"123456"`.
- [x] 2.2 Add read-back fixtures for a Cyrillic value, a one-character value and a value longer than 40 bytes.
- [x] 2.3 Run `uv run pytest tests/test_native_write.py -q`.

## 3. Live Verification

- [x] 3.1 Run the card-level live write regression after all CR-03 changes:
  `python -m qa_mcp.regression --include-write`.
- [x] 3.2 Retain the regression summary under `.artifacts/openspec/committed-readback-honest/2026-07-02/` and record
  exact/normalized commit evidence in the card.

Evidence: `.artifacts/openspec/committed-readback-honest/2026-07-02/live-regression/20260702T054219Z/report.txt`
reports GREEN 8/8; focused offline tests cover exact/normalized matching for Cyrillic, one-character, long and prefix
non-commit read-backs.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient protocol write verification | native write read-back extraction and `committed` matching | Offline read-back fixtures plus live write regression with exact/normalized value checks | `source_preflight`, `qa_testclient_scenario`, `scenario_log`, `data_assertion` | `.artifacts/openspec/committed-readback-honest/2026-07-02/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| BSL diagnostics | no BSL files changed | N/A because this change edits Python protocol code only | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/bsl-mcp` | no BSL module is modified | no BSL behavioral surface |
