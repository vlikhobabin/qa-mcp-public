## Why

The Windows host-agent exposes desktop-control endpoints that can type, click and capture windows. Its default install path currently makes that surface reachable from the LAN and keeps the bearer token visible in the scheduled-task command line.

## What Changes

- Scope the Windows host-agent listener and firewall rule so desktop-control traffic is local or explicitly allowlisted by default.
- Move token delivery out of the scheduled-task process command line and into a protected token source.
- Require constant-time token validation and apply authentication to sensitive status and control endpoints.
- Reject hostile browser origins and add a small rate limit around authenticated request handling.
- Document the secure install and Docker Desktop routing choices in the host-agent runbook.

## Capabilities

### New Capabilities
- `qa-mcp-windows-host-agent-security`: Windows host-agent installs and serves desktop-control endpoints with network scope, token handling and endpoint authentication that fail closed by default.

### Modified Capabilities
- none

## Impact

Touches Windows host-agent Go code, the Windows install PowerShell script, focused Go tests and delivery documentation. This does not require live 1C runtime, Vanessa MCP, EDT/meta snapshots or protocol capture evidence; verification is source inspection plus `go test ./...`.
