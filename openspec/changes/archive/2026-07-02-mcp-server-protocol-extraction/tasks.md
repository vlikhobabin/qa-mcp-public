## 1. Protocol Module Extraction

- [x] 1.1 Add `src/qa_mcp/protocol/introspection.py` for descriptor, value, table-cell and window-list read helpers.
- [x] 1.2 Add `src/qa_mcp/protocol/foreground.py` for foreground/open helpers currently embedded in `mcp_server.py`.
- [x] 1.3 Move splice/header helpers needed by those flows into protocol-owned modules without changing frame bytes.

## 2. MCP Server Wiring

- [x] 2.1 Replace `mcp_server.py` private wire-helper calls with imports from the new protocol modules.
- [x] 2.2 Preserve `@testclient_tool` usage, MCP docstrings, `_values_equivalent`, activation retry and `_should_retry_label_locate`.
- [x] 2.3 Confirm `mcp_server.py` no longer directly opens sockets or imports `GuidRebinder`.

## 3. Verification

- [x] 3.1 Add or update focused tests for extracted helper call-through and endpoint propagation.
- [x] 3.2 Run `uv run pytest -q`.
- [x] 3.3 Run `rg "create_connection|GuidRebinder" src/qa_mcp/mcp_server.py` and confirm zero matches.
- [x] 3.4 Run the existing tool-surface/tool-count check or `verify_protected_image.py` if available in the repo.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient protocol runtime | MCP protocol foreground/introspection helpers | Offline pytest plus source checks for socket/rebinder extraction; optional unchanged live-regression when a client is available | source_preflight: no `create_connection` or `GuidRebinder` matches in `src/qa_mcp/mcp_server.py`; scenario_log: `uv run pytest -q` -> 663 passed; tool surface: 63 registered tools and `tests/test_clean_tool_surface.py` -> 2 passed; summary: `.artifacts/openspec/mcp-server-protocol-extraction/20260702-offline/evidence-summary.md`; live bundle not run | `.artifacts/openspec/mcp-server-protocol-extraction/20260702-offline/` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Offline coverage preserves wrapper contracts and parsing; residual live replay risk remains bounded by no frame-byte semantic change. |
| BSL and 1C metadata | N/A - MCP Python/provider refactor only | No BSL modules, metadata objects, roles, reports or migrations are changed | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change does not edit 1C configuration source or live infobase data. | Runtime behavior is covered by protocol/MCP tests and optional live-regression, not BSL diagnostics. |
