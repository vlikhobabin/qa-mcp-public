## ADDED Requirements

### Requirement: List-reading tools fail loud for uncertain zero-row results
`read_list_grid`, `read_list_column`, and `read_list_row` SHALL NOT return a
normal-looking empty result when display refresh, clean-state sweep, or
target-window confirmation failed before a zero-row or all-empty list result.
Such results MUST be marked with `ok: false` and
`data_confidence: "unknown"` while preserving the underlying structured error
and the original row/value payload for diagnostics.

#### Scenario: Refresh window lookup fails before a zero-row grid read
- **WHEN** `read_list_grid` resolves the form descriptor for an `open_link`
- **AND** the requested refresh fails with a structured `window-not-found`
  diagnostic
- **AND** the protocol grid replay returns `row_count: 0`
- **THEN** the top-level result includes `ok: false`
- **AND** the top-level result includes `data_confidence: "unknown"`
- **AND** the top-level result exposes the `window-not-found` diagnostic outside
  the nested `list_refresh` object
- **AND** callers can still inspect `row_count`, `rows`, `list_refresh`, and
  `table_resolution`.

#### Scenario: Refresh opt-out still fails loud when clean-state confirmation fails
- **WHEN** a list-reading tool is called with `refresh=false`
- **AND** the clean-state sweep or target-window confirmation fails
- **AND** the replay returns zero rows, no value, or an all-empty row
- **THEN** the result is marked `ok: false`
- **AND** the result uses `data_confidence: "unknown"` rather than presenting
  the zero as confirmed empty data.

#### Scenario: Confirmed refreshed empty list remains valid
- **WHEN** a list-reading tool successfully refreshes and confirms a clean
  state
- **AND** the replay returns zero rows from the resolved table
- **THEN** the result MAY report `row_count: 0` as confirmed empty
- **AND** the result MUST NOT be marked `ok: false` solely because the list is
  empty.

### Requirement: Remote-client list diagnostics include host window evidence
Remote-client list reads SHALL include a bounded diagnostic of the host-agent
window identity that was searched and the discovered Windows-side 1C windows
when they fail loud because zero-row data is uncertain and that authenticated
diagnostic route is available. If visible UI Automation cell text is available
from the host-agent, the result MUST include it as diagnostic fallback evidence;
if not, it MUST include the structured diagnostic failure.

#### Scenario: Remote zero-row failure lists discovered 1C windows
- **WHEN** `read_list_grid` fails loud in remote-client mode
- **AND** the host-agent `/window_list` route is reachable
- **THEN** the result includes the target window identity
- **AND** the result includes discovered `V8TopLevelFrame*` windows with handle,
  class, title, and PID.

#### Scenario: Visible UIA cells are attached as fallback evidence
- **WHEN** `read_list_grid` fails loud in remote-client mode
- **AND** the host-agent visible-cell diagnostic returns UI Automation cell text
- **THEN** the result includes a bounded visible-cell list
- **AND** callers can compare that diagnostic with the protocol `rows` before
  trusting the read.

#### Scenario: Diagnostic failures do not hide the original list failure
- **WHEN** a remote-client list read is already marked uncertain
- **AND** host window or visible-cell diagnostics fail
- **THEN** the result remains `ok: false`
- **AND** the diagnostic failure is recorded separately from the original
  refresh or sweep error.
