## ADDED Requirements

### Requirement: Demo button pilot publication states final status
The protocol lab SHALL publish every demo real-button pilot result with an
explicit final status and compact evidence links.

#### Scenario: Demo button pilot is published
- **WHEN** the target selection, classification and capture or blocked result
  have been reviewed
- **THEN** publication records the selected target, safety classification,
  attempted or skipped action, recovery status, evidence paths, final status
  and residual risk
- **AND** raw runtime output remains outside reviewed git

#### Scenario: Accepted status is claimed
- **WHEN** the demo button pilot is published as accepted
- **THEN** the publication links same-action replay, direct Python-manager
  probe or typed contract proof for the non-mutating action
- **AND** accepted-mapping output includes only rows supported by that proof

#### Scenario: Proof is missing
- **WHEN** the pilot has target, classification or capture evidence but lacks
  accepted replay, direct probe or typed contract proof
- **THEN** publication marks the row candidate, blocked, rejected or another
  explicit non-accepted status
- **AND** accepted-mapping output excludes the row

### Requirement: Demo mutation outcomes route to V3
The protocol lab SHALL route demo button results that write data, execute
business commands or require rollback to V3 or later mutation/recovery work.

#### Scenario: Demo button requires mutation handling
- **WHEN** classification or capture shows the selected button is mutating,
  business-owned, rollback-dependent or outside the V2 allowlist
- **THEN** the publication records `routed_to_v3` or equivalent blocker status
  with owner route, evidence links and residual risk
- **AND** no accepted safe-action mapping is published for the row
