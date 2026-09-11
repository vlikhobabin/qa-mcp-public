## ADDED Requirements

### Requirement: List-reading tools resolve the live dynamic-list table
`read_list_grid` and `read_list_column` SHALL resolve the table they read from the live form descriptor for the supplied `open_link` unless the caller supplies an explicit `table` argument. The tools SHALL include the resolved table name in the result and SHALL retarget the underlying list replay to that table instead of assuming `Список`.

#### Scenario: Single descriptor table is used
- **WHEN** `read_list_grid` or `read_list_column` is called for a list form whose descriptor contains exactly one `Table` element named `Валюты`
- **THEN** the tool reads table `Валюты`
- **AND** the result reports `table` as `Валюты`
- **AND** the tool does not report that table `Список` was read

#### Scenario: Explicit table overrides descriptor inference
- **WHEN** `read_list_grid` or `read_list_column` is called with `table="Валюты"`
- **THEN** the tool reads table `Валюты`
- **AND** the result reports `table` as `Валюты`
- **AND** the descriptor is used only to validate or diagnose that selection

#### Scenario: Legacy list table remains supported
- **WHEN** the descriptor identifies the target dynamic-list table as `Список`
- **THEN** `read_list_grid` and `read_list_column` continue to read table `Список`
- **AND** existing callers that omit `table` keep working

### Requirement: List-reading empty diagnostics are table-aware
`read_list_grid` and `read_list_column` SHALL distinguish table-resolution failures from a resolved table that is genuinely empty after refresh. The tools MUST NOT state that a list is genuinely empty when the descriptor table could not be resolved, was ambiguous, or did not match an explicit caller-supplied table.

#### Scenario: Table cannot be resolved
- **WHEN** a list-reading tool cannot resolve a table from the descriptor for the supplied `open_link`
- **THEN** the tool returns a structured diagnostic such as `list-table-unresolved`
- **AND** the diagnostic includes the available descriptor tables when known
- **AND** the reason does not claim that the list is genuinely empty

#### Scenario: Explicit table does not match descriptor
- **WHEN** a caller supplies `table="Список"` but the descriptor exposes only table `Валюты`
- **THEN** the tool returns a structured diagnostic such as `list-table-not-found`
- **AND** the result identifies the requested table and available descriptor tables
- **AND** the tool does not run the replay against the wrong table and then call zero rows empty

#### Scenario: Resolved table is empty after refresh
- **WHEN** the table is resolved successfully
- **AND** the refreshed list replay returns zero rows
- **THEN** the existing refreshed-empty diagnostic may state that the resolved list is genuinely empty
- **AND** the result identifies the table that was actually read
