## ADDED Requirements

### Requirement: Real demo mutation corpus publication states final row status
The protocol lab SHALL publish real demo mutation pilot outcomes with explicit
row status, evidence links and residual risk.

#### Scenario: Real demo mutation pilot is published
- **WHEN** target selection, manifest review, guarded execution or blocked
  outcome and frame-isolation review have completed
- **THEN** publication records every selected or attempted row with target id,
  operation family, mutation flag, recovery status, frame-isolation status,
  proof route, final status, evidence paths and residual risk
- **AND** the API coverage case map and generated coverage report are
  refreshed when row statuses changed
- **AND** publication states whether the mutation scheme is proven well enough
  to plan the follow-up batch corpus card
- **AND** raw runtime output remains outside reviewed git

#### Scenario: Row is blocked or rejected
- **WHEN** a selected real-demo mutation row cannot execute, cannot recover,
  lacks frame evidence or violates the manifest contract
- **THEN** publication records the blocker or rejection reason, owner route and
  next actionable evidence need
- **AND** the row is not omitted from corpus coverage notes

### Requirement: Real demo mutation accepted output is proof-gated
The protocol lab SHALL keep accepted mutation output empty unless accepted
proof exists for the same real-demo action.

#### Scenario: Accepted row is published
- **WHEN** a real demo mutation row is added to accepted output
- **THEN** the publication links separated action-frame evidence plus
  same-action replay, direct Python-manager probe or accepted typed contract
  proof
- **AND** the row records recovery status and any residual demo data risk

#### Scenario: Accepted proof is missing
- **WHEN** the pilot has target, manifest, runtime or frame evidence but lacks
  accepted replay, direct probe or typed contract proof
- **THEN** accepted output remains empty for that row
- **AND** the row is published as candidate, blocked, rejected, partial or
  timeout with evidence paths and residual risk
