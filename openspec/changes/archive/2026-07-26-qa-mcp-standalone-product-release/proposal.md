## Why

The component helper still publishes a secret-link directory on the retired
release server, while the root product track now owns authenticated
`/qa-mcp/` catalogs and private immutable S3 publication. The component must
stage exact signed bytes without mutating remote release state.

## What Changes

- Stage standalone releases at product-version download paths.
- Retire component-side public-link generation and activation.
- Add solo-only standalone product guidance to the signed artifact inventory.
- Keep the frozen `ai1c.component-release.manifest.v1` identity contract.

## Capabilities

### New Capabilities

- `qa-mcp-standalone-product-release`: component-owned signed staging for the
  root authenticated standalone product publisher.

### Modified Capabilities

- None.

## Impact

This changes component release tooling, staged delivery documentation and
offline release tests. It does not require a live 1C runtime. It deliberately
does not edit the source activation files owned by the active
`license-activation-bootstrap` change.
