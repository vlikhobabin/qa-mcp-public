## 1. Leaf Module

- [x] 1.1 Add `src/qa_mcp/versioning.py` with cycle-free version helpers.
- [x] 1.2 Re-export moved helpers from `src/qa_mcp/regression/versioning.py`.
- [x] 1.3 Replace protocol lazy imports with top-level imports from `qa_mcp.versioning`.

## 2. Compatibility

- [x] 2.1 Preserve bare family and full platform version handling.
- [x] 2.2 Preserve unsupported-version fail-closed diagnostics.
- [x] 2.3 Keep regression callers import-compatible.

## 3. Verification

- [x] 3.1 Add or update focused versioning tests.
- [x] 3.2 Run `uv run pytest -q`.
- [x] 3.3 Run `rg "regression.versioning|lazy import|active_version_key" src/qa_mcp/protocol src/qa_mcp/mcp_server.py` and confirm protocol callers use the leaf module.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient protocol runtime | bundled protocol asset version selection | Offline pytest plus source check for top-level leaf imports | source_preflight: py_compile passed and protocol callers show only `qa_mcp.versioning` imports/usages for `active_version_key`; scenario_log: focused versioning/bootstrap tests -> 44 passed; full suite -> 665 passed; summary: `.artifacts/openspec/qa-mcp-versioning-leaf/20260702-offline/evidence-summary.md` | `.artifacts/openspec/qa-mcp-versioning-leaf/20260702-offline/` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Offline coverage preserves version-family selection; residual live risk is limited to platform installations not represented by the offline roots. |
| BSL and 1C metadata | N/A - Python version policy refactor only | No BSL modules, metadata objects, roles, reports or migrations are changed | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change does not edit 1C configuration source or live infobase data. | Runtime behavior is covered by versioning/protocol tests. |
