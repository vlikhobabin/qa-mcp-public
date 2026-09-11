## Why

Model-B remote-client mode can drive the 1C TestClient protocol over TCP, but
the display-bound tools still assume a local Linux X display. On Windows the
rendered 1C client lives in the host desktop session, so screenshots, raw input
and OS window enumeration need a backend seam that can route to a host agent.

## What Changes

- Add a `DisplayBackend` abstraction for keyboard, mouse, screenshot and OS
  window-list primitives.
- Wrap the existing Linux XTEST/scrot/ImageMagick behavior in
  `LocalXTestBackend` so model A keeps the current behavior.
- Add `RemoteAgentBackend`, selected by `QA_MCP_REMOTE_CLIENT=1` plus
  `QA_MCP_HOST_AGENT`, to call a host-side HTTP display agent.
- Convert the current display-only MCP guard return points into backend
  dispatch points where a remote backend is configured.
- Route `open_external_processor` through the same backend path so it no longer
  crashes in remote-client mode.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: display-bound MCP tools select a local or remote
  backend and fail closed with actionable diagnostics when the display backend
  is unavailable.

## Impact

- Touches Python manager code and MCP provider setup under `src/qa_mcp/`.
- Touches protocol display helpers:
  `src/qa_mcp/protocol/native_xtest.py`,
  `src/qa_mcp/protocol/screenshot.py`, and
  `src/qa_mcp/protocol/windows.py`.
- Touches MCP tool routing in `src/qa_mcp/mcp_server.py`.
- Requires offline unit tests for backend selection/dispatch and Linux
  behavior preservation.
- Requires live Windows runtime only for final remote backend verification; the
  abstraction itself is testable offline with a fake HTTP agent.
