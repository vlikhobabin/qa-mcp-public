## 1. Backend Interface

- [x] 1.1 Add a display backend module with local and remote backend classes.
- [x] 1.2 Add environment-driven backend selection for `QA_MCP_REMOTE_CLIENT`,
  `QA_MCP_HOST_AGENT`, and optional `QA_MCP_HOST_AGENT_TOKEN`.
- [x] 1.3 Preserve local XTEST, screenshot and window-list command construction
  through the local backend.

## 2. MCP Routing

- [x] 2.1 Replace guard-only remote-client returns for display tools with
  backend dispatch where a remote backend is configured.
- [x] 2.2 Keep local-boot lifecycle tools guarded in remote-client mode.
- [x] 2.3 Route `open_external_processor` through the backend and return a
  structured remote-client diagnostic when the backend is unavailable.

## 3. Tests And Evidence

- [x] 3.1 Add offline tests for local backend preservation and remote backend
  HTTP dispatch using fake responses.
- [x] 3.2 Add MCP tool tests for remote-mode unavailable-agent diagnostics.
- [x] 3.3 Run `python -m compileall src tests` and focused pytest for display
  backend, MCP server, screenshot, window and XTEST helpers.
- [x] 3.4 Retain bounded verification evidence under
  `.artifacts/openspec/display-backend-abstraction/20260626-card120/`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BSL-only module edit | N/A | No BSL or 1C metadata source changes in this Python backend refactor. | N/A | N/A | N/A | /opt/ai-dev-suite-for-1c/bsl-mcp | Python-only change; no BSL modules are edited. | None for BSL. |
| Delivery or runtime apply | `src/qa_mcp/protocol/*`, `src/qa_mcp/mcp_server.py` display backend routing | Offline compile and pytest focused on backend selection plus local Linux command preservation. | source_preflight, scenario_log | `.artifacts/openspec/display-backend-abstraction/20260626-card120/offline-tests.json` | required | /opt/ai-dev-suite-for-1c/qa-mcp |  | Remote Windows proof is deferred to `remote-display-e2e`. |
| Managed form layout | Display-bound tool screenshot/input path | Fake remote screenshot and local screenshot dispatch prove PNG routing without live UI mutation. | screenshot, scenario_log | `.artifacts/openspec/display-backend-abstraction/20260626-card120/backend-dispatch-evidence.md` | required | /opt/ai-dev-suite-for-1c/qa-mcp |  | Pixel correctness requires the later Windows E2E change. |
