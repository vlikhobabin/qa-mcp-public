## Why

R7 is published and R8 is the only planned public-path integration successor,
but repeated-defect R8 cannot pass deterministic ChangeRail preflight without
one separately published authorization bound to its exact future in-progress
card path. Historical A2/A3/A4 authorizations target other successors and must
not be reused.

## What Changes

- Publish one closed six-field authorization object from completed R5-R2 to
  future in-progress R8, gated by published R7 and A5's reciprocal relations.
- Preserve the machine ceiling `301`, R8's stricter at-most-`300` production
  line cap and `allow_new_authority_or_wire_protocol: false`.
- Prove an isolated finalized exact candidate is accepted while bounded
  successor/source mismatches fail closed.
- Keep OSS-04E blocked until reviewed R8 itself publishes.

## Capabilities

### New Capabilities

- `qa-mcp-positive-operation-boundary-integration-authorization`: exact A5
  authorization source and reciprocal fail-closed consumption contract for R8.

### Modified Capabilities

- None.

## Impact

OpenSpec and board metadata only. No Python manager, MCP provider, protocol
tool, runtime lab configuration, dependency, test, live 1C, Windows, Docker or
external-state change is required.
