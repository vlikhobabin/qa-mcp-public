# 99. Capture-free last-mile — populated navigated-record value-read + general date-grid-cell

## Status
4.done

## Order Index
99

## Owner
unassigned

## OpenSpec Stage
implemented

## Result
DONE 2026-06-21. **Change 1 `read_record`** (populated navigated-record value-read) — decoded the e1cib `?ref=`
encoding (UUID groups g4·g5·g3·g2·g1) and shipped `read_record(record_type, ref)` (#51); live vs OData:
Товары/«Доставка» 12 attrs (Вид=Услуга, Родитель=Услуги, …), Контрагенты/«Покупатели». **Change 2
`set_table_date_cell`** (#52) — on-screen localization via ImageMagick `compare -subimage-search` (no new deps),
NO hardcoded coords; live fixture PF_TABLE_DATE → «15.08.2026»; **plus cross-year via the calendar year dropdown**
→ «15.08.2028» (2026→2028). 52 MCP tools, 351 offline tests green. The "(ideally) a 2nd form" stretch was scoped
up to **Path B (true config-agnostic table date-cell)** and carried to a dedicated follow-up card
`100-2026-06-21-config-agnostic-2nd-form-date-cell` (key risk retired; 4-blocker chain mapped; blocked on the
edt-mcp deploy reconnect). Evidence: `evidence/card99-{populated-record-valueread,set-table-date-cell,2ndform-pathB}-*`.

## Next
- follow-up card `100-2026-06-21-config-agnostic-2nd-form-date-cell` for Path B (after the edt-mcp deploy reconnect).

## Change Set
1. `populated-navigated-record-valueread` — `openspec/changes/populated-navigated-record-valueread/` (do first; tractable, unblocked)
2. `general-set-table-date-cell` — `openspec/changes/general-set-table-date-cell/` (look-ahead; new localization capability)

## Next
- run `$opsx-do openspec/board/2.todo/99-2026-06-20-navigated-record-read-and-date-cell.md` after reviewing artifacts (change 1 first)

## Source
- 2026-06-20: the two optional follow-ups recorded as out-of-scope at the close of epic 82 (cards 96/97/98 done).
  Both are LAST-MILE productization — the hard mechanism is already built + shipped; what remains is composition
  (change 1) or one new on-screen-localization capability (change 2). Neither was a blocker for the epic.
- Epic: 82 (closed, `4.done`). Detail of the gaps: card 82 Result + the evidence below.

## Summary
Close the two remaining productization gaps left open when epic 82 closed: (1) read VALUES off a POPULATED
navigated RECORD form (the mechanism reaches the form but was only verified against an empty create-form), and
(2) a GENERAL `set_table_date_cell` MCP tool (the protocol-activate + mouse-calendar mechanism + the date→click
geometry are shipped; a general tool needs on-screen cell localization). Both capture-free, no Vanessa. Change 1
is the tractable one (now unblocked by the card-98 dynlist reads); change 2 needs a new localization capability
(shared with any future click-by-coords tool) and is the look-ahead.

Capability: both extend `qa-mcp-protocol-lab` (read/introspection + table interaction surface).

## Change 1: `populated-navigated-record-valueread`
**Goal.** `read_form_descriptor(open_link=…)` (or a dedicated reader) returns the actual field VALUES of a
POPULATED catalog/document RECORD form opened by navigation — not just the field set.

**State (mechanism DONE, evidence `card98-navigated-record-valueread-2026-06-20`).** The navigated value-read
already REACHES a real record form on a 2nd config: `e1cib/data/Справочник.Валюты` (demo БСП) opens
`Валюта (создание)` and the value-read resolves per object-attribute field (`Код` / `Наименование` / …) against
the navigated form's `S.F`. Shipped gains: zero-group field enumeration (`extract_descriptor_fields` matches
`ManagedForm[F].EditField[name]` with no enclosing Group — record forms; columns still excluded) and a
newest-window open fallback in `_open_form_by_link`.

**Gap.** The verified form was a NEW/EMPTY create-form → fields carry no `e0 4b 53` «стал равен» envelope → 0
values (a correct read of an empty form, but no NON-EMPTY proof). `xdotool type` to populate failed because the
navigated form was not the focused OS window (the demo showed «Поиск по функциям»).

**Approach.** Open an EXISTING POPULATED record so the value-read reaches real values — now unblocked by the
card-98 dynlist reads (`read_list_row(where=…)` / `read_list_grid` give a row + ref):
- by record ref: navigate `e1cib/data/Справочник.X?ref=<guid>` (decode/confirm the ref nav-link form), OR
- by row-drill: `open_card` from a positioned list row → value-read the opened record form's fields.
Then value-read the populated record and assert each value vs OData. Largely COMPOSITION of existing tools
(`read_list_row` / `open_card` / `read_form_descriptor` value-read) + one live verify on a real populated record.

**Done when.** A populated catalog record (real config) is opened capture-free and ≥1 non-empty object-attribute
value is read back and matches OData; a unit/shape test + an evidence note.

**Risk/scope.** Small–medium; lab work = one cold boot + verify. Read-only (no mutation). Watch the cold-client
boundary (dynlist read materialisation) and the navigated-form `S.F` retarget (`_retarget_read_to_groups(
form_ref=…)`).

## Change 2: `general-set-table-date-cell` (look-ahead)
**Goal.** A general `set_table_date_cell(table, column, date, …)` MCP tool — set a DATE grid cell on ANY form,
no hardcoded coordinates.

**State (mechanism SOLVED + shipped, evidence `card97-date-gridcell-2026-06-19`).** The date grid cell IS
settable capture-free, live-verified end-to-end (`10.01.2026` → `15.08.2026`, committed): PROTOCOL-activate the
cell (replay `set_table_cell`'s `write_block`, activate+SET, WITHOUT the commit) → the inline date editor +
calendar dropdown button appear → MOUSE: click dropdown → click month → click day → `Return`. The date→click
geometry is productized + unit-tested (`calendar_month_cell` / `calendar_day_cell`, native_xtest.py). Keystrokes
are ruled out (1C's masked date editor ignores synthetic XTEST keys; protocol text-SET rejected) — mouse only.

**Gap.** A GENERAL tool needs the cell's ON-SCREEN location (calendar-button coords + calendar-popup origin),
which is layout/scroll/resolution-specific; the probe HARDCODES them for the fixture.

**Approach (localization — the one new capability).** Either:
- derive element BOUNDS from the form descriptor (if pixel bounds are decodable there) → compute the click
  coords; or
- screenshot template-matching to find the calendar dropdown button (recognizable icon).
This localization is SHARED with any future generic click-by-coords / cell-by-coords tool.

**Done when.** `set_table_date_cell` sets a date in a grid cell located WITHOUT hardcoded coords (descriptor
bounds or template-match), live-verified on the fixture date column + (ideally) a 2nd form; tests + evidence.

**Risk/scope.** Medium–high — the mechanism + date math are done; the localization is genuinely new. Needs an X
display (XTEST mouse), matchbox for layout, the fixture's `PF_TABLE_DATE` column.

## Notes / constraints
- Both are capture-free, no Vanessa. Change 1 is read-only; change 2 mutates form state (date cell) on the test
  fixture only (recovery = re-open form).
- Lab recipe: the cold-client boundary (one materialised dynlist read per fresh `launch_test_client`); matchbox
  for XTEST layout/focus; apache contention (stop for the native client). See [[genuine-action-capture-recipe]],
  [[vanessa-mcp-linux-genuine-manager]], [[linux-native-testclient-xvfb]].
- Do change 1 first (tractable, unblocked); change 2 when date-grid entry / click-by-coords is actually needed.

## Plan for the new session (start here)
1. Read the START-HERE memory `qa-mcp-capture-free-epic` + the handoff `capture-free-epic-session-handoff.md`
   (epic 82 closed; this card is the only active work).
2. `/opsx:ff openspec/board/2.todo/99-2026-06-20-navigated-record-read-and-date-cell.md` — generate the
   OpenSpec artifacts for change 1 (and change 2 as look-ahead).
3. `/opsx:do …` — implement change 1 (populated navigated-record value-read): compose `read_list_row`/`open_card`
   → value-read; live-verify a populated record vs OData; tests + evidence.
4. `/opsx:pub …` after change 1 (or after both).

## Related
- OpenSpec changes (apply-ready): `openspec/changes/populated-navigated-record-valueread/` (change 1),
  `openspec/changes/general-set-table-date-cell/` (change 2).
- Epic 82 (closed). Evidence: `evidence/card98-navigated-record-valueread-2026-06-20/` (change 1),
  `evidence/card97-date-gridcell-2026-06-19/` (change 2).
- Code: `src/qa_mcp/protocol/responses.py` (`extract_descriptor_fields`), `src/qa_mcp/mcp_server.py`
  (`_open_form_by_link`, `read_form_descriptor`, `read_list_row`/`open_card`),
  `src/qa_mcp/protocol/native_xtest.py` (`calendar_{month,day}_cell`).
- Probes: `navigated_record_valueread_probe.py`, `navigated_nonempty_valueread_probe.py`,
  `date_cell_calendar_probe.py`.

## Log
- 2026-06-20 card created — captures the two optional follow-ups left open at epic-82 close (populated
  navigated-record value-read = change 1, tractable/unblocked; general set_table_date_cell = change 2,
  look-ahead). Not yet ff-processed; implementation deferred to a new session per request.
- 2026-06-20 `$opsx-ff` — decomposed into two apply-ready OpenSpec changes (slugs preserved from the card):
  `populated-navigated-record-valueread` and `general-set-table-date-cell`, each extending the
  `qa-mcp-protocol-lab` capability with proposal/specs/design/tasks + a 1C Verification Matrix.
  `openspec validate --all` → 3 passed/0 failed; `git diff --check` clean. Stage → artifacts. Next: `$opsx-do`.
- 2026-06-20 change 1 ✅ DONE+productized — decoded the e1cib `?ref=` encoding (UUID groups g4·g5·g3·g2·g1)
  from the genuine open-card capture; shipped `read_record(record_type, ref)` (#51) + `navigation.e1cib_ref_hex`
  / `e1cib_data_link` + `_normalize_data_ref_link`. Live vs OData: Товары/«Доставка» 12 attrs (Вид=Услуга,
  Родитель=Услуги, …), Контрагенты/«Покупатели». Cold-client boundary documented. Evidence
  `evidence/card99-populated-record-valueread-2026-06-20/`.
- 2026-06-20 change 2 ✅ DONE — on-screen localization via ImageMagick `compare -subimage-search`
  (`native_xtest.locate_calendar_button` + glyph asset `protocol/assets/calendar_button.png`, no new deps);
  shipped `set_table_date_cell(date, column)` (#52) — activate → localize → mouse-pick → Return, NO hardcoded
  coords. Live-verified on fixture PF_TABLE_DATE → «15.08.2026» (screenshot proof). Evidence
  `evidence/card99-set-table-date-cell-2026-06-20/`.
- 2026-06-20 change 2 YEAR-NAV ✅ DONE — decoded the calendar year controls (‹/› step MONTH; year via the
  «<year> ▼» dropdown, current at top + current+k below; type-ahead rejected). `set_table_date_cell` now navigates
  forward to a different year (current = `from_year` or today; dropdown row-click chained ≤3/open;
  `calendar_year_row` geometry, unit-tested). Live cross-year: «15.08.2028» (2026→2028, offset +2). Backward years
  return `status=blocked` (forward-only dropdown — residual). 52 tools, 351 tests. Both changes uncommitted on
  `main` — ready for `$opsx-pub`. REMAINING card-99 residual: 2nd-form generality (date-cell on a non-fixture form).
