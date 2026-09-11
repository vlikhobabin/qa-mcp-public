## 1. Implementation

- [x] 1.1 Change `src/qa_mcp/scenario/reporting.py::junit_xml` so suite counters derive from one testcase verdict per
      scenario.
- [x] 1.2 Emit a `<failure>` for non-passed failed scenarios even when no bad step details are present.
- [x] 1.3 Emit a single `<error>` rather than both failure and error when a scenario has error evidence.
- [x] 1.4 Keep failure/error message bodies useful by including available bad step details.

## 2. Offline Tests

- [x] 2.1 Add `tests/test_reporting.py` coverage for `status: "failed"` with no bad steps.
- [x] 2.2 Add coverage for a scenario with both `assert_failed` and `error` details counting once.
- [x] 2.3 Add an invariant assertion for `tests == passed + failures + errors + skipped`.
- [x] 2.4 Preserve Cyrillic/XML escaping coverage.

## 3. Verification

- [x] 3.1 `uv run pytest tests/test_reporting.py -q` — 8 passed.
- [x] 3.2 `uv run pytest tests/ -q` — 594 passed.
- [x] 3.3 `uv run python -m compileall -q src/qa_mcp` — passed.
- [x] 3.4 `openspec validate junit-verdict-from-status --strict` — passed.
- [x] 3.5 `git diff --check` — passed.
- [x] 3.6 Windows-native verification: not run in this Linux delivery; no platform-specific code changes. The
      equivalent gate is `uv run pytest tests/test_reporting.py -q` on Windows before a Windows release build.

## Verification Matrix

Card scope: qa-mcp pure Python scenario-reporting code. No BSL, metadata, managed form, role, posting, source import or
live infobase mutation is touched.

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | residual_risk | n/a_reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Python manager / scenario reporting | `src/qa_mcp/scenario/reporting.py::junit_xml` | scenario-status based JUnit verdict and coherent counters | `uv run pytest tests/test_reporting.py -q` (8 passed), `uv run pytest tests/ -q` (594 passed), `uv run python -m compileall -q src/qa_mcp` | `tests/test_reporting.py` | provided | qa-mcp | none for offline behavior | — |
| CI report consumers | `write_test_report(..., junit=True)` output semantics | failed scenarios no longer render green; mixed bad details count once | parsed XML assertions (`uv run pytest tests/test_reporting.py -q`, 8 passed) | `tests/test_reporting.py` | provided | qa-mcp | CI dashboards may show corrected failures that were previously false green | — |
| QA/TestClient live runtime | live scenario execution | no live behavior change; only report serialization changes | N/A | N/A | N/A | qa-mcp | live run payload shape unchanged | no live 1C required because the bug is pure report serialization |
| OpenSpec/spec contract | `qa-mcp-protocol-lab` delta | JUnit verdict/counter requirements added and synced | `openspec validate junit-verdict-from-status --strict` | `openspec/changes/junit-verdict-from-status/` | provided | qa-mcp | none | — |
