## ADDED Requirements

### Requirement: Create scenarios require persistence verification for save claims
The qa-mcp open-link create scenario path SHALL report a persisted-record claim
as accepted only when a read-back, list-read or data assertion verifies the
created record state.

#### Scenario: Saved contract is verified by data assertion
- **WHEN** a create scenario saves a `ДоговорыКонтрагентов` record
- **THEN** qa-mcp records a persistence verification summary containing the
  identifying fields, observed `Наименование`, observed `Основной` and
  assertion status
- **AND** a missing or failed assertion keeps the scenario from reporting the
  persistence claim as passed

#### Scenario: Provider gap remains explicit
- **WHEN** no read-back, list-read or live-data route is available for the saved
  record
- **THEN** qa-mcp reports a provider-gap or verification error with owner route
  and expected evidence type
- **AND** the scenario does not silently accept the save as verified

### Requirement: Mutation proof requires cleanup evidence
The qa-mcp create/write flow SHALL require cleanup evidence or explicit
unresolved-leftover diagnostics before accepting live mutation proof.

#### Scenario: Cleanup proof is retained after create
- **WHEN** a live create proof saves one or more demo records
- **THEN** retained evidence records created object identifiers, cleanup action,
  final-state check and unresolved leftovers
- **AND** cleanup artifacts remain under ignored runtime or artifact paths unless
  a curated summary is selected for review

#### Scenario: Missing cleanup blocks acceptance
- **WHEN** a save proof has no cleanup route and no explicit residual-risk
  record
- **THEN** qa-mcp reports the cleanup evidence as missing
- **AND** the mutation proof is not archive-ready
