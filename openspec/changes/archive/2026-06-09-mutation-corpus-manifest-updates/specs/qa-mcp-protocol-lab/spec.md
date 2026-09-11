## ADDED Requirements

### Requirement: V3 mutation rows use a fail-closed manifest shape

The protocol lab SHALL require a machine-readable manifest row for every V3
mutation case before capture or publication.

#### Scenario: Incomplete row is rejected

- **WHEN** a mutation row is missing `target_marker`, `pre_state`, `action`,
  `post_state`, `recovery_expectation`, `mutates_business_data=false`,
  `mutation_family` or `expected_action_result_markers`
- **THEN** the row fails closed
- **AND** the fixture or runner does not accept it for capture

#### Scenario: Complete row is reviewable

- **WHEN** a mutation row provides all required manifest fields
- **THEN** the row can be reviewed against the V3 mutation contract
- **AND** the row can proceed to the next evidence step if the rest of the
  pipeline is ready

#### Scenario: Row names baseline, post-state and recovery markers

- **WHEN** a mutation row targets a string, number, date, checkbox or inert
  button case
- **THEN** the row names the target marker, initial value marker, expected
  mutated marker, post-state marker and recovery marker
- **AND** the row remains rejected until those markers are present in reviewed
  fixture evidence

### Requirement: V3 mutation evidence is published as compact reviewed links

The protocol lab SHALL publish V3 mutation proof as compact evidence links and
summaries rather than raw captures in git.

#### Scenario: Evidence publication retains compact links

- **WHEN** a V3 mutation proof is published
- **THEN** the reviewed evidence references compact bundle paths and summary
  artifacts
- **AND** raw traffic or generated replay payloads remain outside reviewed git
  changes
