## ADDED Requirements

### Requirement: Pending manager fixture V1 rows require current-run probe proof
The protocol lab SHALL promote a pending manager fixture V1 read-only row only
when retained replay or direct-probe evidence matches the current cleanup run
identity and expected semantic response.

#### Scenario: Probe proof matches the cleanup row
- **WHEN** replay or direct-probe evidence is used to accept a pending row
- **THEN** the evidence records the cleanup run id, case id, manager frame
  range, normalized hash, response marker and dynamic-field adaptation
- **AND** the reporter can validate those fields against the joined corpus row

#### Scenario: Probe proof is mismatched
- **WHEN** replay transport succeeds but the expected marker, endpoint, frame
  range or normalized hash does not match the cleanup row
- **THEN** the row remains non-accepted
- **AND** the mismatch is retained as reviewed evidence

#### Scenario: Older probe evidence is supporting only
- **WHEN** older probe evidence exists for the same conceptual operation
- **THEN** it can be linked as supporting context
- **AND** it SHALL NOT promote the current cleanup row unless reconciled with
  the current run range and normalized hash
