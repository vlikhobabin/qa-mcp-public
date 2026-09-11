## ADDED Requirements

### Requirement: Focused V2 safe-action proof attempts replay, probe or typed contract validation
The protocol lab SHALL attempt replay, direct Python-manager probe or typed
contract validation before the first focused V2 safe-action row is promoted to
accepted status.

#### Scenario: Proof succeeds
- **WHEN** a focused safe-action row has isolated action frames, recovery
  evidence and accepted replay, direct probe or typed contract proof for the
  same non-mutating action
- **THEN** the row may be marked accepted
- **AND** compact evidence records normalized hash, dynamic fields, operation
  token, request/response sizes and action result markers where available

#### Scenario: Proof is missing or fails
- **WHEN** a focused safe-action row lacks accepted replay, direct probe or
  typed contract proof
- **THEN** the row remains candidate or another explicit non-accepted status
- **AND** the row records the missing proof, failure reason and residual risk

#### Scenario: Raw proof payloads stay ignored
- **WHEN** replay or probe tooling writes request series, generated payloads,
  platform logs or raw runtime files
- **THEN** those files remain under ignored runtime or artifact paths
- **AND** reviewed git contains only compact proof summaries and evidence links
