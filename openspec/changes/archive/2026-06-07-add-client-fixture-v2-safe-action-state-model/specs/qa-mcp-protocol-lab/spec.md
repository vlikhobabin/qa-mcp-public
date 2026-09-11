## ADDED Requirements

### Requirement: V2 safe-action state markers are local and observable

The protocol lab SHALL expose a resettable fixture-local state model for V2
safe actions.

#### Scenario: Fixture opens with local markers

- **WHEN** TestClient opens the client fixture V2 surface
- **THEN** read-only inspection can observe `PF_LAST_ACTION`,
  `PF_ACTION_COUNTER`, `PF_SELECTED_PAGE`, `PF_SELECTED_ROW`,
  `PF_FOCUSED_ELEMENT` and `PF_RESET_STATE`
- **AND** the markers describe only local UI state, not business objects or
  external services

#### Scenario: Safe action updates local state

- **WHEN** a fixture-local safe action changes focus, page, row selection or
  activation state
- **THEN** the relevant `PF_*` markers change in a deterministic way
- **AND** the update does not write business data

### Requirement: V2 safe-action state can be reset to the baseline

The protocol lab SHALL restore the V1 baseline after a V2 safe action is
completed or reset.

#### Scenario: Reset returns fixture to baseline

- **WHEN** `PF_RESET_STATE` or an equivalent reset hook is invoked after a
  safe action
- **THEN** the fixture returns to the baseline state that existed before the
  action
- **AND** the local selection, focus and page markers no longer retain the
  prior action state
- **AND** no business data is created, edited, posted or deleted
