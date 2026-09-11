## ADDED Requirements

### Requirement: Manager V2 safe-action catalog is fail-closed
The protocol lab SHALL define manager fixture V2 safe-action rows through a
reviewed catalog or manifest before any manager-runner execution.

#### Scenario: Safe-action catalog row is executable
- **WHEN** a manager V2 safe-action row includes action id, target id, target
  marker, pre-state, action, post-state, recovery expectation,
  `mutates_business_data=false`, allowlisted action family and expected result
  markers
- **THEN** the manager runner may treat the row as executable candidate input
- **AND** the row remains non-accepted protocol evidence until live proof and
  replay/probe or typed contract evidence are reviewed

#### Scenario: Unsafe catalog row is rejected
- **WHEN** a manager V2 safe-action row is incomplete, mutating, unsupported or
  outside the V2 allowlist
- **THEN** the manager runner rejects the row before execution
- **AND** the rejection records reason, owner and residual risk
