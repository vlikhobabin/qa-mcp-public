## Why

Large Windows file infobases can time out when another 1C client is already
using the same base. Live MCP already consumes the host-agent marker probe for
Windows path evidence, but the host-agent does not expose a safe contention
signal that lets operators distinguish "slow first connect" from "possibly
busy file base".

## What Changes

- Extend the authenticated `POST /path/infobase` response with a best-effort
  active 1C process summary for the supplied file infobase path.
- Keep the signal secret-safe: return counts, process names, and path-match
  status only; never return command lines, usernames, passwords, connection
  strings, directory listings, or the raw requested path.
- Report `unavailable` with a reason when the host-agent cannot inspect process
  metadata on the current platform or host.
- Cover the probe logic with host-agent regression tests.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: the file-infobase host-agent probe may
  include secret-safe active 1C process evidence.

## Impact

- `host-agent/windows-display-agent/path_probe.go`
- Optional Windows-specific active process discovery for `1cv8*` processes.
- Focused host-agent tests.
- No desktop input, UI automation, live infobase writes, process termination, or
  arbitrary platform command execution.
