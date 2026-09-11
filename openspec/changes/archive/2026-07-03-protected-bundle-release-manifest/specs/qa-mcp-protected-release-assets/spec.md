## ADDED Requirements

### Requirement: Release manifest declares protected baked protocol assets
The qa-mcp component release manifest SHALL declare that encrypted `_bundled/`
protocol data is baked into the protected image and SHALL NOT publish it as a
separate data asset.

#### Scenario: Manifest has no qa data archive
- **WHEN** qa-mcp release assets are staged
- **THEN** the manifest lists the protected image archive and an empty qa data asset
  list for `_bundled`

#### Scenario: Manifest records carve-out rationale
- **WHEN** the manifest is inspected
- **THEN** it records that `_bundled/` is small encrypted protocol IP and is not a
  swappable external data plane artifact

### Requirement: Protected image verification remains the release gate
qa-mcp releases SHALL run protected-image verification before publishing or
activating the self-hosted release link.

#### Scenario: Protected verifier passes
- **WHEN** `docker/verify_protected_image.py` succeeds against the release image
- **THEN** the publish helper can stage the image archive and manifest

#### Scenario: Protected verifier fails
- **WHEN** the protected verifier reports readable protocol source, plaintext
  bundled data or import/tool-surface failure
- **THEN** the publish helper fails before upload or public-link activation
