## ADDED Requirements

### Requirement: Client fixture V1 exposes stable read-only control families
The protocol lab SHALL expose a broad, deterministic V1 control surface in the
client fixture processor for read-only TestClient protocol research.

#### Scenario: Fixture form exposes common control families
- **WHEN** the V1 fixture form is opened
- **THEN** read-only form inspection can identify markers for edit fields, checkboxes, choice or radio-style input, buttons, command bar, table, label, group and pages
- **AND** each target family has a unique `PF_*` marker

#### Scenario: Fixture values are deterministic
- **WHEN** the V1 fixture form initializes
- **THEN** string, number, date, checkbox, choice and table values are populated from local fixture state
- **AND** the values do not depend on current business documents, catalogs, registers or external services

#### Scenario: V1 controls are not accepted as actions
- **WHEN** V1 read-only evidence is reviewed
- **THEN** the existence of buttons, commands, checkboxes and pages does not by itself accept click, command, toggle, input or page-switch protocol mappings
- **AND** unsupported action semantics remain out of scope until later fixture versions
