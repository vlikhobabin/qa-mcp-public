## MODIFIED Requirements

### Requirement: Staged bootstrap selects the standalone license product

The staged bootstrap SHALL start qa-mcp without selecting, activating, or
checking a qa-mcp product license and SHALL NOT require an entitlement, lease,
license server, activation material, or product-license broker. Protected
bundled-data key input, when required by the release, SHALL be supplied through
a caller-created ACL-protected file and SHALL remain independent of product
licensing.

#### Scenario: Standalone bootstrap artifact is inspected

- **WHEN** a signed standalone version is staged
- **THEN** its bootstrap contains no qa-mcp product activation or runtime gate
  configuration
- **AND** it contains no invocation or required path for `ai1c-license`
- **AND** any bundled-data key must be supplied through a caller-created,
  ACL-protected input file rather than a tracked default or command-line string

#### Scenario: Rendered artifact is checked on Windows

- **WHEN** the staged bootstrap is parsed by Windows PowerShell on the
  authorized architect workstation
- **THEN** it has no parser errors and exposes no qa-mcp entitlement,
  activation, lease, broker, or product-license server input
- **AND** any retained protected-file input is identified only as the external
  bundled-data decryption key

### Requirement: Active license bootstrap ownership remains explicit

The standalone product release SHALL supersede the active
`license-activation-bootstrap` work and SHALL remove it from the active change
set without applying its activation tasks or archiving it as completed.

#### Scenario: Change scope is reviewed

- **WHEN** component diffs and active OpenSpec changes are inspected
- **THEN** `license-activation-bootstrap` is absent from the active change list
- **AND** the replacement card and archived Git history retain the supersession
  lineage
