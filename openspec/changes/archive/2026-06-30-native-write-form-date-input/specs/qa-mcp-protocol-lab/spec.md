## ADDED Requirements

### Requirement: Native write tools can set form-level date fields
The qa-mcp native write path SHALL provide a form-level date field operation for managed form `EditField` date attributes, separate from table date-cell calendar operations.

#### Scenario: Form-level date write succeeds
- **WHEN** a caller requests a `DD.MM.YYYY` value for a form-level date field on an opened or open-link form
- **THEN** qa-mcp validates the date format before live input
- **AND** the result reports `surface=form_field_date`, the target field, the requested date and the read-back or verification status

#### Scenario: Grid date-cell path remains separate
- **WHEN** a caller uses `set_table_date_cell`
- **THEN** qa-mcp continues to treat the target as a tabular date cell
- **AND** form-level date-field handling does not change the table-cell calendar result contract

### Requirement: Date write evidence identifies formatting behavior
Form-level date write evidence SHALL record the requested date and the observed read-back formatting so date-prefix acceptance, time suffixes or provider gaps are reviewable.

#### Scenario: Date read-back has a time suffix
- **WHEN** a date field read-back includes a time component after the requested date
- **THEN** qa-mcp may accept the write by date prefix
- **AND** the retained evidence records the full read-back string and the prefix comparison
