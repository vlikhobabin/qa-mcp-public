## ADDED Requirements

### Requirement: V3 mutation state markers are local and observable

The protocol lab SHALL expose a resettable fixture-local mutation state model
for V3 scenarios.

#### Scenario: Fixture opens with local mutation markers

- **WHEN** TestClient opens the client fixture V3 surface
- **THEN** read-only inspection can observe the mutation baseline markers
- **AND** the markers describe only local UI state, not business objects or
  external services

### Requirement: V3 mutation targets declare deterministic expected values

The protocol lab SHALL declare stable initial values and expected mutated
values for each V3 mutation target family.

#### Scenario: Editable targets expose initial and expected values

- **WHEN** TestClient opens the client fixture V3 surface
- **THEN** read-only inspection can observe initial and expected value markers
  for string, number and date targets
- **AND** those markers are stable across reset and rerun cycles

#### Scenario: Checkbox targets expose initial and expected values

- **WHEN** TestClient opens the client fixture V3 surface
- **THEN** read-only inspection can observe initial and expected state markers
  for checkbox targets
- **AND** those markers are stable across reset and rerun cycles

#### Scenario: Mutation target markers are target-specific

- **WHEN** the fixture publishes V3 mutation markers
- **THEN** each editable and checkbox target has a target-specific value marker
  and expected-result marker
- **AND** the marker set can distinguish string, number, date and checkbox
  cases during evidence review

### Requirement: V3 mutation state updates are observable

The protocol lab SHALL publish target-specific post-state and recovery markers
for every V3 mutation case.

#### Scenario: Mutation updates local state deterministically

- **WHEN** a fixture-local mutation scenario changes an editable value, a
  checkbox, an inert action marker or a local counter
- **THEN** the relevant `PF_*` markers change in a deterministic way
- **AND** the update does not write business data

#### Scenario: Mutation exposes post-state and recovery markers

- **WHEN** a V3 mutation scenario completes
- **THEN** the fixture exposes a target-specific post-state marker
- **AND** the reset path exposes a recovery marker proving the baseline was
  restored

### Requirement: V3 mutation state can be reset to the baseline

The protocol lab SHALL restore the V1 baseline after a V3 mutation scenario is
completed or reset.

#### Scenario: Reset returns fixture to baseline

- **WHEN** `PF_RESET_STATE` or an equivalent reset hook is invoked after a
  mutation
- **THEN** the fixture returns to the baseline state that existed before the
  scenario
- **AND** the local value, checkbox, focus and counter markers no longer retain
  the prior mutation state
- **AND** no business data is created, edited, posted or deleted
