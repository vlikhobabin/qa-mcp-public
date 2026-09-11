## ADDED Requirements

### Requirement: Manager fixture V1 harness executes manifest runs end to end

The protocol lab SHALL provide a manager-side V1 harness entrypoint that loads
a read-only manifest, executes each command against the proxied TestClient and
writes side-channel evidence under the selected runtime directory.

#### Scenario: Manifest command sequence is executed

- **WHEN** the manager V1 harness is invoked with a valid read-only manifest
- **THEN** it connects to the TestClient through the manifest proxy port
- **AND** it executes the manifest commands in order
- **AND** it writes before and after `case_events.jsonl` records for each
  command
- **AND** it writes `manager_harness_result.json` with command counts and final
  run status

#### Scenario: Command failure is retained as evidence

- **WHEN** one read-only command raises a TestManager or platform exception
- **THEN** the harness records the exception summary in the command after-event
- **AND** the final result records failed and completed counts
- **AND** already written events remain in the runtime directory

#### Scenario: Non-read-only command is rejected

- **WHEN** the manifest contains an action, input, command execution or write
  command kind
- **THEN** the manager V1 harness rejects the run before executing the command
- **AND** the result records a fail-closed status without accepting any
  protocol mapping
