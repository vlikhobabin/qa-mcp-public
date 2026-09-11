## 1. Parser guards

- [x] 1.1 Add bounds checks for truncated value envelopes in `responses.py`.
- [x] 1.2 Add bounds checks for truncated window-caption envelopes in `responses.py`.
- [x] 1.3 Make parser helpers that encode field names as Latin-1 return `None` for unsupported names instead of raising `UnicodeEncodeError`.

## 2. List-grid stop behavior

- [x] 2.1 Remove adjacent-duplicate row equality as an end-of-list condition in `read_list_grid_replay`.
- [x] 2.2 Preserve all adjacent duplicate rows in the returned row list.
- [x] 2.3 Add explicit truncation or stop-reason metadata when a row read times out or an empty row stops the sweep.

## 3. Tests

- [x] 3.1 Add parser tests for truncated form-field value envelopes and truncated window-caption envelopes.
- [x] 3.2 Add parser tests proving Cyrillic field names return `None` rather than `UnicodeEncodeError`.
- [x] 3.3 Add list-grid tests proving adjacent equal rows are preserved.
- [x] 3.4 Add list-grid tests proving timeout or empty-row stops expose stop metadata.

## 4. Verification

- [x] 4.1 Run focused parser/list-grid tests.
- [x] 4.2 Run `uv run pytest -q`.
- [x] 4.3 Run `openspec validate parser-truncation-guards --strict`.
- [x] 4.4 Run `git diff --check -- openspec/changes/parser-truncation-guards src tests`.
- [x] 4.5 Run or record a runtime-gap diagnostic for a Linux live list read after offline tests.

## 5. Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Response parser | `_value_after_leaf`, `_window_caption_after`, field-name scanners | truncated blob and Cyrillic field-name fixtures | `uv run pytest -q tests/test_form_value_parser.py tests/test_native_write.py` (80 passed), `uv run pytest -q` (620 passed) | `tests/test_form_value_parser.py` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` | N/A | Low: byte scanner still cannot resolve every non-Latin name |
| List-grid read | `read_list_grid_replay` duplicate and timeout handling | fake replay/session with adjacent equal rows and timed-out row | offline unit tests preserve adjacent duplicate rows and expose `truncated` / `stop_reason` | `tests/test_native_write.py` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` | N/A | Low: result shape remains additive for existing MCP callers |
| QA/TestClient live read | `read_list_grid` on Linux `vanessa_client` | optional live read pass after parser/list-grid tests | `uv run python -m qa_mcp.regression ...` GREEN 6/6; `ui.list_grid_after_dirty` row_count=5 | `.artifacts/openspec/parser-truncation-guards/2026-07-02/live-read/20260702T063006Z/report.json` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` | N/A | Low: live list read completed on Linux lab |
