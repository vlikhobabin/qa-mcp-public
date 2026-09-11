## ADDED Requirements

### Requirement: Real demo mutation targets are selected before execution
The protocol lab SHALL select real demo mutation candidates through a reviewed
read-only target record before manifest validation or guarded execution.

#### Scenario: First row set is selected
- **WHEN** the real-demo mutation pilot chooses candidate rows
- **THEN** each selected row records `target_id`, form or object path, element
  path, visible caption or marker, operation family, expected mutation,
  recovery feasibility, evidence route, owner and residual risk
- **AND** the selected set remains small enough to review before execution

#### Scenario: Candidate is rejected or deferred
- **WHEN** a real demo form action cannot be reviewed safely, lacks a stable
  target marker or has unclear recovery feasibility
- **THEN** the target-selection evidence records the candidate as rejected,
  deferred or blocked with reason, owner route and residual risk
- **AND** no click or write is attempted for that candidate

### Requirement: Target selection does not create mutation proof
The protocol lab SHALL keep target selection separate from runtime execution,
frame evidence and accepted protocol mappings.

#### Scenario: Target selection completes
- **WHEN** the target-selection summary is published for downstream manifest
  review
- **THEN** the summary contains only read-only evidence and candidate metadata
- **AND** it does not claim action-frame ranges, replay status, direct
  Python-manager proof or accepted mapping output
