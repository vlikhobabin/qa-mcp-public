## ADDED Requirements

### Requirement: V3 mutation handlers update only local fixture state

The protocol lab SHALL route V3 mutation inputs through local fixture handlers
that change only transient state.

#### Scenario: Editable value changes stay local

- **WHEN** TestClient enters a text, number or date value into a V3 mutation
  target
- **THEN** the corresponding local marker changes deterministically
- **AND** `PF_LAST_ACTION`, the action counter and the target-specific
  post-state marker reflect the mutation
- **AND** no business object, register or external side effect is written

#### Scenario: Checkbox toggles stay local

- **WHEN** TestClient toggles a V3 mutation checkbox
- **THEN** the checkbox state and related local markers change deterministically
- **AND** `PF_LAST_ACTION`, the action counter and the checkbox post-state
  marker reflect the toggle
- **AND** no persisted business data is changed

#### Scenario: Mutation handlers retain recovery markers

- **WHEN** a V3 mutation handler completes and the reset hook is invoked
- **THEN** the target-specific recovery marker proves that the baseline value
  or checkbox state was restored
- **AND** the same mutation can be run again with the same observable markers

### Requirement: V3 inert actions do not invoke business commands

The protocol lab SHALL treat inert V3 buttons as local marker updates only.

#### Scenario: Inert button click updates local action markers

- **WHEN** TestClient clicks a V3 inert button
- **THEN** only `PF_LAST_ACTION`, counters or other local markers change
- **AND** the click does not run a business command or external side effect

### Requirement: Unsupported mutation targets fail closed

The protocol lab SHALL reject V3 mutation targets that are not explicitly
allowlisted for local mutation handling.

#### Scenario: Unsupported target is rejected

- **WHEN** a mutation request targets a control that is outside the reviewed
  local mutation set
- **THEN** the request fails closed
- **AND** the fixture state remains unchanged
