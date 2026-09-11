## ADDED Requirements

### Requirement: V2 safe-action tooling validates manifest rows before capture

The protocol lab SHALL validate V2 safe-action manifest rows before capture,
reporting or manager-runner execution.

#### Scenario: Complete row can proceed to capture

- **WHEN** a safe-action row includes the required target, state, recovery,
  allowlist and expected result marker fields
- **THEN** tooling may pass the row to the safe-action scenario
- **AND** the row remains non-accepted until evidence proves the action

#### Scenario: Incomplete row fails closed

- **WHEN** a safe-action row is missing a required manifest field
- **THEN** tooling rejects it before capture or execution
- **AND** the rejected row records a reason, provider owner and residual risk
  when it is retained for coverage review

### Requirement: V2 safe-action manifest excludes mutation families

The protocol lab SHALL reject text input, checkbox/value toggles, business
commands, object writes and external side effects from V2 safe-action rows.

#### Scenario: Mutation family is rejected

- **WHEN** a manifest row uses an action family outside the V2 allowlist
- **THEN** tooling fails closed before capture
- **AND** the row is routed to later mutation or recovery work instead of V2
