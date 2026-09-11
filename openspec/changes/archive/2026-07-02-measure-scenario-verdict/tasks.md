## 1. Implementation

- [x] 1.1 Change `src/qa_mcp/debug/measure.py` so `scenario_ok` is derived from `res.get("status") == "passed"`.
- [x] 1.2 Remove the non-dict truthiness fallback for the scenario verdict; malformed result payloads fail closed.

## 2. Offline Tests

- [x] 2.1 Add `tests/test_measure.py` coverage for `measure_scenario` returning `scenario_ok: false` when
      `run_scenario` returns `status: "failed"`.
- [x] 2.2 Add the matching passing case where `status: "passed"` yields `scenario_ok: true`.
- [x] 2.3 Keep existing debug report parsing tests green.

## 3. Verification

- [x] 3.1 `uv run pytest tests/test_measure.py -q` — 9 passed.
- [x] 3.2 `uv run pytest tests/ -q` — 594 passed.
- [x] 3.3 `uv run python -m compileall -q src/qa_mcp` — passed.
- [x] 3.4 `openspec validate measure-scenario-verdict --strict` — passed.
- [x] 3.5 `git diff --check` — passed.
- [x] 3.6 Windows-native verification: not run in this Linux delivery; no platform-specific code changes. The
      equivalent gate is `uv run pytest tests/test_measure.py -q` on Windows before a Windows release build.

## Verification Matrix

Card scope: qa-mcp Python manager debug/measure verdict handling. No BSL, metadata, managed form, role, posting,
source import or live infobase mutation is touched.

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | residual_risk | n/a_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Python manager / debug measure | `src/qa_mcp/debug/measure.py::measure_scenario` | `scenario_ok` follows `ScenarioResult.status` | `uv run pytest tests/test_measure.py -q` (9 passed), `uv run pytest tests/ -q` (594 passed), `uv run python -m compileall -q src/qa_mcp` | `tests/test_measure.py` | provided | qa-mcp | none for offline behavior | — |
| QA/TestClient live runtime | live debug TestClient measure flow | no live behavior beyond verdict calculation | N/A | N/A | N/A | qa-mcp | live launch/cleanup unchanged; offline tests monkeypatch live dependencies | no live 1C required because the bug is pure Python verdict logic |
| OpenSpec/spec contract | `qa-mcp-protocol-lab` delta | scenario verdict requirement added and synced | `openspec validate measure-scenario-verdict --strict` | `openspec/changes/measure-scenario-verdict/` | provided | qa-mcp | none | — |
