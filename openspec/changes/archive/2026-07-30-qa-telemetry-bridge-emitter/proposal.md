## Why

qa-mcp produces useful scenario, report, screenshot and verification outcomes,
but those outcomes do not reach the suite trace store as semantic QA telemetry.
The root retrospective pipeline can already ingest `qa_telemetry_bridge`
observations, so the remaining gap is a qa-mcp emitter.

## What Changes

- Add a qa-mcp telemetry bridge emitter that builds bounded
  `qa_telemetry_bridge` observations from existing QA outcomes.
- Resolve the active suite trace context from proxy environment variables or
  proxy trace context files, and append observations only when a trace context
  exists.
- Wire the emitter into scenario, report, screenshot and verification-summary
  surfaces without changing non-traced run behavior.
- Add offline tests for emitted payload shape, bounded evidence, trace-context
  no-op behavior and MCP endpoint wiring.

## Capabilities

### New Capabilities
- `qa-mcp-telemetry-bridge`: qa-mcp emits bounded semantic QA telemetry
  observations into an active suite trace.

### Modified Capabilities
- none

## Impact

This change touches Python manager/runtime code under `src/qa_mcp/`, focused
offline tests, qa-mcp OpenSpec artifacts and the component board card. It does
not require live 1C runtime, Vanessa MCP, EDT/meta snapshots or raw protocol
captures for implementation verification; optional root closure may later run a
suite retrospective over a real trace.
