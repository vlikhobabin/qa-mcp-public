## 1. Form-Read Diagnostics

- [x] 1.1 Add a structured helper for missing current ManagedForm GUID / missing `open_link` cases.
- [x] 1.2 Update `read_form_descriptor` so the no-`open_link` path returns actionable guidance instead of `attached-descriptor-empty` with a raw template detail.
- [x] 1.3 Update `read_table_cell` so the no-`open_link` path returns the same actionable guidance before raw template errors cross the tool boundary.

## 2. Stale Attachment Gating

- [x] 2.1 Update endpoint resolution or wrapper logic so `attached=true` with `listening=false` is treated as stale for endpoint-touching tools.
- [x] 2.2 Include a recovery action hint for `qa-mcp-testclient` restart or re-attach.
- [x] 2.3 Preserve explicit `host`/`port` override behavior for callers that intentionally bypass attachment state.

## 3. Verification

- [x] 3.1 Add offline pytest coverage for no-`open_link` `read_form_descriptor` diagnostics.
- [x] 3.2 Add offline pytest coverage for no-`open_link` `read_table_cell` diagnostics.
- [x] 3.3 Add offline pytest coverage that stale attachment liveness blocks endpoint-touching tools before connector use.
- [x] 3.4 Run focused pytest for MCP server/tool wrapper behavior.
- [x] 3.5 Record retained verification evidence under `.artifacts/openspec/form-read-current-form-and-stale-attachment/<run-id>/`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | `read_form_descriptor`/`read_table_cell` wrapper diagnostics without `open_link` | Offline pytest with monkeypatched protocol path and no live 1C process | Pytest output and retained summary | `.artifacts/openspec/form-read-current-form-and-stale-attachment/20260705T193326Z/form-read-wrapper-diagnostics.md` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | Stale attached endpoint with `listening=false` | Offline pytest for attachment liveness rejection and action hint | Pytest output and retained summary | `.artifacts/openspec/form-read-current-form-and-stale-attachment/20260705T193326Z/stale-attachment.md` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Managed form layout | Real Windows/BSP current-form read smoke | Read-only `read_form_descriptor(open_link=...)` and no-`open_link` diagnostic transcript against an operator-owned Windows host | QA/TestClient transcript or MCP tool output bundle | `.artifacts/openspec/form-read-current-form-and-stale-attachment/<run-id>/windows-form-read-smoke.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows host, GUI desktop, PowerShell runtime, or licensed 1C TestClient is available inside this Linux workspace. | First Windows model-B validation must confirm the diagnostic text against a real form. |
