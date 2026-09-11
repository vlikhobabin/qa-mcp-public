## MODIFIED Requirements

### Requirement: Windows host-agent artifacts are reproducible and source-bound

The qa-mcp release tooling SHALL provide one non-interactive Linux command that
builds and verifies the current Windows amd64 GUI host-agent from a clean
checkout, emits a sha256 sidecar and machine-readable provenance, and SHALL make
the signed self-hosted publisher consume that same verified artifact contract
for both built and explicitly supplied assets.

#### Scenario: Clean checkout builds the current artifact

- **WHEN** the host-agent artifact command runs from a clean checkout with Go
  available
- **THEN** it emits `qa-mcp-host-agent.exe`, its sha256 and a provenance
  manifest without requiring an operator-authored cross-build command
- **AND** the manifest identifies source revision/fingerprint, agent version,
  toolchain, target architecture and Windows GUI subsystem.

#### Scenario: Identical inputs build reproducibly

- **WHEN** the artifact is built twice from identical source and Go toolchain
- **THEN** both executable sha256 values are equal
- **AND** both bundles pass the same verifier.

#### Scenario: Stale or incomplete executable is refused

- **WHEN** an executable has the wrong PE architecture/subsystem, missing or
  mismatched VCS/source metadata, or lacks a required bridge-registration,
  BSL-supervision or TestClient marker
- **THEN** verification exits non-zero before release staging or installation
- **AND** the diagnostic names the missing or mismatched bounded contract fact.

#### Scenario: Public release stages a built verified artifact

- **WHEN** `publish_self_hosted.sh` builds a release rather than receiving an
  explicit existing executable
- **THEN** it obtains the executable through the shared artifact builder
- **AND** the existing detached signed component manifest remains the download
  trust anchor for bootstrap installation.

#### Scenario: Public release stages a supplied verified bundle

- **WHEN** `publish_self_hosted.sh` receives an explicit existing executable,
  including when regression gates are skipped
- **THEN** it requires and verifies the adjacent source-bound bundle manifest
  and sha sidecar before copying any asset into the version staging directory
- **AND** a bare, stale or source-mismatched executable fails before staging.

#### Scenario: Dirty source is explicit

- **WHEN** a release build has tracked host-agent inputs that differ from HEAD
- **THEN** the builder fails closed by default
- **AND** a local test-only override records dirty state and the actual source
  fingerprint rather than claiming clean-HEAD provenance.
