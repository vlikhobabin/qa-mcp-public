## ADDED Requirements

### Requirement: Manager V2 safe-action rows prove recovery
The protocol lab SHALL prove recovery or a documented known final state for
every executable manager fixture V2 safe-action row.

#### Scenario: Safe action recovers to baseline
- **WHEN** a manager V2 safe-action row completes
- **THEN** the runner executes the documented recovery path or records why no
  cleanup is required
- **AND** the post-recovery read shows the expected baseline or known-state
  markers

#### Scenario: Recovery proof is missing
- **WHEN** a V2 safe-action row lacks recovery markers, recovery frame range or
  known-state rationale
- **THEN** the row remains candidate, blocked, rejected, partial or timeout
- **AND** the row is not promoted as accepted safe-action evidence

#### Scenario: Action reruns after recovery
- **WHEN** the first focused candidate subset is recovered
- **THEN** the same action row can be run again with the same observable
  pre-state and result markers
