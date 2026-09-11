## ADDED Requirements

### Requirement: Manager fixture V1 cleanup acceptance is republished after probes
The protocol lab SHALL regenerate reviewed manager fixture V1 cleanup evidence
after pending-row classification and replay/direct-probe attempts, preserving
the accepted gate and documenting any residual pending rows.

#### Scenario: Accepted summaries are folded into the cleanup report
- **WHEN** retained replay/probe summaries match cleanup corpus rows
- **THEN** the regenerated live-join report marks those rows accepted
- **AND** each accepted row links the replay/probe evidence used for promotion

#### Scenario: Residual pending rows remain visible
- **WHEN** a row still lacks matching replay/probe proof or has a semantic
  mismatch
- **THEN** the regenerated report keeps the row non-accepted
- **AND** records the exact blocker and next route

#### Scenario: V2 readiness is stated
- **WHEN** the final manager fixture V1 cleanup report is published
- **THEN** protocol research docs state whether V2 safe-action planning is
  blocked, unblocked or allowed only with explicit residual risk
