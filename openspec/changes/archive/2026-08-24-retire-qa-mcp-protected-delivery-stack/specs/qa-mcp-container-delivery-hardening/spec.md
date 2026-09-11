## MODIFIED Requirements

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

## REMOVED Requirements

### Requirement: Published verification runs the strengthened protected-image check
**Reason**: The protected-image scanner enforces confidentiality requirements
that are intentionally retired.
**Migration**: Use the new source-visible package and asset-integrity release
checks.

## ADDED Requirements

### Requirement: Published verification checks open package integrity
The release workflow SHALL verify that the source-visible image contains the
expected readable qa-mcp modules and curated assets, imports successfully and
matches the release manifest before publication.

#### Scenario: Public image verification passes
- **WHEN** a tagged source-visible image is built and saved
- **THEN** expected modules and plaintext curated assets are present and usable
- **AND** no private credential, private binary or undeclared artifact is
  required or included.
