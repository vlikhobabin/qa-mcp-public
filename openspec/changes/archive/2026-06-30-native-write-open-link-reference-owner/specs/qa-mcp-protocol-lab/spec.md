## ADDED Requirements

### Requirement: Open-link write scenarios set reference fields
The qa-mcp native write scenario path SHALL support an explicit reference field
step for an open-link managed form when the target field is addressed by visible
label and the requested value is a reference display value.

#### Scenario: Owner reference is selected on a create form
- **WHEN** a write scenario opens `e1cib/data/Справочник.ДоговорыКонтрагентов`
  and requests `Владелец=<Контрагент>`
- **THEN** qa-mcp targets the `Владелец` field as a reference field rather than
  plain text
- **AND** the step result records whether the field was targeted and whether
  the requested owner was selected

#### Scenario: Unsupported reference write fails closed
- **WHEN** qa-mcp cannot locate the reference field, open the chooser, find the
  requested value or disambiguate the selection
- **THEN** the reference step is reported as an error with a stable reason
- **AND** the scenario does not continue to a save command as if the owner had
  been set

### Requirement: Reference field evidence separates routing and selection
Live reference-write evidence SHALL distinguish field targeting, chooser
interaction and selected value verification.

#### Scenario: Reference evidence is retained
- **WHEN** live TestClient proof is run for an open-link reference write
- **THEN** retained evidence records the target nav-link, field label, requested
  reference value, selector result and active-form evidence
- **AND** raw screenshots, logs and local runtime details remain under ignored
  artifact paths unless a curated summary is explicitly selected for review
