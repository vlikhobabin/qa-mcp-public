## Why

Platform `8.3.27.2214` is installed in a connected development contour but
is not recorded in the 8.3 capture manifest. A failed legacy factory run used
the retired `vanessa_client` publication and therefore did not establish
protocol incompatibility.

## What Changes

- Run a genuine Vanessa TestManager capture on `8.3.27.2214` against a
  disposable demo infobase.
- Replay the existing bundled 8.3 protocol data through qa-mcp against the same
  live TestClient.
- Retain only sanitized counts and hashes in Git, and record the build as
  compatible when the read-only protocol checks are green.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `qa-mcp-self-hosted-release`: the same-family validated-build list includes
  `8.3.27.2214` without replacing the 8.3 capture templates.

## Impact

- Updates the 8.3 protocol-capture manifest, platform-support documentation and
  compact protocol evidence.
- Does not change Python runtime code, bundled payloads, 1C configuration
  source or business data.
