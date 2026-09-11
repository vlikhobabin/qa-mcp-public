## 1. Decorator Foundation

- [x] 1.1 Add the shared endpoint-aware tool decorator near the existing local-only guard.
- [x] 1.2 Route endpoint resolution, capture resolution, structured error shaping and attachment annotation through the decorator.
- [x] 1.3 Preserve existing structured write/replay verdicts such as `retarget_failed` and `send_timeout`.

## 2. Tool Migration

- [x] 2.1 Apply the decorator to endpoint-touching tools that currently bypass `_resolve_testclient_endpoint`.
- [x] 2.2 Apply the local-boot guard path to `measure_scenario`.
- [x] 2.3 Confirm decorated internal-call paths already pass explicit resolved endpoints; no new guarded internal call path was introduced.

## 3. Verification

- [x] 3.1 Add or update focused offline tests for the decorator and `measure_scenario` remote-client guard.
- [x] 3.2 Run `uv run pytest -q` and retain the output summary.
- [x] 3.3 Run `openspec validate testclient-tool-decorator --strict`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation tool surface | Endpoint-touching MCP tools in `src/qa_mcp/mcp_server.py` | Offline pytest suite with monkeypatched connectors and registry assertions | pytest output, structured result assertions | `.artifacts/openspec/testclient-tool-decorator/cr-05-do/pytest-mcp-server.txt` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | Live 1C runtime, metadata apply and infobase mutation | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No 1C metadata/runtime state is changed by this Python server refactor. | Live runtime proof is deferred to existing protocol/tool smoke coverage. |
