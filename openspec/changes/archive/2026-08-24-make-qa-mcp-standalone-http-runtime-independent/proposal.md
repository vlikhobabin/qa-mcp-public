## Why

OSS-02 now produces one readable, manifest-bound qa-mcp package, but the thin
image still requires an immutable suite-base input and `ai-mcp-proxy`, while
native Streamable HTTP MCP has no equivalent in-project Bearer boundary. A
public standalone image must build and run safely from public inputs alone
without dropping the inventory, provenance and archive-integrity gates already
established for that package.

## What Changes

- **BREAKING**: Replace the suite-base/proxy runtime contract with a direct
  project-owned HTTP application and public base image.
- Add authenticated Streamable HTTP MCP behavior with loopback-safe defaults.
- Standardize port, health, non-root execution and Windows/Linux Compose.
- Remove AI for 1C runtime environment names, private endpoints and private
  build inputs from standalone operation.
- Add clean-checkout build/start/authentication tests.
- Preserve the exact readable-package inventory, component-manifest, OCI
  revision and archive-digest reconciliation introduced by OSS-02.

## Capabilities

### New Capabilities
- `qa-mcp-independent-standalone-runtime`: Public-input Docker build and direct
  authenticated HTTP MCP runtime contract.

### Modified Capabilities
- `qa-mcp-suite-container-delivery`: Replace suite-base/proxy ownership with an
  independent public runtime while preserving remote TestClient behavior.
- `qa-mcp-http-transport-security`: Add built-in/project-owned authentication
  for non-loopback container serving instead of requiring a private proxy.

## Impact

Touches MCP provider startup, HTTP middleware, settings, Docker/Compose,
release verification, health/doctor behavior, tests and standalone docs. It
requires offline and container-network evidence plus Windows Docker Desktop
E2E of the standalone container boundary. It changes no protocol frames and
needs neither Vanessa MCP nor EDT/meta snapshots. Final extraction and release
qualification of the independent Windows bridge remains owned by OSS-05.
