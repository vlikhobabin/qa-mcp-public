## Why

The model-A streamable HTTP MCP server exposes the full qa-mcp tool surface. Binding it to all interfaces and publishing `8000:8000` by default makes that unauthenticated tool surface reachable by any host that can reach the machine.

## What Changes

- Change the default HTTP transport bind and Docker Compose publish path to loopback.
- Require an explicit unsafe opt-in before binding the model-A HTTP server to `0.0.0.0`.
- Log a startup warning whenever the HTTP MCP server is intentionally exposed beyond loopback without a built-in auth layer.
- Update Docker/runbook/README guidance so local-only and exposed deployments are visibly different.

## Capabilities

### New Capabilities
- `qa-mcp-http-transport-security`: qa-mcp HTTP MCP transport defaults to local-only access and makes unauthenticated network exposure explicit.

### Modified Capabilities
- none

## Impact

Touches Python MCP server startup configuration, Docker Compose/run scripts and user-facing operations documentation. This does not require live 1C runtime, Vanessa MCP, EDT/meta snapshots or protocol capture evidence; verification is offline config tests, source inspection and container/compose checks.
