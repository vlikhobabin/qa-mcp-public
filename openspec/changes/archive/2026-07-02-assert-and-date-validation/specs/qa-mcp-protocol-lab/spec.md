## ADDED Requirements

### Requirement: Data-layer match modes fail closed
The OData data assertion comparator SHALL reject unsupported match modes instead of treating them as equality, and SHALL
support numeric comparison for decimal values that differ only by locale decimal separator or insignificant trailing
zeros.

#### Scenario: Unknown match mode raises
- **WHEN** `match_value(actual, expected, mode="__bogus__")` is called
- **THEN** it raises `ValueError` naming the unsupported mode
- **AND** no equality fallback result is returned.

#### Scenario: Numeric mode compares decimal values
- **WHEN** `match_value("120,50", "120.5", mode="numeric")` is called
- **THEN** the comparison succeeds numerically.

### Requirement: Table date-cell input validates before UI interaction
The table date-cell writer SHALL validate a requested `DD.MM.YYYY` value with calendar range checks before activating
the table cell, locating the calendar button or clicking calendar coordinates.

#### Scenario: Invalid date blocks before activation
- **WHEN** `set_table_date_cell` is requested with `date="99.99.2026"`
- **THEN** the result reports `status: "blocked"` and `reason: "invalid_date"`
- **AND** no calendar activation, screenshot localization or mouse click is attempted.

#### Scenario: Valid date still reaches the picker
- **WHEN** `set_table_date_cell` is requested with a valid date such as `05.03.2026`
- **THEN** the validated day, month and year are passed to the calendar picker.

### Requirement: Calendar blocked paths do not open unreachable year dropdowns
The calendar picker SHALL evaluate unsupported backward-year navigation before opening the calendar dropdown, so a
blocked backward-year result does not leave an additional popup open.

#### Scenario: Backward year is blocked before dropdown click
- **WHEN** a table date-cell pick targets a year before the current calendar year
- **THEN** the result is `blocked`
- **AND** no dropdown-opening click is issued for the unsupported year selection.
