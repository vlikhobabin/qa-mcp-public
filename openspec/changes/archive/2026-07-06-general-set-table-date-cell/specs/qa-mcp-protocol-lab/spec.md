## ADDED Requirements

### Requirement: A date grid cell is set without hardcoded coordinates
The protocol lab SHALL provide a general `set_table_date_cell(table, column,
date, …)` operation that sets a DATE value into a grid cell on a form by
LOCALIZING the cell and its calendar dropdown on screen — from descriptor bounds
or screenshot template-matching — rather than from coordinates hardcoded for one
fixture, then driving the already-shipped activate → calendar → mouse-click →
`Return` sequence.

#### Scenario: A date is set in a localized grid cell
- **WHEN** `set_table_date_cell(table, column, date)` is invoked on a form whose
  grid has a date column
- **THEN** the target cell and its calendar dropdown button are located on screen
  by descriptor bounds or template-match (no hardcoded fixture coordinates)
- **AND** the cell is protocol-activated, the calendar is opened, and the
  requested date is selected via the productized month/day click geometry
- **AND** after confirmation the grid cell holds the requested date, verified
  read-back (for example via `read_table_cell`)

#### Scenario: The cell cannot be localized on screen
- **WHEN** neither descriptor bounds nor template-matching can locate the cell or
  its calendar button with confidence
- **THEN** the operation returns an explicit `blocked`/`unsupported` result with
  the reason (no decodable bounds, low template-match score, off-screen/scrolled)
- **AND** the operation does NOT fall back to clicking hardcoded or guessed
  coordinates

### Requirement: General date-cell set is fixture-scoped and recoverable
The general `set_table_date_cell` operation SHALL be exercised only against test
fixtures and SHALL leave the form recoverable, retaining evidence of the
localization route and the live verification.

#### Scenario: The date-cell set is verified and evidenced on the fixture
- **WHEN** `set_table_date_cell` is live-verified
- **THEN** it runs against the test fixture date column (`PF_TABLE_DATE`) and the
  form is recoverable by re-opening it (no infobase mutation beyond the fixture
  cell)
- **AND** the retained evidence records the localization route used (descriptor
  bounds or template-match), the computed click coordinates, the requested date,
  and the read-back confirmation
