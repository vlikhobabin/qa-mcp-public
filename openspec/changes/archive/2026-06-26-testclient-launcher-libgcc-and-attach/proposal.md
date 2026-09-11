## Why

`launch_test_client` can fail before the TestClient port opens when the bundled
1C runtime resolves an older `libgcc_s.so.1` ahead of the system library needed
by host shared libraries. The current timeout hides the underlying process
error, and externally booted clients lack a first-class attach/session path for
the protocol tools that need to drive an already-listening TestClient.

## What Changes

- Add launcher environment handling that can preload a system `libgcc_s.so.1`
  for native Linux TestClient boots, with explicit opt-out and override
  controls.
- Improve failed launch diagnostics so the timeout response includes bounded
  stderr or `/Out` log evidence without exposing credentials.
- Add a documented attach-to-running-client path that returns a TestClient
  handle for an already-listening host/port and establishes the same protocol
  session entry point used by lifecycle-owned launches.
- Cover the lifecycle behavior with offline tests and plan live runtime
  evidence for the Linux lab contour.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: TestClient lifecycle and direct session tooling must
  support diagnostic native launch failures and attach-driven protocol access
  to already-running clients.

## Impact

- Affected code: `src/qa_mcp/protocol/lifecycle.py`,
  `src/qa_mcp/mcp_server.py`, protocol package exports and lifecycle/session
  tests.
- Affected systems: native Linux 1C TestClient process launch, the MCP
  `launch_test_client`/status surface, and tools that drive protocol sessions
  by `host:port`.
- Runtime: offline tests are required first; live 1C launch evidence requires
  the qa-mcp Linux runtime preflight and the `vanessa_client` file infobase to
  be free.
- Not in scope: Windows launcher work, host-agent display/input work, new raw
  protocol claims, raw capture publication, business data mutation, or replacing
  existing protocol replay templates.
