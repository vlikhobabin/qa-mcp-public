## 1. Registry Contract

- [x] 1.1 Add an explicit endpoint-touching tool classification used by the contract test.
- [x] 1.2 Add parametrized registry tests that call endpoint-touching tools after `attach_test_client`.
- [x] 1.3 Capture and assert the resolved `host` and `port` through monkeypatched connector/native helper seams.

## 2. Error And Guard Coverage

- [x] 2.1 Add invalid capture or invalid argument assertions for wrapped endpoint tools.
- [x] 2.2 Add `QA_MCP_REMOTE_CLIENT=1` coverage for `measure_scenario`.
- [x] 2.3 Make the test fail when a new endpoint-touching registry tool lacks classification.

## 3. Verification

- [x] 3.1 Run the focused contract tests.
- [x] 3.2 Run `uv run pytest -q`.
- [x] 3.3 Run `openspec validate attach-contract-test --strict`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation tool surface | Registry-level attach endpoint contract for MCP tools | Parametrized pytest contract, monkeypatched connector capture, structured error assertions | pytest output and case count summary | `.artifacts/openspec/attach-contract-test/cr-05-do/pytest-mcp-server.txt` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | Live 1C runtime, metadata apply and infobase mutation | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change is a Python offline test contract and does not mutate runtime 1C state. | Offline seams must stay aligned with the true connector paths. |
