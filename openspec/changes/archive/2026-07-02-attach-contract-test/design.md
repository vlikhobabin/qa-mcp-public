## Context

Individual tests can prove one tool resolves attachments, but they cannot prove the registry-wide contract that `attach_test_client` advertises. The test should derive its cases from an explicit endpoint-touching tool list and assert the connector endpoint captured by monkeypatching lower-level connect/replay functions.

## Design

- Keep an explicit endpoint-touching tool list in the test module so adding a new tool requires a conscious classification.
- Use `mcp._tool_manager.list_tools()` the same way the clean tool-surface tests inspect registered tools.
- Attach a sentinel endpoint and call each tool with omitted `host` and `port`.
- Monkeypatch the relevant low-level connector or native helper for each tool family to capture `host` and `port` without live 1C runtime.
- Include negative cases for invalid `capture` and invalid arguments where the wrapper can fail before any socket operation.
- Test `measure_scenario` with `QA_MCP_REMOTE_CLIENT=1` and assert the structured local-only result instead of `FileNotFoundError`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation tool surface | FastMCP registered endpoint-touching tools and attach contract | Registry-driven pytest contract with monkeypatched connectors | pytest output, registry case count, endpoint capture assertions | `.artifacts/openspec/attach-contract-test/<run-id>/pytest.txt` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | Live 1C runtime and platform process startup | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | Contract is intentionally offline and does not perform live UI actions. | Test doubles can miss a real connector path unless the case list is kept aligned with registered tools. |

## Notes

The test is allowed to use narrow monkeypatches per tool family, but it should fail loudly when a newly registered endpoint tool is missing from the classification list.
