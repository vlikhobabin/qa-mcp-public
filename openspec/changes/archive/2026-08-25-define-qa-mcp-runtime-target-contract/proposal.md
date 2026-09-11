## Why

Project-mode lifecycle needs a public target contract before any suite-specific
handoff or process behavior can depend on it. This first bounded payload isolates
the immutable models and closed schema so later deliveries stay independently
reviewable below the ChangeRail complexity ceiling.

## What Changes

- Add public immutable runtime fingerprint, binding, observation, profile and
  evidence-policy models beside the existing shared-core identity types.
- Package a closed JSON schema for provider-local runtime-target profiles.
- Add contract and packaging tests only; do not resolve a handoff, start a
  TestClient or change MCP lifecycle behavior.

## Capabilities

### New Capabilities
- `qa-mcp-runtime-target-contract`: Generic public runtime-target data and
  profile-schema contract.

### Modified Capabilities
- None.

## Impact

Python shared-core code, package assets, tests and OpenSpec docs change. No
protocol tools, MCP provider setup, runtime lab configuration, live 1C,
Vanessa MCP or EDT/meta snapshot is required.
