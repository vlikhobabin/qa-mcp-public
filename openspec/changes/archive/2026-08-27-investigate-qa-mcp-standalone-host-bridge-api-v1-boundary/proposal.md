## Why

OSS-05 introduces the versioned public `qa-mcp.windows-host-bridge` API major
`1`. Its implementation is bounded and verified, but ChangeRail must consume a
separately published investigation before a successor with a new wire contract
can enter independent review.

## What Changes

- Publish one exact investigation decision bound only to the existing OSS-05
  card at its canonical `3.inprogress` path.
- Permit the new public bridge API v1 contract and a minimum ChangeRail machine
  ceiling of `301`, while preserving OSS-05's stricter `300` added-production-
  LOC gate.
- Freeze the allowed route family to authenticated capability negotiation,
  TestClient lifecycle/relay and bounded display/UIA operations.
- Forbid COM, BSL, agent CLI, Team/onboarding, generic execution, OSS-06 and
  reuse by another successor.

## Capabilities

### New Capabilities

- `qa-mcp-standalone-host-bridge-api-v1-investigation`: Exact bounded
  investigation decision for the OSS-05 public bridge API v1 successor.

### Modified Capabilities

- None.

## Impact

OpenSpec and board metadata only. No Python, Go, installer, protocol capture,
Windows host, live 1C, Docker or external-action behavior changes.
