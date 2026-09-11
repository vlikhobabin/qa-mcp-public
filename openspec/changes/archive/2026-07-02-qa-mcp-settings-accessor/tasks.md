## 1. Settings Module

- [x] 1.1 Add `src/qa_mcp/config.py` with `Settings.from_env()`.
- [x] 1.2 Document supported `QA_MCP_*` variables and defaults in the settings module.
- [x] 1.3 Add tests for explicit environment mappings, remote-client truth parsing and OData defaults.

## 2. Call Site Migration

- [x] 2.1 Migrate remote-client guards to the centralized settings/accessor path.
- [x] 2.2 Migrate OData defaults in `data/odata.py` and `regression/__main__.py`.
- [x] 2.3 Migrate remaining scattered `QA_MCP_*` reads that belong in `Settings`.

## 3. Verification

- [x] 3.1 Run focused configuration and endpoint guard tests.
- [x] 3.2 Run `uv run pytest -q`.
- [x] 3.3 Run `rg "QA_MCP_" src/qa_mcp` and confirm remaining reads are either in `config.py` or explicitly justified call sites.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient provider runtime configuration | `QA_MCP_*` parsing, remote-client guard and OData defaults | Offline pytest plus source inventory of remaining environment reads | source_preflight: py_compile passed; direct QA_MCP env-read grep returned no matches outside centralized access; scenario_log: focused config/OData/display/license tests -> 42 passed; full suite -> 670 passed; summary: `.artifacts/openspec/qa-mcp-settings-accessor/20260702-offline/evidence-summary.md` | `.artifacts/openspec/qa-mcp-settings-accessor/20260702-offline/` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Offline coverage preserves defaults and guard behavior; residual risk is limited to untested operator env combinations. |
| BSL and 1C metadata | N/A - Python configuration parsing only | No BSL modules, metadata objects, roles, reports or migrations are changed | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change does not edit 1C configuration source or live infobase data. | Runtime behavior is covered by configuration/endpoint tests. |
