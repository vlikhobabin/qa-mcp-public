## ADDED Requirements

### Requirement: Supported 8.5 capture lookup uses validated 8.3 protocol data

The Python protocol runtime SHALL resolve capture-backed operation data for the
supported `8.5` family through the validated `8.3` bundled capture set until an
8.5-specific bundle is populated. The active platform version MUST remain the
live 8.5 version for synthesized frames, full captured-replay frames and
diagnostics; only capture-data path selection falls back.

#### Scenario: 8.5 capture-backed read resolves to bundled 8.3 data

- **WHEN** `QA_MCP_PLATFORM_VERSION` or an explicit resolver argument selects
  platform family `8.5`
- **THEN** `resolve_capture_dir("nextrow")` resolves to the bundled `8.3`
  capture directory when no `8.5` capture exists
- **AND** the result is not reported as `capture-not-found` for the supported
  fallback case

#### Scenario: 8.5 full replay declares the live platform version

- **WHEN** a capture-backed full replay uses the validated 8.3 protocol-data
  fallback while `QA_MCP_PLATFORM_VERSION=8.5.1.1343`
- **THEN** the replay sends frames stamped with `8.5.1.1343`
- **AND** it does not declare the captured 8.3 platform version to the live 8.5
  TestClient session

#### Scenario: Direct 8.3 lookup remains unchanged

- **WHEN** platform family `8.3` is active
- **THEN** capture-backed operation lookup resolves to bundled `8.3` data
- **AND** no fallback warning or unsupported-family behavior is involved

#### Scenario: Undeclared platform family still fails closed

- **WHEN** platform family `9.0` or another undeclared family is selected
- **THEN** active version resolution rejects it before capture lookup
- **AND** the error names supported families and the capture refresh runbook
