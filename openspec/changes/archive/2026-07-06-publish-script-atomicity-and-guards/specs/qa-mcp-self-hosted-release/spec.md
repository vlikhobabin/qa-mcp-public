## ADDED Requirements

### Requirement: Self-hosted activation is atomic and immutable

The qa-mcp self-hosted publish helper SHALL activate a staged release on the
release server by copying into a temporary server-side version directory and
atomically moving that directory into `versions/<version>` only after the copy
has completed. After activation, the version directory SHALL be made read-only
for normal write paths so post-activation hand edits cannot silently mutate the
published asset set.

#### Scenario: Interrupted server copy does not wedge retries
- **WHEN** server activation is interrupted while assets are being copied to the
  release server
- **THEN** no final `versions/<version>` directory is left behind
- **AND** a later publish of the same version can retry activation after the
  temporary directory is cleaned

#### Scenario: Activated version directory is immutable
- **WHEN** server activation succeeds for version `vX.Y.Z`
- **THEN** `versions/vX.Y.Z` exists only after the complete staged directory has
  been copied
- **AND** the helper removes write permission from the activated version
  directory tree

### Requirement: Publish helper preserves explicit operator arguments

Ignored release environment files SHALL supply defaults only. Explicit
command-line arguments to `publish_self_hosted.sh` SHALL override values sourced
from `.ai/release.env` or legacy `.ai1c/release.env`.

#### Scenario: CLI version wins over release env
- **WHEN** `.ai1c/release.env` or `.ai/release.env` defines `VERSION`
- **AND** the operator invokes `publish_self_hosted.sh --version vCLI`
- **THEN** the staged manifest and directory use `vCLI`

#### Scenario: CLI release link wins over release env
- **WHEN** `.ai1c/release.env` or `.ai/release.env` defines `RELEASE_LINK_ID`
- **AND** the operator invokes `publish_self_hosted.sh --release-link-id r-cli`
- **THEN** the generated public release URL uses `r-cli`

### Requirement: Supplied image archive tag matches the manifest tag

When `--skip-build` stages an existing Docker archive, the publish helper SHALL
verify that the archive contains the image tag that will be written to
`manifest.json`. A mismatch SHALL fail before sidecars, manifest generation,
upload, or public-link activation.

#### Scenario: Missing image tag fails before staging
- **WHEN** the operator invokes `publish_self_hosted.sh --skip-build`
- **AND** `--image-archive` does not contain the supplied or default
  `--image-tag`
- **THEN** the helper exits non-zero with a clear image-tag mismatch error
- **AND** no version directory is staged

### Requirement: Delivery docs are generated through the manifest path

Durable qa-mcp delivery documents that are part of the tester handoff SHALL be
copied by `publish_self_hosted.sh`, receive sha256 sidecars, and be declared in
`manifest.json`. Post-activation manual copies into `versions/<version>` SHALL
not be a supported way to publish delivery docs.

#### Scenario: Agent install runbook is manifest staged
- **WHEN** the publish helper stages a self-hosted release
- **THEN** `agent-install-runbook.md` is present in the versioned release
  directory
- **AND** `agent-install-runbook.md.sha256` is present
- **AND** `manifest.json` declares `agent-install-runbook.md` with sha256 and
  size metadata

#### Scenario: Public link cleanup tolerates non-symlink entries
- **WHEN** activation succeeds and `public/` contains an unrelated non-symlink
  entry
- **THEN** cleanup skips that entry without causing the already-successful
  activation to exit non-zero
