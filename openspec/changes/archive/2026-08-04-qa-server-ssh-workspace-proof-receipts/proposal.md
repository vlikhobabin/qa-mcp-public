## Why

Root server SSH workspace routing needs qa-mcp to publish a policy-gated
QA/TestClient proof receipt contract without making runtime proof mandatory for
every workspace delivery. The receipt must bind any required QA evidence to the
same pushed commit/tree/source identity used by source and readiness providers.

## What Changes

- Add a qa-mcp proof receipt contract for server SSH workspace deliveries.
- Report missing QA proof as `not-required` unless an explicit project policy or
  card marks QA proof as required.
- Preserve bounded diagnostics for missing, stale and unavailable proof without
  retaining screenshots, raw protocol logs, customer data, infobase dumps,
  source bodies or mutable workspace paths.
- Add offline tests for receipt construction, freshness classification and
  forbidden source/body route rejection.

## Capabilities

### New Capabilities
- `qa-mcp-workspace-proof-receipts`: Policy-gated QA/TestClient proof receipts
  tied to pushed source identity and bounded evidence references.

### Modified Capabilities
- none

## Impact

- Touches Python manager code and OpenSpec specs/tests.
- Does not change native TestClient protocol frames, MCP provider setup, runtime
  lab configuration or live 1C execution.
- Requires offline pytest/OpenSpec validation only; live 1C runtime, Vanessa MCP
  and EDT/meta snapshots are not required.
