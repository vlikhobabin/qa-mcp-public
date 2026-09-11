## MODIFIED Requirements

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
