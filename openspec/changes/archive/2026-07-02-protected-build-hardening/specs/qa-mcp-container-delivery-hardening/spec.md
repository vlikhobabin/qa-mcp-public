## ADDED Requirements

### Requirement: Images run as non-root and expose healthchecks

qa-mcp Docker images SHALL run the MCP process as a non-root user and SHALL define a lightweight healthcheck suitable for local Docker and Compose runs.

#### Scenario: Runtime user is non-root
- **WHEN** either shipped qa-mcp image is inspected
- **THEN** its configured runtime user is not root
- **AND** runtime-writable directories required by qa-mcp are owned by that user

#### Scenario: Image defines a healthcheck
- **WHEN** either shipped qa-mcp image is inspected
- **THEN** it defines a healthcheck command for the local MCP service

### Requirement: Delivery inputs are immutable

qa-mcp delivery images and release workflow SHALL pin external mutable inputs used for published artifacts. Base images SHALL be pinned by digest, and GitHub Actions used by the release workflow SHALL be pinned to full commit SHAs.

#### Scenario: Base images are digest pinned
- **WHEN** the Dockerfiles are reviewed
- **THEN** every `FROM` image used for published artifacts includes a `sha256` digest

#### Scenario: Release actions are SHA pinned
- **WHEN** `.github/workflows/release.yml` is reviewed
- **THEN** every `uses:` entry for a GitHub Action is pinned to a full commit SHA rather than a mutable major tag

### Requirement: Published verification runs the strengthened protected-image check

The release workflow SHALL run the strengthened protected-image verifier before publishing protected artifacts.

#### Scenario: Pre-publish verifier is authoritative
- **WHEN** the release workflow builds a protected image
- **THEN** it runs `docker/verify_protected_image.py`
- **AND** the script includes gate-module, docstring-leak and decrypt-round-trip checks
