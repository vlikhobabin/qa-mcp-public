## ADDED Requirements

### Requirement: The released GHCR image is the protected build
The release pipeline (`.github/workflows/release.yml`) SHALL build and publish the
thin image through the protected build path — compiled `protocol/` `.so` and
encrypted `_bundled` data — so the public `ghcr.io/vlikhobabin/qa-mcp-thin` image
is the protected build. The AES-GCM encryption key SHALL be supplied from a **CI
secret** (never committed). The **local** `docker build` path SHALL still produce
a working protected image.

#### Scenario: A tagged release publishes a protected image
- **WHEN** a version tag triggers `release.yml` and the GHCR image is pushed
- **THEN** the published image has compiled `protocol/` (no readable `protocol/*.py`)
  and encrypted `_bundled` data
- **AND** the encryption key came from a CI secret, not from the repository

#### Scenario: Local builds still work
- **WHEN** a maintainer runs `docker build -f docker/Dockerfile.thin` locally
- **THEN** the build succeeds and produces a working protected image (using a
  documented local/default key or build-arg), without requiring CI

#### Scenario: Added build cost is documented
- **WHEN** the protected build runs in CI
- **THEN** the release/CI docs record the added build time (Nuitka compile +
  encrypt) and the one-time key-secret setup
