## ADDED Requirements

### Requirement: Fixture read-only capture records compact wire evidence

The protocol lab SHALL generate compact corpus evidence for available
controlled read-only fixture cases before those cases are classified.

#### Scenario: Fixture case is captured

- **WHEN** a controlled fixture case is run through the Windows-native corpus
  capture path
- **THEN** the reviewed row records case id, element family, capture id, frame
  range, request and response sizes, normalized hash, dynamic fields,
  operation token, response markers and replay or probe status when available
- **AND** raw capture payloads and process logs remain under ignored runtime
  paths

#### Scenario: Fixture capture cannot produce a row

- **WHEN** the fixture source, runner, live 1C runtime or provider support
  cannot produce reviewed wire evidence for a family
- **THEN** the compact evidence records `pending`, `partial`, `unsupported`,
  `timeout`, `rejected` or another explicit unresolved status with reason
- **AND** the row is not accepted from fixture plan or metadata evidence alone

### Requirement: Fixture probes remain read-only

The protocol lab SHALL keep fixture direct probes and replay confirmation
limited to read-only TestClient queries.

#### Scenario: Direct probe is run for a fixture family

- **WHEN** a direct Python-manager probe is used to confirm a fixture mapping
- **THEN** the probe evidence records query, family, expected response markers,
  status and evidence path
- **AND** the probe excludes clicks, command execution, text input, checkbox
  toggles, table edits and other write/action semantics
