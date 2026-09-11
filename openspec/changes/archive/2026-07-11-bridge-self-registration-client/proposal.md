## Why

Team-server consumers cannot route a user session to that user's Windows host-agent until the agent advertises its reachable endpoint and refreshes the registry lease. The frozen team topology requires dynamic self-registration and forbids operator-maintained per-developer bridge entries.

## What Changes

- Add an opt-in host-agent registry client that registers once at startup and then on a configurable heartbeat (30 seconds by default) with a 90-second TTL.
- Send the immutable configured user, reachable endpoint, per-developer token, and current `ai1c.windows-host-bridge.discovery.v1` body using the additive `ai1c.bridge-registration.v1` envelope.
- Treat authorization and network failures as bounded, secret-safe status while leaving all existing bridge endpoints available.
- Preserve solo mode: without registry configuration the client creates no registry requests and reports disabled state.
- Verify on Linux with an in-process fixture registry. A real Windows host-agent and live root registry round-trip remain supervised provider gaps.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: add secret-safe, fail-soft bridge self-registration and solo-mode behavior to the host-agent contract.

## Impact

- Host-agent Go configuration, lifecycle, authenticated health output, tests, and operator documentation.
- No TestClient protocol tooling, Python manager protocol behavior, MCP provider setup, live 1C runtime, Vanessa MCP, EDT/meta snapshot, or runtime lab configuration changes.
- Depends on the root-owned registry schema/service for live integration; the component implementation is tested offline against a fixture registry.
