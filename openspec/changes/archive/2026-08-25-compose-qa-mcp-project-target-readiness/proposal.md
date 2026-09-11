## Why

A resolved target must be composed into one application instance and exposed
through readiness without changing ordinary standalone behavior or starting a
client. Keeping this integration separate prevents lifecycle authority from
entering the adapter payload.

## What Changes

- Carry an optional immutable runtime-target resolution in `ApplicationContext`.
- Resolve project binding once during MCP server startup and keep instance state
  isolated.
- Add an ordered, secret-safe doctor/readiness result for bound and unbound mode.
- Retain no-side-effect Linux/Windows adapter preflight evidence.

## Capabilities

### New Capabilities
- `qa-mcp-project-target-composition`: Application/server/doctor composition of
  the resolved runtime target without lifecycle side effects.

### Modified Capabilities
- None.

## Impact

Python application composition, MCP startup, doctor, tests and docs change.
Read-only host inventory is required; live TestClient, Vanessa MCP, protocol
capture and EDT/meta snapshots are not.
