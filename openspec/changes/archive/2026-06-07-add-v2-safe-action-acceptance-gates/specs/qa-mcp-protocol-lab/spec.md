## ADDED Requirements

### Requirement: V2 safe-action rows require replay/probe or typed contract proof for acceptance

The protocol lab SHALL promote a V2 safe-action row to accepted only when the
same non-mutating action has reviewed action evidence and accepted replay,
direct Python-manager probe or typed contract proof.

#### Scenario: Candidate action is not promoted by frame join alone

- **WHEN** a safe-action row has a joined `action_frame_range` but lacks
  accepted replay, probe or typed contract evidence
- **THEN** the row remains candidate or another explicit non-accepted status
- **AND** accepted-mapping output excludes the row

#### Scenario: Accepted action retains compact proof links

- **WHEN** a safe-action row is promoted to accepted
- **THEN** it retains normalized hash, dynamic fields, operation token,
  action result markers and compact proof evidence links
- **AND** raw replay or probe payloads remain outside reviewed git

### Requirement: V2 comparison output keeps non-accepted action rows visible

The protocol lab SHALL keep unresolved safe-action rows visible in comparison
output with explicit status and reason values.

#### Scenario: Non-accepted action remains visible

- **WHEN** comparison sees a `candidate`, `blocked`, `partial`, `timeout`,
  `rejected` or `unsupported` safe-action row
- **THEN** the row remains in comparison output
- **AND** the output records why the row is not accepted
