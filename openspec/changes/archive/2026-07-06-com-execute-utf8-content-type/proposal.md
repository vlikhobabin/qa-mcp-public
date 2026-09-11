## Why

`/com/execute` success responses currently return raw UTF-8 worker JSON with a
bare `application/json` content type. The rest of the host-agent JSON surface
declares `charset=utf-8`, so the COM bridge should make the same HTTP contract
explicit for localized 1C payloads.

## What Changes

- Change the `/com/execute` success response header to
  `application/json; charset=utf-8`.
- Preserve the existing raw worker JSON passthrough body and validation flow.
- Add a Go regression test that proves the header includes UTF-8 and the
  non-ASCII worker response body remains unchanged.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-windows-host-agent-security`: `/com/execute` success responses must
  declare UTF-8 JSON while preserving worker JSON passthrough.

## Impact

- Touches host-agent Go code and tests under
  `host-agent/windows-display-agent/`.
- Touches the existing host-agent security specification.
- Does not change native TestClient protocol tooling, Python manager runtime,
  MCP provider setup, or runtime lab configuration.
- Does not require live 1C runtime, Vanessa MCP, EDT/meta snapshots, or protocol
  capture/replay evidence; host-agent Go tests are sufficient for this
  header-only contract fix.
