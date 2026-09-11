## Why

Lifecycle admission cannot be safe if the shared executor accepts a foreign or
stale target/session and results lose that identity. The common MCP/scenario
boundary needs one generic gate before tool-specific lifecycle work.

## What Changes

- Extend operation results and artifact references with bounded target/session
  provenance.
- Gate MCP and scenario execution on application, session, attachment,
  generation and endpoint equality before invoking an adapter.
- Apply evidence policy to artifact paths for every verdict class.
- Preserve downstream fake-executor compatibility.

## Capabilities

### New Capabilities
- `qa-mcp-target-session-operation-identity`: Target/session enforcement and
  provenance at the public shared executor boundary.

### Modified Capabilities
- None.

## Impact

Python shared-core contracts, executor routing and offline tests change. No MCP
tool schema, protocol frame, runtime lab configuration or live 1C execution is
part of this payload.
