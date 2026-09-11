## Why

Windows model-B installs rely on the host-agent `/window_list` response to find
the live 1C TestClient window. Tester feedback showed Russian titles returned as
mojibake, forcing ASCII-only title matching and making automated bootstrap less
reliable.

## What Changes

- Preserve localized window titles from the Windows host-agent as valid UTF-8
  JSON end to end.
- Keep `/window_list` usable for automatic 1C window selection and expose enough
  structured data for diagnostics when only the generic `Клиент тестирования`
  fallback is available.
- Add Go coverage for non-ASCII titles and keep a Windows-native smoke checklist
  for the real desktop path.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: host-agent display introspection must
  preserve localized window titles and diagnose weak window matching without
  breaking authenticated endpoint boundaries.

## Impact

- Touches host-agent Go code under `host-agent/windows-display-agent/`.
- Touches bootstrap/runtime diagnostics only where they consume `/window_list`.
- Requires offline Go tests in this Linux workspace and a retained Windows-native
  smoke transcript when a Windows desktop/TestClient host is available.
- Does not require protocol capture, live Linux TestClient replay, EDT/meta
  snapshots, or business-data mutation.
