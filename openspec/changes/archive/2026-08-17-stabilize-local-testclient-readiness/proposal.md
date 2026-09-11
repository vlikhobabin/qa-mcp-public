## Why

The local Linux launcher treats the first TCP accept as durable readiness. A
1C TestClient can expose TPort and then exit during license/session startup, so
the MCP call reports success even though the next protocol tool receives
connection refused. The stateless cleanup path then refuses to stop the owned
Xvfb because the primary PID is already gone. Project MCP profiles also point
at a target env file whose OData/runtime settings are not loaded by `Settings`,
and stdio doctor runs incorrectly require an HTTP bearer token by default.

## What Changes

- Require the owned process to survive a 20-second stability window after the
  non-consuming TPort listener check. Launch does not read the protocol
  greeting because that consumes the cold-client manager session.
- Return bounded, password-redacted launch output when post-listener readiness
  fails.
- Permit ownership-record-backed cleanup of an owned Xvfb after the primary
  client has exited, without weakening PID-reuse checks.
- Refuse occupied local TPorts and record ownership before readiness waits.
- Load runtime settings from `QA_MCP_TARGET_ENV_FILE`, with process environment
  overrides, and make doctor bearer defaults transport-aware.
- Classify manager ACK drift as a protocol-runtime diagnostic rather than an
  invalid tool argument.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `qa-mcp-protocol-lab`: local TestClient lifecycle readiness and cleanup are
  durable and fail-closed.

## Impact

- Local Linux lifecycle, runtime settings, doctor and structured protocol
  diagnostics with focused tests.
- No 1C configuration source, infobase data, protocol templates or Windows
  host-agent behavior changes.
