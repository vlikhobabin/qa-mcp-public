## Why

The Windows host-agent display route cannot deliver `F5`, so qa-mcp's list
refresh path can report "no reachable display backend" even when attach and
read operations are otherwise working. The keymap currently knows `f4` but not
the rest of the function-key range used by 1C list refresh workflows.

## What Changes

- Add `F1` through `F12` virtual-key resolution to the host-agent keymap.
- Keep existing letter, digit, navigation, modifier, and `F4` behavior intact.
- Add a regression test that proves `virtualKey("f5")` resolves to `0x74` and
  the full function-key range resolves to `VK_F1` through `VK_F12`.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `qa-mcp-windows-host-agent-security`: extends the authenticated host-agent
  display-input contract to include function-key delivery needed by qa-mcp UI
  refresh flows.

## Impact

- Touches host-agent Go keymap code and tests under
  `host-agent/windows-display-agent/`.
- Does not change authentication, firewall, token, `/platform/execute`
  mutation-boundary behavior, native TestClient protocol frames, live 1C data,
  Vanessa MCP, EDT/meta snapshots, or runtime lab configuration.
- Verification is local Go unit coverage, Linux build coverage, OpenSpec
  validation, and a retained note that live Windows TestClient F5 delivery is
  not executed in this Linux workspace.
