## Why

Source compilation, stripping and bundled-data encryption no longer serve the
fully open standalone product or the server-side AI for 1C cloud product. They
now obstruct reproducible builds and impose key management on code that will be
public in every deployment.

## What Changes

- **BREAKING**: Remove the protected-image build and runtime-key contract.
- Remove Nuitka compile stages, source/docstring stripping, bundled-data
  encryption/decryption and protection-only verifiers.
- Ship readable Python source and plaintext curated protocol assets in wheels
  and images for both standalone and AI for 1C consumption.
- Remove protection-only dependencies, tests, release inputs and active docs.
- Replace secrecy gates with package integrity, asset loading and reproducible
  source-build checks.

## Capabilities

### New Capabilities
- `qa-mcp-open-source-runtime-assets`: Readable source and plaintext curated
  runtime assets with integrity and loadability verification.

### Modified Capabilities
- `qa-mcp-comment-free-image`: Retire every requirement that hides or strips
  readable implementation material.
- `qa-mcp-protected-release-assets`: Retire encrypted-asset and protected-image
  release gates.
- `qa-mcp-protocol-lab`: Replace protected GHCR/source/data requirements with
  open-source delivery behavior.
- `qa-mcp-container-delivery-hardening`: Remove the protected-image verifier as
  a release gate while retaining ordinary container hardening.
- `qa-mcp-container-build-cache`: Remove protection-specific cache invariants
  and retain reproducible dependency/source layering.
- `qa-mcp-ci-quality-gates`: Gate source-visible release artifacts on the
  offline pytest job instead of naming a protected image.
- `qa-mcp-standalone-product-release`: Remove the final bundled-data key input
  from standalone bootstrap and Windows parsing requirements.
- `qa-mcp-suite-container-delivery`: Replace the protected builder/ABI contract
  with the source-visible image and immutable suite-base input.

## Impact

Touches Python runtime code, package dependencies, Dockerfiles, CI/release and
bootstrap inputs, build helpers, tests, active OpenSpec specs and documentation.
It needs offline package/image evidence, a container runtime smoke and a
key-free check of the current Windows standalone contract; it introduces no new
protocol claim and does not require Vanessa MCP or EDT/meta snapshots. Building
the final public release train belongs to OSS-08, and downstream AI for 1C
pinning/cutover belongs to OSS-09.
