## Why

R7 published the bounded positive result normalizer, but the public MCP and
ScenarioRunner paths still call executors directly. R8 must put one pure,
fail-closed route gate and one operation-local evidence scope in front of both
paths before OSS-04E can safely add lifecycle admission.

## What Changes

- Route composed operations only when unbound, pre-session, or bound
  target/session/attachment state is exact and symmetric; reject malformed or
  foreign state before Local or Windows adapters run.
- Admit trusted provenance before opening the application-owned evidence scope,
  execute once inside that scope, and normalize once before `finally` closes
  the scope.
- Make real MCP and ScenarioRunner return the same trusted provenance, verdict
  taxonomy, declared-field mismatch outcome, URL matrix outcome, and bounded
  total result.
- Add test-first Linux matrices plus exact-source Windows offline integration
  evidence. No protocol capture, live 1C mutation, lifecycle authority, new
  wire contract, MCP provider setup, or runtime-lab configuration is added.

## Capabilities

### New Capabilities

- `qa-mcp-positive-operation-boundary-public-integration`: Pure route
  admission and positive-result normalization shared by the real MCP and
  ScenarioRunner public paths.

### Modified Capabilities

- None.

## Impact

- Python manager/core routing and the existing MCP/ScenarioRunner call sites.
- Focused public-path, route, provenance, URL, bounds and adapter-isolation
  tests plus shared-core extension documentation.
- Offline Windows wheel verification only; no live 1C, Vanessa MCP, EDT/meta
  snapshot, protocol capture, Docker, host-agent or external mutation.
