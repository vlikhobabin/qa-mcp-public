## ADDED Requirements

### Requirement: V2 readiness documentation reflects V1 read-only closure
The protocol lab SHALL keep current project status documentation aligned with
the final manager fixture V1 read-only readiness state before V2 safe-action
work starts.

#### Scenario: V2 planning reads current status
- **WHEN** a V2 safe-action card uses project readiness documentation as input
- **THEN** the documentation states whether manager fixture V1 read-only
  coverage blocks, partially blocks or unblocks V2 planning
- **AND** the current accepted evidence paths are cited instead of relying only
  on older baseline pending counts

#### Scenario: Side-channel rows are cited
- **WHEN** readiness documentation mentions diagnostic rows accepted through
  typed manager side-channel contracts
- **THEN** those rows are labeled as side-channel contract evidence
- **AND** they are not described as direct TestClient wire marker claims

### Requirement: V1 readiness does not accept V2 action mappings by inference
The protocol lab SHALL treat V1 read-only closure as a prerequisite for V2
planning, not as proof of any safe-action protocol mapping.

#### Scenario: V2 action evidence is absent
- **WHEN** docs state that V1 read-only no longer blocks V2
- **THEN** the docs also state that V2 action rows still require their own
  pre-state, action, post-state, recovery, frame-range and replay or direct
  probe evidence before acceptance
- **AND** deferred or supporting V1 evidence is not promoted into V2 action
  protocol knowledge
