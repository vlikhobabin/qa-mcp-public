## ADDED Requirements

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

The staged bootstrap SHALL select license product `qa-mcp` for activation and
runtime checks, SHALL use the source-pinned standalone-capable broker in the
protected image, and SHALL NOT embed or accept as a plain PowerShell parameter
a 1C password, shared license key, activation material, or bundled-data
decryption key.

#### Scenario: Standalone bootstrap artifact is inspected

- **WHEN** a signed standalone version is staged
- **THEN** activation and runtime gate configuration select product `qa-mcp`
- **AND** protected values must be supplied through caller-created,
  ACL-protected input files rather than tracked defaults or command-line
  string parameters

#### Scenario: Rendered artifact is checked on Windows

- **WHEN** the staged bootstrap is parsed by Windows PowerShell on the
  authorized architect workstation
- **THEN** it has no parser errors, exposes only protected-file secret inputs,
  and carries both activation and runtime product selection

### Requirement: Active license bootstrap ownership remains explicit

The standalone product release change SHALL NOT absorb or archive the active
`license-activation-bootstrap` change and SHALL record its dependency while
limiting this change to staged-artifact transformations and new standalone
guidance.

#### Scenario: Change scope is reviewed

- **WHEN** component diffs are compared with active OpenSpec ownership
- **THEN** the source bootstrap and its existing Windows activation runbook
remain owned by `license-activation-bootstrap`
