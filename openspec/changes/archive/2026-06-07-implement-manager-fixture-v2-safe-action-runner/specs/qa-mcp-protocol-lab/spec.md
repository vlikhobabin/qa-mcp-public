## ADDED Requirements

### Requirement: Manager V2 runner executes only allowlisted safe actions
The protocol lab SHALL execute manager fixture V2 safe actions only when the
row passes the reviewed catalog and belongs to an allowlisted non-mutating
action family.

#### Scenario: Runner executes an allowlisted action
- **WHEN** the manager V2 runner receives a validated row for an allowlisted
  target and action family
- **THEN** the runner reads pre-state, executes the action and reads post-state
- **AND** the action is recorded as candidate evidence, not accepted protocol
  knowledge

#### Scenario: Runner rejects unsafe action
- **WHEN** the requested action is missing, disabled, mutating, outside the V2
  allowlist or cannot prove post-state
- **THEN** the runner fails closed before or during execution with a typed
  rejected or blocked result
- **AND** no business data write or external side effect is attempted
