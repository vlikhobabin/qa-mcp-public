## Why

The retained hidden direct-`/Execute` candidate combines too many lifecycle
layers to review and publish safely as one unit. Its lowest-level desktop,
process, environment and run-identity primitives must first become a bounded,
dormant foundation that can be verified independently.

## What Changes

- Add internal opaque run-identity and inherited-environment filtering
  primitives for one bounded hidden-desktop lifecycle.
- Add Windows-only primitives that create an exact named desktop and start an
  exact windowless worker executable on that desktop.
- Add focused hostile tests and Windows build/native verification without
  wiring the primitives into the current TestClient launch path.
- Keep the existing host behavior, HTTP/wire surface and stable MCP tool
  profile unchanged.

## Capabilities

### New Capabilities

- `qa-mcp-hidden-desktop-process-foundation`: Dormant, exact-owned Win32
  desktop/process/environment/run-identity primitives for later bounded
  hidden-worker successors.

### Modified Capabilities

- none

## Impact

The change touches only internal Go host-agent source, focused tests and
OpenSpec documentation. It does not touch protocol tools, Python manager code,
MCP provider setup or runtime lab configuration, and it requires no live 1C,
Vanessa MCP or EDT/meta snapshot; Linux unit tests, Windows cross-build and a
bounded Windows-native focused test are sufficient.
