# qa-mcp-standalone-product-release Specification

## Purpose

Define the staged artifact, authenticated download guidance, solo deployment,
and ownership boundaries for standalone qa-mcp product releases.
## Requirements
### Requirement: Component releases stage authenticated product-version paths

The qa-mcp release helper SHALL stage a signed
`ai1c.component-release.manifest.v1` inventory whose bootstrap and current
guidance use `/qa-mcp/download/versions/<version>/` and SHALL leave remote
publication to the root product publisher.

#### Scenario: A signed standalone release is staged

- **WHEN** the component release gates, artifact checks and manifest signing
  succeed
- **THEN** the exact version directory contains the signed manifest, all
  declared artifacts and checksum sidecars
- **AND** its current guidance uses the authenticated product-version path

#### Scenario: Legacy activation is requested

- **WHEN** an operator supplies `--activate` or `--server-root`
- **THEN** the helper fails before building, staging or changing remote state

### Requirement: Standalone component guidance is solo-only

The signed current standalone guidance SHALL support only one Windows
workstation and SHALL direct team deployment requests to the full-suite track
without emitting team deployment commands or credentials.

#### Scenario: Current staged guidance is inspected

- **WHEN** release-facing staged documents are scanned
- **THEN** they declare solo-only support
- **AND** they contain no active legacy distribution origin

### Requirement: Staged bootstrap selects the standalone license product

The staged bootstrap SHALL start qa-mcp without selecting, activating, or
checking a qa-mcp product license and SHALL NOT require an entitlement, lease,
license server, activation material, product-license broker, protected bundled
data key, or any other protection-only secret.

#### Scenario: Standalone bootstrap artifact is inspected

- **WHEN** a signed standalone version is staged
- **THEN** its bootstrap contains no qa-mcp product activation or runtime gate
  configuration
- **AND** it contains no invocation or required path for `ai1c-license`
- **AND** it contains no bundled-data key variable, file or command-line input

#### Scenario: Rendered artifact is checked on Windows

- **WHEN** the staged bootstrap is parsed by Windows PowerShell on the
  authorized architect workstation
- **THEN** it has no parser errors and exposes no qa-mcp entitlement,
  activation, lease, broker, product-license server or bundled-data key input

### Requirement: Active license bootstrap ownership remains explicit

The standalone product release SHALL supersede the active
`license-activation-bootstrap` work and SHALL remove it from the active change
set without applying its activation tasks or archiving it as completed.

#### Scenario: Change scope is reviewed

- **WHEN** component diffs and active OpenSpec changes are inspected
- **THEN** `license-activation-bootstrap` is absent from the active change list
- **AND** the replacement card and archived Git history retain the supersession
  lineage
