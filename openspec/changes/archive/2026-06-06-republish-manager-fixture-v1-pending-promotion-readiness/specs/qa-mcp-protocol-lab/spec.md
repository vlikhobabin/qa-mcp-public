## ADDED Requirements

### Requirement: Manager fixture V1 pending-promotion work is republished as a readiness state

The protocol lab SHALL republish manager fixture V1 read-only cleanup evidence
after pending-row promotion attempts and state the resulting V2 readiness.

#### Scenario: Accepted and pending counts are regenerated

- **WHEN** retained pending-row probe, isolation and marker-contract evidence
  exists
- **THEN** the protocol lab regenerates the reviewed live-join report with all
  accepted and non-accepted summaries folded in
- **AND** the report records coherent accepted and pending counts for all 17
  command windows

#### Scenario: Accepted rows link proof

- **WHEN** a row is promoted to accepted
- **THEN** the final report links the replay or direct-probe evidence used for
  promotion
- **AND** that evidence matches case id, manager frame range and
  normalized hash

#### Scenario: V2 readiness is published

- **WHEN** the final manager fixture V1 pending-promotion report is published
- **THEN** protocol research docs state whether V2 safe-action acceptance is
  unblocked, blocked, or allowed only by explicit residual-risk decision
- **AND** any remaining pending rows retain precise blocker evidence
