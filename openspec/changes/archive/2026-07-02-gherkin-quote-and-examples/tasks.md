## 1. Parser Implementation

- [x] 1.1 Update `_q()` in `src/qa_mcp/scenario/gherkin.py` to require matching single/double delimiters while
      allowing the other quote character in captured values.
- [x] 1.2 Change examples parsing so each `Примеры:` / `Examples:` block has its own header and data rows.
- [x] 1.3 Make `_split_row()` preserve `\|` as a literal pipe inside a table cell.
- [x] 1.4 Make triple-quoted docstring blocks explicit unsupported input that becomes an unmapped diagnostic, not
      executable steps.

## 2. Offline Tests

- [x] 2.1 Add `tests/test_scenario_gherkin.py` coverage for `'ООО "Ромашка"'` and the symmetric double-quoted value
      containing a single quote.
- [x] 2.2 Add coverage for two examples blocks generating only data-row scenarios.
- [x] 2.3 Add coverage for escaped pipes in a DataTable cell.
- [x] 2.4 Add coverage for unsupported triple-quoted docstrings being reported as unmapped.

## 3. Verification

- [x] 3.1 `uv run pytest tests/test_scenario_gherkin.py -q` — 18 passed.
- [x] 3.2 `uv run pytest tests/ -q` — 598 passed.
- [x] 3.3 `uv run python -m compileall -q src/qa_mcp` — passed.
- [x] 3.4 `openspec validate gherkin-quote-and-examples --strict` — passed.
- [x] 3.5 `git diff --check` — passed.
- [x] 3.6 Windows-native verification: not run in this Linux delivery; no platform-specific code is planned. The
      equivalent Windows gate is `uv run pytest tests/test_scenario_gherkin.py -q` before a Windows release build.

## Verification Matrix

Card scope: qa-mcp Python Gherkin parser/transpiler. No BSL, metadata, managed form, role, posting, source import,
live infobase mutation, or runtime TestClient launch is required for this change.

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | residual_risk | n/a_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Python manager / Gherkin parser | `src/qa_mcp/scenario/gherkin.py` quoted args, examples, tables, docstrings | Parser keeps input values exact and fails closed on unsupported docstrings | `uv run pytest tests/test_scenario_gherkin.py -q` (18 passed), `uv run pytest tests/ -q` (598 passed), `uv run python -m compileall -q src/qa_mcp` (passed) | `tests/test_scenario_gherkin.py` | provided | qa-mcp | none for offline parser behavior | — |
| QA/TestClient live runtime | scenario execution after transpile | no live behavior change; only parser output changes | N/A | N/A | N/A | qa-mcp | live launch/cleanup unchanged; parser regressions covered offline | no live 1C required because defects are pure input parsing |
| OpenSpec/spec contract | `qa-mcp-protocol-lab` delta | Gherkin parsing requirements added and synced | `openspec validate gherkin-quote-and-examples --strict` (passed), `git diff --check` (passed) | `openspec/changes/gherkin-quote-and-examples/` | provided | qa-mcp | none | — |
