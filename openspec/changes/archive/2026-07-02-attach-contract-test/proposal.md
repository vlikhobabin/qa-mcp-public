## Why

The attach-endpoint bug is easy to reintroduce because endpoint-aware behavior is spread across many registered MCP tools. A registry-driven contract test makes the advertised attach contract enforceable for every endpoint-touching tool.

## What Changes

- Add a parametrized contract test over the FastMCP tool registry for endpoint-touching tools.
- Assert that attached endpoints are used when tool calls omit `host` and `port`.
- Assert invalid captures and invalid arguments return structured errors for wrapped tools.
- Assert `measure_scenario` returns structured local-only guidance under `QA_MCP_REMOTE_CLIENT=1`.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-tool-endpoint-contract`: add registry-level offline verification for attach-aware endpoint behavior and structured wrapper errors.

## Impact

Touches offline tests and, where needed, small test seams in Python MCP server code. This does not require live 1C runtime, Vanessa MCP, EDT/meta snapshots, or new capture evidence; proof comes from pytest output and monkeypatched connector observations.
