## ADDED Requirements

### Requirement: Manager V2 safe-action runs record phase boundaries
The protocol lab SHALL record manager fixture V2 safe-action phase events that
allow action, background and recovery traffic to be reviewed separately.

#### Scenario: Safe-action event sequence is complete
- **WHEN** a manager V2 safe-action row executes
- **THEN** `case_events.jsonl` records pre-read, action-start, action-end,
  post-read and recovery or recovery-read events with action id, target id,
  action family and result markers
- **AND** candidate frame-range correlation inputs are retained for the V2
  reporter

#### Scenario: Boundary is ambiguous
- **WHEN** a V2 action boundary cannot be joined to frames or chunk counters
  reliably
- **THEN** the row remains candidate, partial, timeout, rejected or blocked
- **AND** the ambiguity is visible in reviewed evidence
