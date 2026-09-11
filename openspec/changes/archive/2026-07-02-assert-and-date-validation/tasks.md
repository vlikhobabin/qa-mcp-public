## 1. Data Assertion Validation

- [x] 1.1 Update `src/qa_mcp/data/odata.py::match_value` to raise `ValueError` for unknown modes.
- [x] 1.2 Add `numeric` mode using decimal comparison with comma-to-dot normalization.
- [x] 1.3 Add `tests/test_odata.py` coverage for unknown mode and numeric comparisons.

## 2. Table Date Validation

- [x] 2.1 Add a shared table-date normalization path in `src/qa_mcp/mcp_server.py` that reuses the managed-form date
      validator.
- [x] 2.2 Validate table date-cell input before capture/session activation in both capture-backed and open-link paths.
- [x] 2.3 Move the backward-year calendar guard before dropdown-opening clicks in `_drive_calendar_pick`.
- [x] 2.4 Add `tests/test_mcp_server.py` coverage proving invalid dates return `blocked/invalid_date` without calendar
      interaction and valid dates still route to the picker.

## 3. Verification

- [x] 3.1 `uv run pytest tests/test_odata.py tests/test_mcp_server.py -q` — 58 passed.
- [x] 3.2 `uv run pytest tests/ -q` — 601 passed.
- [x] 3.3 `uv run python -m compileall -q src/qa_mcp` — passed.
- [x] 3.4 `openspec validate assert-and-date-validation --strict` — passed.
- [x] 3.5 `git diff --check` — passed.
- [x] 3.6 Windows-native verification: not run in this Linux delivery; no platform-specific code is planned. The
      equivalent Windows gate is `uv run pytest tests/test_odata.py tests/test_mcp_server.py -q` before a Windows
      release build.

## Verification Matrix

Card scope: qa-mcp Python data assertion and table date-cell validation. No BSL, metadata, role, posting, source import
or runtime apply is touched. The date-cell surface can drive QA/TestClient UI in normal use, but this change verifies
invalid-input safety offline with injected fakes and does not execute a live UI action.

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | residual_risk | n/a_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Python manager / data assertion | `src/qa_mcp/data/odata.py::match_value` | unsupported modes raise; numeric mode compares decimal values | `uv run pytest tests/test_odata.py tests/test_mcp_server.py -q` (58 passed), `uv run pytest tests/ -q` (601 passed), `uv run python -m compileall -q src/qa_mcp` (passed) | `tests/test_odata.py` | provided | qa-mcp | none for offline comparator behavior | — |
| QA/TestClient UI automation safety | `src/qa_mcp/mcp_server.py::set_table_date_cell` date validation and calendar picker guard | invalid dates block before activation/clicks; backward-year guard does not open dropdown | `uv run pytest tests/test_odata.py tests/test_mcp_server.py -q` (58 passed), `uv run pytest tests/ -q` (601 passed), `uv run python -m compileall -q src/qa_mcp` (passed) | `tests/test_mcp_server.py` | provided | qa-mcp | live calendar geometry unchanged; tests assert no invalid-input interaction | — |
| Live TestClient runtime execution | actual date-cell write on a running 1C client | no live execution planned for invalid-input parser fix | N/A | N/A | N/A | qa-mcp | valid live date-cell flow remains covered by prior runtime evidence; this card only changes preflight guards | no live 1C required because acceptance is offline safety/validation |
| OpenSpec/spec contract | `qa-mcp-protocol-lab` delta | data/date validation requirements added and synced | `openspec validate assert-and-date-validation --strict` (passed), `git diff --check` (passed) | `openspec/changes/assert-and-date-validation/` | provided | qa-mcp | none | — |
