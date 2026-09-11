## Archive Note (2026-07-06)

Archived during board hygiene as historical/superseded planning. The active
delivery is represented by done board card
`openspec/board/4.done/100-2026-06-21-config-agnostic-2nd-form-date-cell.md`;
the unchecked checklist below is retained as the original plan, not as active
OpenSpec work.

## 1. On-screen localization capability

- [ ] 1.1 Probe whether the form descriptor carries decodable pixel BOUNDS for a
  grid column/cell (extend `extract_descriptor_*` in
  `src/qa_mcp/protocol/responses.py`); record the finding.
- [ ] 1.2 If bounds are not decodable, build a screenshot template-match helper
  that locates the calendar dropdown button glyph on screen and returns its
  origin + a confidence score.
- [ ] 1.3 Return an explicit `blocked`/`unsupported` result (with reason) when
  neither route localizes the cell above a confidence threshold — never click
  guessed coordinates.

## 2. General `set_table_date_cell` tool

- [ ] 2.1 Add `set_table_date_cell(table, column, date, …)` to
  `src/qa_mcp/mcp_server.py` that localizes the cell/calendar button, then drives
  the shipped activate → calendar-open → `calendar_{month,day}_cell` → `Return`
  sequence (`src/qa_mcp/protocol/native_xtest.py`).
- [ ] 2.2 Reuse the date→click geometry unchanged; compute the click point from
  the localized origin, not hardcoded fixture coords.

## 3. Live verification

- [ ] 3.1 Live-verify on the fixture date column (`PF_TABLE_DATE`) with localized
  coordinates: set a date, then read it back (`read_table_cell`) to confirm
  (X display + matchbox + apache stopped per the lab recipe).
- [ ] 3.2 Ideally repeat on a 2nd date-grid form to prove generality; if only the
  fixture is available, record the residual risk.

## 4. Tests + evidence

- [ ] 4.1 Add a localization unit test (bounds-decode shape or template-match
  score), plus keep the date→click geometry tests
  (`calendar_{month,day}_cell`).
- [ ] 4.2 Retain evidence under
  `.artifacts/openspec/general-set-table-date-cell/<run-id>/` recording the
  localization route, computed click coords, requested date and read-back
  confirmation; cross-link `evidence/card97-date-gridcell-2026-06-19/`.

## 5. Verification

- [ ] 5.1 Run the change's unit tests green.
- [ ] 5.2 Run `openspec validate general-set-table-date-cell --strict`.
- [ ] 5.3 Run `git diff --check -- openspec/changes/general-set-table-date-cell openspec/board`.

## 6. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| On-screen localization | Calendar dropdown button + cell origin from descriptor bounds or template-match | Decision: descriptor bounds decodable vs template-match fallback; confidence threshold | Localization transcript: route used, computed origin, match score | `.artifacts/openspec/general-set-table-date-cell/<run-id>/localization/` | required | `project:qa-mcp` | N/A | High: descriptors may carry no pixel bounds; template-match is theme/DPI/scroll sensitive |
| Managed form (grid date cell) write | Fixture date grid cell (`PF_TABLE_DATE`) set via activate→calendar→mouse-click | `set_table_date_cell` invocation + localized click coords | Live set + `read_table_cell` read-back confirming the date; before/after evidence | `.artifacts/openspec/general-set-table-date-cell/<run-id>/date-set/` | required | `project:qa-mcp` | N/A | Medium: mutates the fixture cell (recovery = re-open form); layout can shift between activate and click |
| XTEST / mouse geometry | `calendar_{month,day}_cell` date→click math reused unchanged | Unit test of the date→click geometry + localization shape | Offline unit tests green | `tests/` (localization + calendar geometry) | required | `project:qa-mcp` | N/A | Low: date math already productized and unit-tested |
| Generality (2nd form) | A second date-grid form, if available in the lab | 2nd-form verification or explicit residual-risk note | 2nd-form set+read-back, or a recorded residual-risk statement | `.artifacts/openspec/general-set-table-date-cell/<run-id>/second-form/` | optional | `project:qa-mcp` | Only if no 2nd date-grid form exists in the lab | Medium: generality unproven if only the fixture is available |
| Live infobase / posting | None — only a form date cell is written, no posting/register movement | N/A | N/A | N/A | N/A | `project:qa-mcp` | The change writes a form date cell on the fixture; no document posting or register movement | Low: no posting path exercised |
| Vanessa UI evidence | None — capture-free, no Vanessa | N/A | N/A | N/A | N/A | `project:qa-mcp` | The mechanism is native-protocol + XTEST; Vanessa is explicitly out of scope | Low: native mechanism already shipped |
