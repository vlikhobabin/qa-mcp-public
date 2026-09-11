## Why

The current Windows host-agent combines standalone TestClient/display control
with AI for 1C COM, BSL, Team registration, onboarding and generic execution.
The open product needs a narrow self-contained bridge whose complete source and
runtime dependency set can be published.

## What Changes

- Define a versioned public host-bridge capability contract.
- Retain only authenticated TestClient lifecycle/relay and bounded
  window/input/screenshot/UIA primitives.
- **BREAKING**: Remove COM worker, BSL supervisor, agent completion, Team
  registration/onboarding and arbitrary platform-execution endpoints from the
  public executable.
- Build and install the bridge using only public repository source.
- Preserve target-window binding, lifecycle ownership, token safety and exact
  cleanup evidence.

## Capabilities

### New Capabilities
- `qa-mcp-standalone-host-bridge`: Versioned open Windows TestClient/display
  bridge and compatibility handshake.

### Modified Capabilities
- `qa-mcp-windows-host-agent-security`: Narrow the executable to standalone
  capabilities while preserving authentication, target binding and cleanup.

## Impact

Touches Go host-agent code, its installer/schema, Python display/lifecycle
clients, tests and Windows documentation. Offline Go/contract tests and exact
Windows-native lifecycle/display/recovery evidence are required. It changes no
protocol claim and needs neither Vanessa MCP nor EDT/meta snapshots.
