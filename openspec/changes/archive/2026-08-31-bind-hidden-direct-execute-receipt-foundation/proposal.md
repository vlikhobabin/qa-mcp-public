## Why

Published S1-S5 prove a dormant hidden direct-execute lifecycle in Go, but
Python has no typed way to accept its successful result while binding the
receipt to the exact current-run cleanup identity. A mutable, stale or foreign
receipt must not be able to select or repeat cleanup when S7 later integrates
the chain.

## What Changes

- Add a dormant portable Go envelope that validates the published lifecycle,
  S4 observation and optional S5 prompt receipt, then binds their exact current-
  run identity to one opaque cleanup hash and single-use stop lease.
- Add an internal Python parser/lease that requires the same exact typed schema
  and expected cleanup binding before one injected cleanup callback.
- Reject malformed, stale, replayed, foreign, ambiguous or post-bind-mutated
  receipt/stop identity before any cleanup, action or public callback.
- Keep all public host capability, Python/MCP tool and profile routes disabled.

## Capabilities

### New Capabilities

- `qa-mcp-hidden-direct-execute-receipt-foundation`: Internal cross-language
  typed receipt validation, immutable current-run cleanup binding and single-
  use stop behavior for the dormant hidden direct-execute chain.

### Modified Capabilities

- None.

## Impact

- Adds only isolated portable Go/Python source and adjacent tests plus S6
  OpenSpec/card artifacts; published S1-S5 and dirty integration files remain
  unchanged.
- Touches Python manager internals and OpenSpec documentation, but not protocol
  capture/replay tools, MCP provider setup, public schemas, dependencies or lab
  configuration.
- Verification is offline. No live 1C runtime, Windows prompt rerun, Vanessa
  MCP, EDT/meta snapshot or raw capture evidence is required because certified
  Windows behavior and its artifact boundary do not change.
