## ADDED Requirements

### Requirement: Runtime target values are immutable and provider neutral
qa-mcp SHALL expose immutable public values for runtime fingerprints, target
bindings, provider observations, local profiles and evidence policy without a
runtime dependency on suite providers.

#### Scenario: Consumer imports the contract
- **WHEN** a standalone or downstream consumer imports the public core package
- **THEN** it can construct the runtime-target contract values around the
  existing `TargetIdentity`
- **AND** mutation of a constructed value is rejected.

### Requirement: Provider profile schema is closed and packaged
The distribution MUST contain a JSON schema that requires the complete
runtime-target profile shape and rejects unknown fields.

#### Scenario: Complete profile is validated
- **WHEN** a profile supplies binding, target, physical-config reference,
  evidence policy and observation fields
- **THEN** schema validation accepts the document.

#### Scenario: Unknown or incomplete profile is validated
- **WHEN** a required field is absent or an undeclared field is present
- **THEN** schema validation rejects the document.

### Requirement: Contract introduction has no runtime authority
The contract payload SHALL NOT resolve a project handoff, start a process,
connect to an infobase or mutate runtime state.

#### Scenario: Contract tests execute offline
- **WHEN** the contract and packaging verification runs
- **THEN** no TestClient, X display, host-agent or infobase operation occurs.
