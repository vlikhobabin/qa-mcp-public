## Why

The shipped standalone bootstrap and protected-image checks still describe and
package qa-mcp product-license activation even though qa-mcp is now distributed
freely. Those delivery paths must stop requesting entitlement material,
shipping or invoking `ai1c-license`, and treating a compiled license gate as a
release invariant while preserving the separate bundled-data protection model.

## What Changes

- Remove product-license activation parameters, prompts, broker calls, lease
  mounts, and `QA_MCP_LICENSE_*` wiring from the source and generated
  standalone bootstrap paths and their current runbooks.
- Remove the `ai1c-license` binary and product-license gate assumptions from
  the protected thin image, compile list, verifier, and focused release tests.
- Keep `BUNDLED_DATA_KEY_FILE` only as an independently supplied runtime
  data-protection key path; do not obtain it from an entitlement or lease.
- Cancel and remove the active `license-activation-bootstrap` change as
  superseded work, without applying its activation tasks.
- Update durable release specifications so free startup and retained
  source/data/key protections are the normative shipped behavior.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-standalone-product-release`: the staged standalone bootstrap and
  guidance require no qa-mcp product activation, entitlement, lease, broker, or
  license server.
- `qa-mcp-comment-free-image`: the protected image continues compiling private
  implementation modules but no longer ships or verifies a product-license
  gate module or broker.
- `qa-mcp-protected-release-assets`: archive verification continues protecting
  readable source, plaintext bundled data, and runtime key material without
  treating product-license code as a gate.

## Impact

- **Delivery and image wiring:** `delivery/`, `docker/`, generated bootstrap
  rendering, release verification, and focused tests.
- **Docs and OpenSpec workflow:** current standalone/image documentation and
  the superseded active license activation change.
- **Runtime dependencies:** no live 1C runtime, Vanessa MCP, EDT/meta snapshot,
  license server, or broker is required; verification is offline plus the
  project-declared Windows PowerShell parser check where available.
- **Security boundary:** bundled protocol data remains encrypted and the
  runtime key remains absent from shipped layers and retained evidence.
