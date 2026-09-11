## ADDED Requirements

### Requirement: Self-hosted release assets are manifest driven
qa-mcp releases SHALL publish a component manifest, Docker archive, sha256 sidecars
and Windows assets under the qa-mcp self-hosted release namespace.

#### Scenario: Release staging creates versioned assets
- **WHEN** the publish helper stages version `vX.Y.Z`
- **THEN** it creates a manifest, image archive, sha256 sidecars, bootstrap,
  host-agent installer, host-agent executable and delivery docs in the versioned
  release directory

#### Scenario: Public release link is activated
- **WHEN** the helper is invoked with server activation options
- **THEN** exactly one current public qa-mcp release link points at the staged version

### Requirement: Bootstrap installs without GitHub or GHCR
The qa-mcp bootstrap SHALL install model B from `ReleaseBase` by downloading the
manifest and release assets, verifying sha256, loading the Docker archive and running
the loaded image tag.

#### Scenario: Bootstrap downloads from release base
- **WHEN** bootstrap runs with a self-hosted `ReleaseBase`
- **THEN** it downloads `manifest.json` and all required assets from that release
  base instead of GitHub Releases or GHCR

#### Scenario: Hash mismatch blocks execution
- **WHEN** a downloaded asset hash differs from the manifest value
- **THEN** bootstrap stops before executing that asset or loading the image

### Requirement: Bootstrap configures bearer-token MCP access
The qa-mcp bootstrap SHALL configure the suite proxy token for the container and
print MCP client configuration that includes a bearer token.

#### Scenario: Generated MCP token
- **WHEN** bootstrap runs without an explicit MCP proxy token
- **THEN** it generates one, passes it to the container, and includes it in the
  printed client configuration
