## ADDED Requirements

### Requirement: Focused V2 action frames are isolated before proof review
The protocol lab SHALL isolate action, background and recovery frame ranges for
the first focused V2 safe-action run before replay/probe or accepted-status
review.

#### Scenario: Action range is isolated
- **WHEN** the focused V2 reporter processes a live safe-action run
- **THEN** each reviewed row records an action frame range separately from
  bootstrap, background refresh and recovery ranges
- **AND** the row records request/response sizes, dynamic fields, normalized
  hash candidates and action result markers where available

#### Scenario: Join is ambiguous
- **WHEN** the action frame range cannot be isolated from background or
  recovery traffic
- **THEN** the row remains candidate, partial, timeout, rejected or blocked with
  an explicit reason
- **AND** accepted mapping output excludes the row

#### Scenario: Recovery range is separated
- **WHEN** the focused run includes recovery or recovery-read traffic
- **THEN** the recovery frame range is recorded separately from the action frame
  range
- **AND** recovery frames are not used as the action protocol request shape
