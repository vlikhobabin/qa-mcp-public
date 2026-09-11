## Why

The blocked S4-R1 payload has twice reached the same pre-receipt first-window-
inventory refusal, but retained evidence does not bind that refusal to exact
child or listener liveness and the earlier timeline equated a reported
listener PID with current readiness. A separate offline decision is required
before any further implementation correction or real-contour admission.

## What Changes

- Define an exclusive privacy-safe state model for exact child liveness, exact
  listener liveness, main-window presence, and successful non-empty,
  successful empty, or errored desktop inventory.
- Publish one fail-closed decision from retained evidence and offline source
  inspection; do not run 1C, access the real configuration, or add runtime
  evidence.
- Authorize exactly one later S4-R1 correction: replace each untyped inventory
  boundary with one liveness-fenced sample around one enumeration call.
- Preserve all blocked S4-R1, S7, OSS-07 and OSS-08 payload paths and grant no
  live-confirmation or public-route authority.

## Capabilities

### New Capabilities

- `qa-mcp-hidden-direct-execute-observation-liveness-decision`: Defines the
  offline liveness classification, fail-closed inventory semantics and sole
  bounded successor correction authorization.

### Modified Capabilities

- none.

## Impact

This change touches only OpenSpec workflow and protocol-research decision
documentation. It changes no protocol tool, Go or Python manager code, MCP
provider setup, runtime lab configuration or public API. It requires only
retained privacy-safe evidence and offline source analysis; live 1C, Vanessa
MCP, EDT/meta snapshots, Windows task execution and real-contour admission are
out of scope.
