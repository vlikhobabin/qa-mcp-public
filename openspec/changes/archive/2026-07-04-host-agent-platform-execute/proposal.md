## Why

Containerized admin/config flows need a controlled way to run host-installed 1C
platform binaries (`ibcmd`, `1cv8`, `1cv8c`) when those binaries are not present
inside the Linux container. The qa-mcp Windows host-agent is already the
token-authenticated host bridge, but it currently exposes no platform-command
execution endpoint.

## What Changes

- Add authenticated `POST /platform/execute` to the Windows host-agent.
- Resolve only allowlisted 1C platform executables from configured platform
  catalog directories, never from arbitrary request paths.
- Require operation and mutation-boundary fields, including operator intent for
  `platform_command_execute`.
- Run platform commands with bounded stdout/stderr, timeout process-group kill,
  exit-code reporting, and secret-bearing argument redaction.
- Extend authenticated `/health` with bounded 1C platform catalog diagnostics.
- Update host-agent README coverage and Go tests for allowlist, auth,
  policy-field validation, timeout, redaction, and catalog discovery.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `qa-mcp-windows-host-agent-security`: adds the authenticated, allowlisted
  host-side platform command execution boundary and its fail-closed behavior.

## Impact

- Touches host-agent Go code and tests under `host-agent/windows-display-agent/`.
- Touches `host-agent/README.md`.
- Touches the existing `qa-mcp-windows-host-agent-security` capability.
- Does not touch native TestClient protocol capture/replay, Python manager MCP
  tools, live 1C metadata/source mutation, Vanessa MCP, EDT/meta snapshots, or
  runtime lab configuration. Verification is Go unit coverage, Windows
  cross-compile/build coverage, OpenSpec validation, and a retained Windows
  host smoke note when a real Windows host is unavailable in this Linux pass.
