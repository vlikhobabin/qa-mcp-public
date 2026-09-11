## ADDED Requirements

### Requirement: Manager fixture runner shell is target-bound

The protocol lab SHALL provide a manager-side fixture runner shell in the
`manager` EDT target before using a 1C TestManager instance as the controlled
read-only corpus generator.

#### Scenario: Manager runner shell is prepared

- **WHEN** the manager fixture runner shell is implemented
- **THEN** source and deploy operations use `target_id="manager"` with project
  `vanessa_manager` and infobase `vanessa_manager`
- **AND** retained evidence records a successful manager project-to-infobase
  binding check before runtime apply or hot deploy

#### Scenario: Manager runner shell bootstraps the client fixture

- **WHEN** the manager runner starts a V1 run
- **THEN** it accepts `run_id`, proxy TestClient port, client fixture
  navigation target and output directory as explicit run context
- **AND** it labels client fixture form-open traffic as bootstrap rather than
  a read-only corpus case
- **AND** it performs no TCP parsing or protocol normalization inside 1C
