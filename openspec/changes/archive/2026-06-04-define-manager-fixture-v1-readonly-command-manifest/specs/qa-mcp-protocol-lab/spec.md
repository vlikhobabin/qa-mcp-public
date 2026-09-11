## ADDED Requirements

### Requirement: Manager fixture V1 commands are manifest-driven and read-only

The protocol lab SHALL define manager V1 command execution through a manifest
and command catalog that describe only read-only TestManager API operations
against the client fixture V1 surface.

#### Scenario: Read-only manifest is loaded

- **WHEN** the manager V1 harness starts a read-only run
- **THEN** the input manifest records `run_id`, `case_id`, `command_id`, target
  fixture path, proxy TestClient port, target `PF_*` marker and expected
  response marker for each command
- **AND** commands that require text input, clicks, page switching, row
  selection, business commands or object writes are rejected from the V1
  accepted command catalog

#### Scenario: Command event is emitted

- **WHEN** the manager V1 harness executes one manifest command
- **THEN** it writes side-channel events with before and after timestamps,
  command status, target marker, expected marker, result preview and exception
  details when present
- **AND** it writes compact run output such as `case_events.jsonl` and
  `manager_harness_result.json` under the runtime directory selected by the
  capture runner
