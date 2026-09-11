## ADDED Requirements

### Requirement: V2 safe-action handlers are allowlisted and local

The protocol lab SHALL execute only allowlisted fixture-local safe-action
families through the client fixture handler surface.

#### Scenario: Allowlisted action is handled

- **WHEN** a safe-action request targets focus, activation, page switching,
  local row selection or popup/menu/group expansion without command execution
- **THEN** the fixture performs only local UI state updates and records
  `PF_LAST_ACTION`, `PF_ACTION_COUNTER`, `PF_SELECTED_PAGE`,
  `PF_SELECTED_ROW` or `PF_FOCUSED_ELEMENT` as appropriate
- **AND** the action does not mutate business data

#### Scenario: Excluded action fails closed

- **WHEN** a request requires text input, checkbox or value toggle, business
  command click, object write, save, post, delete, fill, import, export or
  another external side effect
- **THEN** the fixture rejects the request before executing it
- **AND** the rejected action does not change the V2 safe-action state model

### Requirement: Safe-action handlers emit deterministic result markers

The protocol lab SHALL emit deterministic local action result markers for each
allowlisted handler execution.

#### Scenario: Handler emits markers

- **WHEN** a handler completes successfully
- **THEN** the fixture updates `PF_LAST_ACTION` and `PF_ACTION_COUNTER`
- **AND** the resulting markers distinguish the action from background refresh
  traffic
