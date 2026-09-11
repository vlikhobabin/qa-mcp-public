## Why

The source-bound Windows proof for lifecycle-window routing currently loses the
HTTP and structured-error boundary at `type_text`, so the blocked S50-120 card
cannot distinguish a proof-client parsing failure from a host-agent or desktop
session failure. A bounded diagnosis is needed before product code is changed or
the Windows verification floor is weakened.

## What Changes

- Capture only the `type_text` HTTP status class and normalized structured error
  code in ignored runtime evidence.
- Classify the failure as proof-client transport/parsing, host-agent
  `foreground-denied`, desktop-session diagnostics, or unexpected process exit.
- If the ignored proof harness is defective, repair that harness and rerun the
  complete source-bound S50-120 route/session/cleanup matrix.
- If product code is defective, produce a linked implementation-card handoff
  with the exact invariant and verification floor instead of editing the product
  in this investigation.

## Capabilities

### New Capabilities

- `windows-display-transport-proof-diagnostics`: Bounded and sanitized
  diagnostic behavior for Windows display-route proof transport failures.

### Modified Capabilities

- None.

## Impact

The change touches OpenSpec workflow/card state and ignored Windows proof
artifacts only. It does not change protocol tools, Python manager code, MCP
provider setup, durable docs, or runtime lab configuration. Verification needs
the authorized Windows workstation and owned fixtures, but does not access a
live 1C runtime or infobase and does not require Vanessa MCP or EDT/meta
snapshots.
