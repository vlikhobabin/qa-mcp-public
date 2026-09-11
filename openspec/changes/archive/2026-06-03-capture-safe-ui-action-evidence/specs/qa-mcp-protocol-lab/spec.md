## ADDED Requirements

### Requirement: Safe UI action captures produce compact evidence
The protocol lab SHALL retain compact reviewed evidence for every attempted
safe UI action capture and keep raw runtime output outside reviewed git
changes.

#### Scenario: Safe action capture is reviewed
- **WHEN** a Windows-native capture runs a safe UI action case
- **THEN** reviewed evidence records `case_id`, `api_call`, `ui_target`,
  pre-state, action, post-state, recovery expectation, frame range,
  normalized hash, dynamic fields, operation token, response markers, replay
  status and action result markers
- **AND** raw TCP captures, platform logs and case-event runtime payloads
  remain under ignored `runtime/protocol-research/` paths

### Requirement: Unsupported safe UI action captures remain visible
The protocol lab SHALL record unavailable or unsupported safe UI action cases
instead of silently omitting them from the matrix.

#### Scenario: Safe action target is unavailable
- **WHEN** a selected safe UI action cannot be performed against the current
  lab form or cannot be joined to a reviewed frame range
- **THEN** the compact evidence records `unsupported`, `pending`, `partial`,
  `timeout` or `rejected` status with an unresolved reason
- **AND** the row is not accepted as protocol knowledge

### Requirement: Safe action capture performs no business mutation
The protocol lab SHALL prevent safe UI action captures from writing persisted
business data.

#### Scenario: Capture scenario attempts a mutating operation
- **WHEN** a capture scenario would execute a command with side effects, enter
  text, toggle persisted values, edit a table, save, post, delete or otherwise
  mutate business data
- **THEN** the scenario is rejected before capture
- **AND** the rejected operation is routed to a separate mutation-specific
  card with rollback expectations
