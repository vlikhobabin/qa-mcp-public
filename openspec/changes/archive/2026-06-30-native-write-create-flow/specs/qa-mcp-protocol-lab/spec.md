## ADDED Requirements

### Requirement: Native write scenarios can fill and save a record in one session
The qa-mcp write scenario tool SHALL execute field input steps and explicit save/command steps on one live native write session when the scenario is intended to create or persist a record.

#### Scenario: Multi-field create flow saves successfully
- **WHEN** a write scenario opens a create form, sets multiple fields and invokes a save command
- **THEN** qa-mcp keeps the same TestClient/write session for all fill and save steps
- **AND** the result reports each step status, the save command status and the persistence verification status

#### Scenario: Unsupported write step fails closed
- **WHEN** a write scenario contains a step that qa-mcp cannot execute safely
- **THEN** the scenario result marks that step as an error with the step kind and reason
- **AND** qa-mcp does not silently skip the step or report the scenario as passed

### Requirement: Create-flow persistence proof is retained
The qa-mcp create/write flow SHALL require read-back, list-read, live-data or explicit provider-gap evidence before a persisted record creation claim is accepted.

#### Scenario: Persistence verification is available
- **WHEN** the save command reports accepted
- **THEN** qa-mcp records a read-back, list-row or data-layer assertion summary showing the created record state
- **AND** cleanup evidence or cleanup residual risk is recorded for the created test data
