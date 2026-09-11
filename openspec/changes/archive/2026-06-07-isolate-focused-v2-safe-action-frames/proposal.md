## Why

The focused proof must separate action traffic from bootstrap, background
refresh and recovery traffic before the lab can review any protocol claim. A
single joined range must remain candidate evidence unless later proof gates are
satisfied.

## What Changes

- Run the V2 reporter/frame-join tooling on the focused live capture output.
- Produce compact rows with action frame range, background ranges, recovery
  range, request/response sizes, dynamic fields, normalized hash candidates and
  action result markers.
- Preserve ambiguous joins as candidate, partial, timeout, rejected or blocked
  with explicit reasons.
- Hand isolated candidate evidence to the replay/probe or typed-contract proof
  change.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: The first focused V2 proof isolates action,
  background and recovery frame ranges before acceptance review.

## Impact

- Existing V2 safe-action reporter and corpus comparison outputs.
- Compact evidence under
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/` and
  `.artifacts/openspec/isolate-focused-v2-safe-action-frames/<run-id>/`.
- Requires the focused live capture output; no new live 1C runtime execution is
  required by this frame-review change.
