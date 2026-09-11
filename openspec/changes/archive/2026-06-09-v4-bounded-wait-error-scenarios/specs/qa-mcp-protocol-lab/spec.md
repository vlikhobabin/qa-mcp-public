## ADDED Requirements

### Requirement: V4 dialog scenarios produce deterministic results
The protocol lab SHALL provide fixture-local warning, question and modal-form
scenarios that expose deterministic text, lifecycle and selected-result
markers.

#### Scenario: Warning scenario records controlled text
- **WHEN** the V4 warning scenario is executed against the client fixture
- **THEN** the fixture exposes the expected warning text marker
- **AND** the result marker records that the warning was acknowledged or
  recovered through the documented path

#### Scenario: Question scenario records selected answer
- **WHEN** the V4 question scenario is answered through an allowlisted option
- **THEN** the fixture exposes the selected answer marker
- **AND** reset returns the question marker set to the baseline state

#### Scenario: Modal form opens and closes with markers
- **WHEN** a fixture-owned V4 modal form scenario runs
- **THEN** the open, close and result markers identify the modal lifecycle
- **AND** no OS, file, print or external-service dialog is involved

### Requirement: V4 expected errors are distinguishable from infrastructure failures
The protocol lab SHALL expose expected-error scenarios with controlled
diagnostic markers and SHALL keep infrastructure failures classified
separately.

#### Scenario: Expected error returns diagnostic marker
- **WHEN** a V4 expected-error scenario is executed
- **THEN** the resulting diagnostic text matches the expected error marker
- **AND** the scenario row is not treated as an infrastructure failure

#### Scenario: Unexpected error fails closed
- **WHEN** a V4 scenario returns an error that lacks the expected diagnostic
  marker
- **THEN** the row is classified as infrastructure failure, rejected or blocked
  according to the evidence contract
- **AND** no accepted protocol claim is published from that row

### Requirement: V4 wait scenarios are bounded and observable
The protocol lab SHALL limit V4 wait/progress scenarios to bounded
fixture-local durations and expose observable start, progress, completion,
cancel and recovery markers.

#### Scenario: Bounded wait completes
- **WHEN** a V4 bounded wait scenario starts
- **THEN** the fixture exposes wait-start and progress markers
- **AND** the scenario completes within the documented maximum duration with a
  completion marker

#### Scenario: Bounded wait is cancelled or retried
- **WHEN** a V4 wait scenario is cancelled or retried through the reviewed path
- **THEN** the fixture exposes the cancel or retry marker
- **AND** reset returns the wait marker set to the baseline state
