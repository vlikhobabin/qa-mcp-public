## Why

The host agent cannot be pushed or started from a cold Linux container because
there is no container-to-host file/exec channel and Windows Session 0 cannot
drive the interactive desktop. Users need a one-time host-side install step and
the container needs a version/hash handshake that fails with exact remediation
instructions.

## What Changes

- Add a Windows install script that copies `qa-mcp-host-agent.exe` to a stable
  location, registers an interactive logon Scheduled Task and configures the
  firewall rule for the agent port.
- Add container-side handshake logic that calls `/version`, compares the
  expected version/hash, and blocks remote display calls on mismatch.
- Return a clear install/update command in mismatch or absent-agent errors.
- Document that v1 detects and instructs only; it does not auto-replace the
  host binary.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: model-B display backend startup includes host-agent
  install instructions and version/hash negotiation that fail closed.

## Impact

- Touches Python remote backend handshake code.
- Adds Windows install/update documentation and script assets.
- Touches Docker/model-B docs so users know the required second port and token.
- Requires Windows-native install-script syntax/behavior verification.
