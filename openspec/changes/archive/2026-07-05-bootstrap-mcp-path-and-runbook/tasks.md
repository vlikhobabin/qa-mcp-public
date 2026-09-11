## 1. Bootstrap URL

- [x] 1.1 Change `delivery/bootstrap.ps1` to print `http://127.0.0.1:<McpPort>/mcp` without a trailing slash.
- [x] 1.2 Update any generated client-config text so it no longer tells operators to keep `/mcp/`.

## 2. Runbook Guidance

- [x] 2.1 Update active delivery runbooks to use slashless `/mcp`.
- [x] 2.2 Document that blank 1C passwords omit `-Password` rather than passing `-Password ""`.
- [x] 2.3 Keep Docker Desktop readiness (`docker info`) visible before install/e2e steps.
- [x] 2.4 Add a manual PowerShell UTF-8 byte-body example for Cyrillic tool calls.
- [x] 2.5 Add or align `-WindowTitle` guidance for ambiguous/fallback window selection.

## 3. Verification

- [x] 3.1 Run focused delivery tests or static assertions for bootstrap/runbook URL text.
- [x] 3.2 Run `git diff --check -- delivery openspec/changes/bootstrap-mcp-path-and-runbook`.
- [x] 3.3 Record retained verification evidence under `.artifacts/openspec/bootstrap-mcp-path-and-runbook/<run-id>/`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `delivery/bootstrap.ps1` printed MCP URL and operator guidance | Static script/doc assertions and diff review | pytest or grep-based focused test output, diff-check output | `.artifacts/openspec/bootstrap-mcp-path-and-runbook/20260705T193326Z/delivery-docs.md` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | Real Windows bootstrap run | Operator-owned Windows bootstrap smoke with Docker Desktop and host-agent | Retained bootstrap transcript and MCP `/mcp` tools/list result | `.artifacts/openspec/bootstrap-mcp-path-and-runbook/<run-id>/windows-bootstrap-smoke.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows host, Docker Desktop, PowerShell runtime, or licensed 1C TestClient is available inside this Linux workspace. | The next release install run must retain a bootstrap transcript using the slashless MCP URL. |
