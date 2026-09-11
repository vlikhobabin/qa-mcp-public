# qa-mcp-container-delivery-hardening Specification

## Purpose

qa-mcp delivery images and release workflows use safe runtime defaults and
immutable published inputs so local Docker and source-visible-image users do
not inherit avoidable container or supply-chain exposure.

## Requirements

### Requirement: Images run as non-root and expose healthchecks

qa-mcp Docker images SHALL run the MCP process as a non-root user and SHALL
define a lightweight healthcheck suitable for local Docker and Compose runs.

#### Scenario: Runtime user is non-root
- **WHEN** either shipped qa-mcp image is inspected
- **THEN** its configured runtime user is not root
- **AND** runtime-writable directories required by qa-mcp are owned by that user

#### Scenario: Image defines a healthcheck
- **WHEN** either shipped qa-mcp image is inspected
- **THEN** it defines a healthcheck command for the local MCP service

### Requirement: Delivery inputs are immutable

qa-mcp delivery images and release workflow SHALL pin external mutable inputs
used for published artifacts. Base images SHALL use a literal digest or a
mandatory build argument that the release path validates as a digest reference,
and GitHub Actions used by the release workflow SHALL be pinned to full commit
SHAs.

#### Scenario: Base images are digest pinned
- **WHEN** the Dockerfiles are reviewed
- **THEN** every `FROM` image used for published artifacts is resolved from an
  immutable `sha256` digest

#### Scenario: Release actions are SHA pinned
- **WHEN** `.github/workflows/release.yml` is reviewed
- **THEN** every `uses:` entry for a GitHub Action is pinned to a full commit SHA
  rather than a mutable major tag

### Requirement: Published verification checks open package integrity

The release workflow SHALL verify that the source-visible image contains the
expected readable qa-mcp modules and curated assets, imports successfully and
matches the release manifest before publication.

#### Scenario: Public image verification passes
- **WHEN** a tagged source-visible image is built and saved
- **THEN** expected modules and plaintext curated assets are present and usable
- **AND** no private credential, private binary or undeclared artifact is
  required or included.
