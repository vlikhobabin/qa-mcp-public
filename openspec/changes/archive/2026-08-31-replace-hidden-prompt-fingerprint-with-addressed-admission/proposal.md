## Why

Fresh per-run EPFs made the hidden direct-`/Execute` security prompt observable,
but exhausted S5 still rejected it before action because admission required one
exact whole-window UIA fingerprint. S5-R1 replaces that brittle proof with the
minimum exact addressed boundary needed for safe prompt confirmation.

## What Changes

- Admit one exact lifecycle-owned prompt and one unique stable target action
  without requiring fixed total control/Invoke/Value counts or a fixed hash of
  the complete prompt topology.
- Re-admit the exact prompt/action tuple immediately before one single-use,
  exact-HWND-addressed confirmation and retain the published S4 post-state.
- Emit bounded sanitized diagnostics for inventory failures and prove fresh-EPF
  prompt/recovery plus exact-owned cleanup.
- Record listener `18081` presence, absence, unknown ownership and independent
  drift only as read-only diagnostics. They do not gate a native run, and S5
  never connects to, restarts, stops, repairs or reconfigures the listener.
- Keep Python, MCP, public/wire/profile admission and S6/S7 behavior unchanged.

## Capabilities

### New Capabilities

- `qa-mcp-minimal-addressed-prompt-admission`: Minimal fail-closed prompt and
  target-action admission, single-use addressed confirmation and passive
  post-state proof for the dormant hidden direct-execute lifecycle.

### Modified Capabilities

- None.

## Impact

- Affects only the four isolated S5 Go policy/Windows adapter/test paths plus
  S5-R1 OpenSpec/card documentation and ignored native evidence.
- Does not change protocol tools, captures, Python manager code, MCP provider
  setup, public APIs, dependencies or persistent runtime configuration.
- Delivery requires exact Windows 1C runtime evidence on the authorized historical-user
  contour. It does not require Vanessa MCP, EDT/meta snapshots or protocol
  capture/replay evidence.
