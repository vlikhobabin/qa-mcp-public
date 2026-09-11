## ADDED Requirements

### Requirement: Controlled read-only fixture plans cover missing element families

The protocol lab SHALL maintain a controlled fixture coverage plan before
promoting new read-only element-family mappings for `Button`, `Table`,
`CommandBar`, `Page`, `Label` or `CheckBox`.

#### Scenario: Missing family is planned for coverage

- **WHEN** a missing read-only element family is selected for fixture coverage
- **THEN** the fixture plan records the family, case id, target form or
  fixture source, expected state, expected response markers, safety class,
  planned evidence paths and provider owner
- **AND** any generated EDT workspace, infobase export, raw fixture output or
  raw capture remains outside reviewed git changes

#### Scenario: Missing family cannot be covered yet

- **WHEN** a missing read-only element family cannot be safely represented in
  the current lab fixture
- **THEN** the fixture plan records the family as blocked or out of scope with
  a reason, owner route and residual risk
- **AND** the corpus matrix keeps the family visible as unsupported or pending
  until compact capture and replay/probe evidence exists

### Requirement: Fixture-derived corpus cases remain read-only and evidence-backed

The protocol lab SHALL feed controlled fixture surfaces into corpus capture
through explicit read-only case definitions and SHALL require compact wire
evidence plus replay or direct Python-manager proof before fixture-derived
rows become accepted mappings.

#### Scenario: Fixture case is added to the corpus

- **WHEN** a controlled fixture surface is added to a corpus manifest or seeded
  matrix
- **THEN** the case definition records the read-only API call, element family,
  UI target, expected state, expected response markers and safety class
- **AND** the case excludes clicks, text input, command execution, navigation
  with business-data mutation and other write/action semantics

#### Scenario: Fixture-derived mapping is promoted

- **WHEN** a fixture-derived corpus row is considered for accepted mapping
- **THEN** the reviewed evidence records capture id, frame range, normalized
  hash, dynamic fields, operation token, response markers and replay or direct
  Python-manager status
- **AND** help, metadata or EDT labels remain semantic support rather than
  proof of native protocol behavior
