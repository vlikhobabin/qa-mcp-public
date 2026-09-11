## Why

The date grid-cell write mechanism (card 97) is SOLVED and live-verified
end-to-end (`10.01.2026` → `15.08.2026`): protocol-activate the cell (replay
`set_table_cell`'s write_block, activate+SET, WITHOUT the commit) → the inline
date editor + calendar dropdown appear → mouse-click dropdown → month → day →
`Return`. The date→click geometry (`calendar_month_cell` / `calendar_day_cell`)
is productized and unit-tested. The one thing keeping it from being a GENERAL
`set_table_date_cell(table, column, date)` tool is on-screen LOCALIZATION: the
probe HARDCODES the calendar-button coords and calendar-popup origin for the
fixture. A general localization capability (derive bounds from the descriptor or
template-match the calendar button) is shared with any future click-by-coords /
cell-by-coords tool, so it is worth building once.

## What Changes

- Add a GENERAL `set_table_date_cell(table, column, date, …)` MCP tool that sets
  a DATE grid cell on ANY form with NO hardcoded coordinates.
- Add an on-screen cell/button LOCALIZATION capability, either by deriving
  element BOUNDS from the form descriptor (if pixel bounds are decodable there)
  or by screenshot template-matching the calendar dropdown button icon.
- Reuse the shipped activate+calendar mechanism and date→click geometry
  (`calendar_month_cell` / `calendar_day_cell`, `native_xtest.py`) unchanged.
- Live-verify on the fixture date column (`PF_TABLE_DATE`) and, ideally, a 2nd
  form, with the click coords coming from localization (not hardcoded).
- This change touches Python manager code + protocol/XTEST tooling; it mutates
  form state (a date cell) on the TEST FIXTURE only (recovery = re-open form).
- It requires a live X display (XTEST mouse), matchbox for layout/focus, and the
  fixture's date column. No Vanessa, no EDT/meta.

## Capabilities

### New Capabilities
<!-- none — this extends the existing protocol-lab capability -->

### Modified Capabilities
- `qa-mcp-protocol-lab`: A general `set_table_date_cell` tool sets a date grid
  cell on any form by LOCALIZING the cell/calendar-button on screen (descriptor
  bounds or template-match) instead of hardcoded coordinates, then driving the
  already-shipped activate→calendar→mouse-click sequence.

## Impact

- Python manager: a new `set_table_date_cell` MCP tool in `src/qa_mcp/mcp_server.py`;
  localization helper(s) in `src/qa_mcp/protocol/` (descriptor-bounds decode in
  `responses.py` and/or a template-match helper); reuse
  `src/qa_mcp/protocol/native_xtest.py` (`calendar_{month,day}_cell`).
- Tests: localization unit test (bounds decode or template-match shape) + the
  date→click geometry tests already present.
- Evidence: `.artifacts/openspec/general-set-table-date-cell/<run-id>/` plus the
  existing `evidence/card97-date-gridcell-2026-06-19/`.
- Runtime: live X display (XTEST), matchbox, fixture `PF_TABLE_DATE` column.
  Mutates the fixture date cell only; recovery = re-open the form.
