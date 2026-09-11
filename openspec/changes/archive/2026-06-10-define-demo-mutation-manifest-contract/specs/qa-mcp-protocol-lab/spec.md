## ADDED Requirements

### Requirement: Real demo mutation manifest rows are complete before execution
The protocol lab SHALL define every real demo mutation attempt through a
complete reviewed manifest row before guarded execution.

#### Scenario: Manifest row is executable
- **WHEN** a real demo mutation row is selected for guarded execution
- **THEN** the row records `target_id`, object or form path, element path,
  target marker, operation family, pre-state, action, expected post-state,
  recovery expectation, `mutates_business_data`, residual risk and proof route
- **AND** `mutates_business_data=true` is allowed only when the recovery or
  cleanup plan is explicit and reviewed

#### Scenario: Manifest row fails closed
- **WHEN** a real demo mutation row is incomplete, unsupported, lacks recovery,
  has ambiguous target state or includes unapproved external side effects
- **THEN** the row is rejected or blocked before guarded execution
- **AND** the retained row records reason, owner route and residual risk

### Requirement: Real demo mutation statuses are proof-gated
The protocol lab SHALL classify real demo mutation rows with explicit status
and proof route before publication.

#### Scenario: Row status is recorded
- **WHEN** a real demo mutation row is retained for corpus review
- **THEN** the row status is one of `accepted`, `candidate`, `rejected`,
  `blocked`, `partial` or `timeout`
- **AND** the row records whether evidence came from replay, direct
  Python-manager probe, typed contract proof, live capture only or blocked
  validation

#### Scenario: Accepted output is requested
- **WHEN** a real demo mutation row is proposed for accepted mapping output
- **THEN** the row has same-action replay, direct Python-manager probe or
  accepted typed contract proof for the same action
- **AND** live visual success or manifest completeness alone does not create
  accepted protocol knowledge
