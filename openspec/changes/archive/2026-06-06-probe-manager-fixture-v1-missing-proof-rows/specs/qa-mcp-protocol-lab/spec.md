## ADDED Requirements

### Requirement: Missing-proof manager fixture V1 rows are probed with current-run identity

The protocol lab SHALL attempt focused replay or direct-probe proof for manager
fixture V1 pending rows that lack proof before promoting, correcting or using
the rows for V2 readiness.

#### Scenario: Missing-proof row is accepted

- **WHEN** a focused replay or direct probe is used to accept a missing-proof
  pending row
- **THEN** the retained summary records the current cleanup run id, case id,
  manager frame range, normalized hash, response marker and dynamic-field
  adaptation
- **AND** the reporter validates those fields against the cleanup corpus row

#### Scenario: Missing-proof row remains pending

- **WHEN** replay/direct-probe proof is absent, mismatched, ambiguous or from
  the wrong endpoint
- **THEN** the row remains non-accepted
- **AND** the retained summary records the exact blocker and next route

#### Scenario: Older evidence is supporting only

- **WHEN** older probe evidence exists for the same conceptual operation
- **THEN** it can be linked as supporting context
- **AND** it SHALL NOT promote the current cleanup row unless reconciled with
  the current run range and normalized hash
