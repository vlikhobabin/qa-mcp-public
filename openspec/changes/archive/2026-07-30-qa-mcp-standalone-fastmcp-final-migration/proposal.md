# QA MCP Standalone FastMCP Final Migration

## Why
qa-mcp is the remaining SDK-bundled FastMCP provider. The suite runtime
standard requires standalone FastMCP with an exact FastMCP pin and an MCP SDK
1.x guard.

## What Changes
- Replace the SDK-bundled FastMCP import with standalone FastMCP.
- Pin `fastmcp==3.4.2` and `mcp>=1.28,<2`.
- Adapt the owned HTTP runner to FastMCP 3's `http_app()` API while preserving
  the UTF-8 JSON-RPC body gate.
- Preserve the pre-migration 68-tool public schema surface with retained
  before/after evidence.

## Impact
- No TestClient protocol semantics, business data mutation, live infobase
  behavior, tool names, tool schemas, or protected runtime assets change.
