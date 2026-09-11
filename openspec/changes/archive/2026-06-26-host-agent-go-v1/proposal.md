## Why

The display backend needs a small native process on the Windows host because
the Linux container cannot call Win32 `SendInput`, `PrintWindow`, `BitBlt` or
`EnumWindows`. The risky keyboard primitive was already proven with ctypes on
the live Windows lab; v1 packages that primitive into a static Go host agent.

## What Changes

- Add a Windows host-side Go agent executable source tree.
- Expose `GET /version`, `GET /health`, and primitive endpoints for keyboard,
  Unicode typing, mouse click, screenshot and OS window listing.
- Implement Win32 primitives with `golang.org/x/sys/windows`.
- Bind only to loopback/host-only addresses and require a shared token for
  mutating or data-returning primitive calls.
- Return PNG screenshot bytes and structured JSON results suitable for the
  Python remote display backend.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: the lab provides a Windows host-side input/screenshot
  agent that serves the display primitives required by model-B remote-client
  mode.

## Impact

- Adds Go source and tests for the host agent.
- Adds Windows-native build and smoke commands to documentation.
- Requires Windows-native verification for `SendInput`, screenshot and window
  enumeration against the lab host.
- Does not require 1C metadata edits or live infobase writes by itself.
