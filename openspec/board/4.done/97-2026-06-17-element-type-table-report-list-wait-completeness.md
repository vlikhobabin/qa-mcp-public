# 97. Element-type & table/report/list completeness — the remaining action surface

## Status
4.done

## Order Index
97

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-17 (board triage): consolidates the remaining lower-frequency action coverage into one story with a
  5-item change set. Folds the table-ops/report/dynamic-list portion of card 95 (§E5), the residue of card 88
  (element-type coverage — number/date/checkbox/choice/table-cell already SHIPPED by card 90), and the one
  deferred read_only item from card 72 (App.WaitForCondition). Sources in `5.canceled` / `4.done`.
- Epic: card 82. Detail: `capture-free-epic-next-roadmap.md` §E5; `capture-free-epic-state.md` §8 (deferred).

## Summary
Round out the native read+act surface across the element/interaction types real configs use but that aren't
yet productized, on top of the shipped per-type writes (string / number / date / checkbox / choice /
table-cell). Each item is an independent capture→decode→productize cycle, pulled as a real scenario demands it.

## Changes (5)
1. **Table row operations — delete / move up-down / copy / multi-select** (was card 95). ✅ **DONE 2026-06-19.**
   - delete/move/copy: `delete_table_row` / `move_table_row(up|down)` / `copy_table_row` (MCP #28–#30),
     capture-free, live-verified via the new `PF_TABLE_SNAPSHOT` read-back. Each is the `…Button[<CMD>]` command
     invoke (tail `88 82 81 20 20 20`) replayed from ONE genuine `PF_COPY_ROW` capture + Button-leaf retarget.
     Detail: `docs/protocol-research/evidence/card97-rowops-2026-06-19/findings.md`.
   - **multi-row select:** DECODED + command productized. "Select all rows" is a protocol TABLE-command
     (`Table[PF_TABLE_ITEMS] 88 82 81 20 20 20`, not OS) → `select_all_table_rows` (MCP #31). ⚠️ Read-back
     BOUNDARY (honest): the multi-selection is transient table-focus state — a separate focus-changing command
     collapses it to the active row (genuine == replay: both read `PF_SEL[1]`), so a live multi-selection isn't
     capture-free-readable across commands; composing select-then-act needs the whole flow in ONE captured
     session. Detail: `docs/protocol-research/evidence/card97-multiselect-2026-06-19/findings.md`.
   - Fixture extended (row-op + select commands + `PF_TABLE_SNAPSHOT` / `PF_SELECTED_ROWS` markers), deployed.
2. **Number / date cells in the grid** (was card 95). ✅ **NUMBER cell SOLVED 2026-06-19** (no new code): the
   genuine PF_TABLE_NUMBER SET is BYTE-IDENTICAL to the string cell (`e0 41 81 81 ba <len> <ascii>`, value as
   text) — the card's "different per-type buffer" assumption is DISPROVEN for grid cells (it holds only for
   plain FIELDS, card 86c). `set_table_cell(value, column="PF_TABLE_NUMBER")` just works (live-proven readback
   "999"). ✅ **DATE cell SOLVED 2026-06-19** (protocol-activate + pure-MOUSE calendar pick; live-verified row 1
   `10.01.2026 9:00:00`→`15.08.2026 0:00:00`, committed). The protocol text-SET is RULED OUT (committed=False
   even at fitting width; the numdate «Неподходящий тип» was Vanessa's step pre-check, not 1C) and synthetic
   keystrokes do NOT reach 1C's masked date editor in any focus state (decisive control: the same `xdotool type`
   DID land in a plain PF_EDIT_STRING field). Working path: PROTOCOL replay the `set_table_cell` write_block
   (activate, NOT the commit) → the inline date editor + calendar dropdown button appear → MOUSE click the month
   (`calendar_month_cell`) + the day (`calendar_day_cell`, day-of-week→6-week-grid math) → `Return` commits.
   Productized the date→click geometry in `native_xtest.py` (+5 tests); a general `set_table_date_cell` MCP tool
   still needs on-screen cell localization → card 98 follow-up. Detail:
   `docs/protocol-research/evidence/card97-date-gridcell-2026-06-19/findings.md` (+ `card97-numdate-2026-06-19`).
3. **Reports / print / spreadsheet document (ТабличныйДокумент)** (was card 95). ✅ **report-RUN DONE
   2026-06-19** — `run_report` (MCP #37) fires the PF_RUN_REPORT command (the `click_command` family), filling
   the form's SpreadsheetDocument attribute server-side, capture-free, live-verified (PF_LAST_ACTION="PF_RUN_REPORT"
   reads back). ✅ **spreadsheet CELL-read DONE** — `read_spreadsheet_cell(address)` (MCP #38), live-verified
   PASS 4/4 (R1C1→PF_RPT_R1C1 … R2C2→PF_RPT_R2C2). The earlier "binary .mxl boundary" was a RED HERRING (that
   blob is the form-RENDER path); a cell is read by an IN-CLIENT 1C method — the genuine «перейти к ячейке
   <addr>» navigate (`EditField[PF_REPORT] 88 82 81 fa <len><addr>`) + the client's value echo
   (`9a <len><value>` = the card-79 value-read shape) — so reading cells is capture-free with NO .mxl decode
   (replay navigate-to-cell + retarget the address + parse the value; the whole exchange is 6.5 KB vs 290 KB for
   a full form read). Fixture extended (PF_REPORT SpreadsheetDocument + PF_RUN_REPORT, deployed gen `38bc7fac8858…`).
   ⇒ **change 3 FUNCTIONALLY COMPLETE** (report-run + cell-read). Detail:
   `docs/protocol-research/evidence/card97-report-2026-06-19/findings.md`.
4. **Dynamic-list operations — filter / search-string / period / grouping** (was card 95) on
   `ДенамическийСписокИерархия`. ✅ **FUNCTIONALLY COMPLETE 2026-06-19** (search-string + view-mode/grouping +
   filter shipped; period N/A on the catalog dynlist).
   - **search-string ✅ DONE 2026-06-19:** `search_list(value, …)` (MCP #34) filters a dynlist by its search
     box, capture-free, live-verified by screenshot ("Молоко"→1 matching row, "Творог"→0 rows; the box shows
     the re-targeted value). DECODE: a dynlist search SET is the **UTF-16 `b7` value buffer**
     (`e0 41 81 81 b7 <char-count><utf-16le><space pad>`) — the SAME buffer as a CatalogRef name SET — addressed
     at the `SearchStringAddition` element; so it reuses the `set_reference_field` full-replay + `retarget_ref_value`
     machinery. ⚠️ FIXTURE deploy needed first: the dynlist command bar was `commandBarLocation=None` (search box
     invisible → the Vanessa search step failed «Невидимый пользователю элемент управления»); 1-line edit
     `None`→`Top` surfaces it (+ the «Ещё» menu = view-mode / filter) — deployed gen `5569447f…`→`08d5aabf7575…`.
     Detail: `docs/protocol-research/evidence/card97-dynlist-search-2026-06-19/findings.md`.
   - **view-mode / grouping ✅ DONE 2026-06-19:** `set_list_view(mode)` (MCP #35) toggles Список / Дерево /
     Иерархический, capture-free, **3-way screenshot-verified** (flat list / collapsed tree / expanded hierarchy
     of the SAME Товары list). DECODE: «Режим просмотра» entries are standard FORM BUTTONS
     (`<dynlist>Список`/`…Дерево`/`…ИерархическийСписок`); a click is the `…Button[<name>] 88 82 81 20 20 20`
     command family (IDENTICAL to the row ops / close-window), but the Button name is **Cyrillic → UTF-16LE
     element path**. Productize **generalized `click_command` to UTF-16** (`_find_element_command` encoding-
     agnostic + `retarget_element_leaf_any` ASCII-or-UTF-16-same-length) — a bonus that lifts the command-click
     machinery onto real Cyrillic-named configs (advances the card-98 "2nd config" goal). Detail:
     `docs/protocol-research/evidence/card97-dynlist-viewmode-2026-06-19/findings.md`.
   - **filter ✅ DONE 2026-06-19:** `advanced_search(value)` (MCP #36) filters a dynlist via the «Расширенный
     поиск» DIALOG (`UniversalListFindExtForm`), capture-free, live-verified by screenshot (an active filter chip
     «Код: Молоко» on the list). This proves the reusable **"drive a modal dialog"** pattern: open the form →
     click «Расширенный поиск» (opens a NEW window) → SET its `Pattern` field (UTF-16 `b7` buffer) → click `Find`
     — a whole-stream replay with GuidRebinder rebinding the dialog window + retarget_ref_value on the Pattern
     (the same machinery as set_reference_field/answer_dialog). Default field = «Код» (FieldSelector at default;
     field-targeting is a refinement). Detail: `docs/protocol-research/evidence/card97-dynlist-advsearch-2026-06-19/findings.md`.
   - **period:** N/A on this fixture — the dynlist is on Catalog.Товары (NO period dimension), so the `…Интервал`
     «Период данных» command exists but has no effect; demonstrating period meaningfully needs a periodic-source
     dynlist (document journal / info register — a fixture extension). The proven modal-dialog pattern is ready
     to drive the period dialog once such a source exists. **⇒ Change 4 is functionally COMPLETE** (search-string
     + view-mode/grouping + filter; period N/A on a catalog).
5. **Waits + assertions — `WaitForCondition` + assert element value/state** (was card 88 + the one deferred
   card-72 read_only item). ✅ **SHIPPED 2026-06-19:** `assert_form_value(field, expected, equals|contains|regex)`
   + `wait_for_form_value(…, timeout_sec, interval_sec)` (MCP #32/#33), live-verified. Fixed a real value-read
   parser bug (the value is LEB128-length-prefixed, not 0x14-delimited → only PF_EDIT_STRING parsed before).
   Read SCOPE — both follow-ups now ✅ **DONE 2026-06-19**: (a) **cross-region read** — the value-read query
   carries the FULL element path; a `groups` full-path retarget (`_retarget_read_to_groups`) reads PF_GROUP_MAIN
   status markers capture-free (live: PF_LAST_ACTION→"PF_STATE_INITIAL"); (b) **number/date value PARSER** — the
   premise was stale: number AND date already decode as formatted display text (genuine-capture verified); fixed
   a latent descriptor-echo parser bug + added a `numeric` assert mode. The only read-side remainder is AUTOMATIC
   `groups` discovery (→ card 98). Detail: `docs/protocol-research/evidence/card97-waits-asserts-2026-06-19/`,
   `card97-crossregion-read-2026-06-19/`, `card97-numdate-parser-2026-06-19/`.

## Notes / constraints
- Most of card 88's original scope (number/date/checkbox/choice/table-cell, read+act+read-back) is ALREADY
  DONE via card 90 — this card carries only the residue (waits/asserts + the long-tail ops above).
- Variable-length and field-declared-length limits are already respected by the card-80 retarget machinery.
- Each sub-item is independent; split into 97a/97b/… if several are scheduled at once.

## Plan for the new session (start here)
Read `capture-free-epic-next-roadmap.md` §E5 + `capture-free-epic-state.md` §6 (the loop) / §8 (deferred).
Pull the specific sub-item a real scenario needs; table-ops and asserts are the most commonly requested.

## Merged from (audit trail)
- card 95 (table-ops / number-date cells / reports / dynamic-list portion) → changes 1–4 (its
  keyboard/messages portion → card 96)
- card 88 (element-type coverage residue) → change 5
- card 72 (deferred App.WaitForCondition; the rest of read_only is DONE in 4.done) → change 5

## Related
- Epic 82. Shipped: cards 80/86/90 (per-type writes, table-cell). `src/qa_mcp/protocol/native_write.py`,
  `src/qa_mcp/scenario/actions.py`.

## Log
- 2026-06-17 card created by board triage — consolidates the 95 remainder + 88 residue + 72 deferred (5 changes).
- 2026-06-19 change 1 (table row ops) SHIPPED capture-free except multi-select: `delete_table_row` /
  `move_table_row` / `copy_table_row` (MCP #28–#30, 30 tools / 241 tests), fixture extended with the row-op
  commands + `PF_TABLE_SNAPSHOT` read-back (deployed, gen b5802e…), live-verified by screenshot. Card moved to
  3.inprogress. Evidence: `docs/protocol-research/evidence/card97-rowops-2026-06-19/findings.md`.
- 2026-06-19 change 1 (multi-row select) DONE → change 1 COMPLETE. "Select all rows" decoded as a protocol
  TABLE-command (`Table[PF_TABLE_ITEMS] 88 82 81`, not OS); productized `select_all_table_rows` (MCP #31, 31
  tools / 242 tests); fixture gained `PF_SELECTED_ROWS` + `PF_REFRESH_SELECTION` (gen c94ebf…). Documented the
  honest read-back boundary (transient table-focus selection collapses on a separate focus-changing command —
  genuine == replay). Evidence: `docs/protocol-research/evidence/card97-multiselect-2026-06-19/findings.md`.
  Remaining on card 97: changes 2–5 (number/date cells, reports/ТабличныйДокумент, dynamic-list, waits/asserts).
- 2026-06-19 change 5 (waits + asserts) SHIPPED: `assert_form_value` / `wait_for_form_value` (MCP #32/#33, 33
  tools / 251 tests), built on the card-79 value-read; fixed the value-read LEB128 length parser (was 0x14-
  delimited → only PF_EDIT_STRING parsed). Honest read scope = value-read region (editable PF_EDIT_* strings);
  cross-region markers + number/date parsing are read-decode follow-ups. Evidence:
  `docs/protocol-research/evidence/card97-waits-asserts-2026-06-19/findings.md`. Remaining on card 97: changes
  2 (number/date cells — NEXT), 3 (reports), 4 (dynamic-list).
- 2026-06-19 change 2 (grid cells): NUMBER cell SOLVED (no new code — number SET = string SET buffer, card
  assumption disproven; set_table_cell(column="PF_TABLE_NUMBER") live-proven readback "999"). DATE cell:
  fixture gained PF_TABLE_DATE (gen 5569447…) but text-input is rejected by the date control + Vanessa's date
  step is calendar-field-only → date grid-cell entry deferred (calendar pick / OS-level follow-up). Evidence:
  `docs/protocol-research/evidence/card97-numdate-2026-06-19/findings.md`. Card 97 remaining: change 2 date
  cell (deferred), change 3 (reports/ТабличныйДокумент), change 4 (dynamic-list).
- 2026-06-19 change 4 (dynamic-list) STARTED — **search-string SHIPPED:** `search_list` (MCP #34, 34 tools /
  254 tests), capture-free, live-verified by screenshot (dynlist filtered "Молоко"→1 row / "Творог"→0 rows).
  DECODE: the dynlist search SET is the UTF-16 `b7` value buffer (same as a CatalogRef name SET) addressed at
  the `SearchStringAddition` element → reuses `set_reference_field` full-replay + `retarget_ref_value`. Required
  a 1-line fixture deploy (dynlist `commandBarLocation` None→Top — the search box / «Ещё» menu were invisible;
  gen `5569447f…`→`08d5aabf7575…`). Evidence: `docs/protocol-research/evidence/card97-dynlist-search-2026-06-19/
  findings.md`. Remaining on card 97: change 4 filter/period/grouping, change 3 (reports), change 2 date cell.
- 2026-06-19 change 4 (dynamic-list) CONTINUED — **view-mode / grouping SHIPPED:** `set_list_view` (MCP #35, 35
  tools / 258 tests), capture-free, 3-way screenshot-verified (Список flat / Дерево collapsed-tree /
  Иерархический expanded-hierarchy). DECODE: «Режим просмотра» = standard FORM BUTTONS; a click is the
  `…Button[<name>] 88 82 81 20 20 20` family (same as row ops), but the Button name is Cyrillic → UTF-16LE path.
  Productize generalized `click_command` to UTF-16 (`_find_element_command` encoding-agnostic +
  `retarget_element_leaf_any`) — also lifts the command-click machinery onto real Cyrillic configs. Evidence:
  `docs/protocol-research/evidence/card97-dynlist-viewmode-2026-06-19/findings.md`. Remaining on card 97: change
  4 filter (`…НастройкаСписка` dialog) / period (`…Интервал` dialog), change 3 (reports), change 2 date cell.
- 2026-06-19 change 4 FUNCTIONALLY COMPLETE — **filter SHIPPED:** `advanced_search` (MCP #36, 36 tools / 259
  tests) filters a dynlist via the «Расширенный поиск» DIALOG, capture-free, live-verified (filter chip «Код:
  Молоко»). Proves the reusable "drive a modal dialog" replay (open new window → SET a field → click confirm),
  reusing the set_reference_field/answer_dialog full-replay + GuidRebinder + retarget_ref_value. Period N/A on the
  Catalog.Товары dynlist (no period dimension). Change 4 done = search-string + view-mode + filter (period N/A).
  Evidence: `docs/protocol-research/evidence/card97-dynlist-advsearch-2026-06-19/findings.md`. Card 97 remaining:
  change 3 (reports/ТабличныйДокумент — needs a fixture ТабличныйДокумент), change 2 date grid cell (deferred).
- 2026-06-19 change 3 (reports) — **report-RUN SHIPPED:** `run_report` (MCP #37, 37 tools / 259 tests) fires
  PF_RUN_REPORT (click_command family), filling the form's SpreadsheetDocument server-side, capture-free,
  live-verified (PF_LAST_ACTION="PF_RUN_REPORT"). Fixture extended (PF_REPORT SpreadsheetDocument + PF_RUN_REPORT
  command/button/handler; deployed gen `08d5aabf…`→`38bc7fac8858…` — a transient EDT-export glitch needed a retry).
  ⚠️ spreadsheet CELL-read = honest boundary: the ТабличныйДокумент content is a 1C-packed BINARY .mxl blob on the
  wire (cell text absent in UTF-16/UTF-8, not zlib/deflate) → reading cells capture-free is a deep .mxl decode
  (deferred; in-client testing API's domain). Evidence: `docs/protocol-research/evidence/card97-report-2026-06-19/
  findings.md`. Card 97 remaining: change 2 date grid cell (deferred — calendar/OS); read-decode follow-ups
  (cross-region value read; number/date value parser; the .mxl spreadsheet decode).
- 2026-06-19 change 3 (reports) FUNCTIONALLY COMPLETE — **spreadsheet CELL-read SHIPPED:** `read_spreadsheet_cell`
  (MCP #38, 38 tools / 261 tests), live-verified PASS 4/4 (R1C1→PF_RPT_R1C1 … R2C2→PF_RPT_R2C2). The earlier
  "binary .mxl boundary" was a RED HERRING — a cell is read by an IN-CLIENT 1C method (NOT a wire-decode): the
  navigate «перейти к ячейке» (`EditField[PF_REPORT] 88 82 81 fa <len><addr>`) + the client's value echo
  (`9a <len><value>`, the card-79 shape) — proven by reading a cell into a Vanessa variable (CELL11="PF_RPT_R1C1")
  in a 6.5 KB exchange while the full form-read binary carries only a 20-byte handle. read_spreadsheet_cell
  replays navigate-to-cell + retargets the address + parses the value; no .mxl decode. Evidence:
  `docs/protocol-research/evidence/card97-report-2026-06-19/findings.md`. Card 97 remaining: change 2 date grid
  cell (deferred — calendar/OS); read-decode follow-ups (cross-region value read; number/date value parser).
- 2026-06-19 read-decode follow-ups BOTH DONE (offline + live). **(b) number/date value PARSER:** premise was
  STALE — number AND date already decode as formatted display text (genuine-capture verified: PF_EDIT_NUMBER→
  "120,50", PF_EDIT_DATE→"15.01.2026 10:30:00"); fixed a latent parser bug (a value-read echoes the field name
  first as an `81 fa` descriptor → the old single-`find` returned None; `extract_edit_field_value` now scans all
  occurrences + decodes the `e0 4b 53 9a` envelope + skips the `e2` stub) + added a `numeric` assert mode
  ("120,50"=="120.5"). **(a) cross-region value read:** the value-read query carries the FULL element path; a
  full-path retarget (`_retarget_read_to_groups`) + a `groups` param read PF_GROUP_MAIN markers capture-free
  (live: PF_LAST_ACTION→"PF_STATE_INITIAL", PF_FIXTURE_VERSION→"protocol-fixture.v1"). 272 tests. Evidence:
  `card97-numdate-parser-2026-06-19/`, `card97-crossregion-read-2026-06-19/`. (commits 962e1b2)
- 2026-06-19 change 2 DATE grid cell SOLVED → **card 97 COMPLETE, moved to 4.done.** Protocol text-SET ruled out
  + synthetic keystrokes don't reach 1C's masked date editor (decisive control: `xdotool type` DID land in plain
  PF_EDIT_STRING); the working path is protocol-activate the cell (write_block, no commit) → MOUSE calendar pick
  (click dropdown → month → day → Return). Live-verified row 1 `10.01.2026 9:00:00`→`15.08.2026 0:00:00`,
  committed. Productized the date→click geometry (`calendar_{month,day}_cell` in native_xtest.py, +5 tests, 277
  total). Evidence: `card97-date-gridcell-2026-06-19/findings.md`; probe `date_cell_calendar_probe.py`. (commit
  24dcbaa) **Productization remainders → card 98:** a general `set_table_date_cell` MCP tool needs on-screen cell
  localization; automatic cross-region `groups` discovery — both fold into card-98 form-introspection.
