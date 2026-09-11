## ADDED Requirements

### Requirement: Focused V2 safe-action run records live phase evidence
The protocol lab SHALL capture the first focused manager fixture V2 safe-action
run with phase-aware evidence for reviewed subset rows only.

#### Scenario: Reviewed row is captured
- **WHEN** a row from the focused subset is executed by the
  `manager-fixture-v2-safe-action` scenario
- **THEN** the run records pre-read, action-start, action-end, post-read and
  recovery or recovery-read events with action id, target id, action family and
  result markers
- **AND** when phase timestamps and proxy traffic are both retained, compact
  evidence records separate action, background and recovery frame ranges
- **AND** raw captures, platform logs and generated replay payloads remain
  under ignored runtime paths

#### Scenario: Row cannot safely execute
- **WHEN** the selected row is unavailable, disabled, incomplete, mutating,
  outside the V2 allowlist or cannot prove post-state or recovery
- **THEN** the run fails closed for that row with typed status and reason
- **AND** no broader UI action or business-data mutation is attempted

#### Scenario: Recovery evidence is retained
- **WHEN** a focused safe-action row completes its action phase
- **THEN** the run records recovery evidence or documented known-state evidence
- **AND** the row remains unavailable for acceptance review when recovery
  evidence is missing
