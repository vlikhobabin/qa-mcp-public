## ADDED Requirements

### Requirement: Client fixture processor shell is target-bound and marker-visible
The protocol lab SHALL provide a dedicated V1 client fixture processor shell in
the `client` EDT target before adding broad read-only control coverage.

#### Scenario: Fixture shell is authored in the client target
- **WHEN** the processor shell is implemented
- **THEN** it is added under the `vanessa_client` EDT project
- **AND** `validate_project_infobase_binding(target_id="client", timeout_seconds=90)` is used before retrieve, update or hot-deploy work

#### Scenario: Fixture shell exposes top-level markers
- **WHEN** TestClient opens the fixture form
- **THEN** read-only form inspection can observe `PF_FORM_MAIN`
- **AND** read-only form inspection can observe `PF_FIXTURE_VERSION`
- **AND** the visible or inspectable version value is `protocol-fixture.v1`

#### Scenario: Fixture shell avoids business mutation
- **WHEN** the fixture form initializes
- **THEN** it does not create, edit, post or delete business objects
- **AND** it does not require catalogs, documents, registers or external services to expose its shell markers
