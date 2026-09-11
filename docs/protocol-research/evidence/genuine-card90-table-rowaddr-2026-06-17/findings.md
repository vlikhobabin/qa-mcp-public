# Card 90 — table row addressing: select / write-to-row-N / add-row (2026-06-17)

## Summary

`set_table_cell` writes into the **active row**. This addresses a SPECIFIC row. Result: **capture-free
row-addressed write is SOLVED** — the native row-select is "find the row where COLUMN = VALUE" (both
length-prefixed strings in the genuine command), so **re-targeting the fixed-width VALUE selects an ARBITRARY
row by its cell value**, and the active-row cell SET then lands there. Live-proven: `PF_ROW_002_TEXT` →
`PF_ROW_003_TEXT` selects + writes row 3. Productized: `select_table_row` + `set_table_cell(row_match=…)`.
Row-select is also **observable** (a deployed fixture OnActivateRow handler). And **`add_table_row` is DONE** via
a custom `PF_ADD_ROW` command (the standard «add row» discards an uncommitted empty row) — plus a generic
`click_command(button)` for any form-command button.

## Fixture fix (deployed) — make row-select observable

The fixture had NO OnActivateRow handler, so `PF_SELECTED_ROW_MARKER` only ever held `PF_ROW_NONE`. Added
`Module.bsl` `&НаКлиенте Процедура PF_TABLE_ITEMSПриАктивизацииСтроки(Элемент)` → sets
`PF_SELECTED_ROW_MARKER = "PF_ROW_IDX_<1-based index>:<row marker>"`, wired via `<handlers><event>OnActivateRow`
on the `PF_TABLE_ITEMS` FormTable. Deployed via the manual `ibcmd` procedure (gen `3aab6541…` → `abce119a…`;
backups `Module.bsl.bak-card90-rowaddr` / `Form.form.bak-card90-rowaddr` / `1Cv8.1CD.bak-card90-rowaddr-pre`).
Metadata validation passed (OnActivateRow is a valid FormTable event).

## Row-select — works live + observable + decoded (structurally)

Vanessa step: `в таблице "PF_TABLE_ITEMS" я перехожу к строке:` + a value table (column→value). Live-proven:
positioning to row 2 (by `PF_TABLE_TEXT=PF_ROW_002_TEXT`) → `PF_SELECTED_ROW_MARKER = "PF_ROW_IDX_2:PF_ROW_002"`;
row 3 → `PF_ROW_IDX_3:PF_ROW_003`. Capture `genuine-card90-rowaddr-20260617` (719 chunks).

Decode (KEY): the row-select is "find the row where COLUMN = VALUE". The genuine command frame carries BOTH as
length-prefixed strings:
```
… c0 4b 53  9a 0d "PF_TABLE_TEXT"  eb 53  9a 0f "PF_ROW_002_TEXT"  20 20…(fixed-width pad)
            └ 9a,len13 ┘                  └ 9a,len15 ┘
            ── search COLUMN ──            ── search VALUE (fixed-width) ──
```
So **re-targeting the VALUE (fixed-width, via `retarget_value`) selects a DIFFERENT row** — the same machinery
as a cell SET. Live-proven: replaying the row2write capture with `PF_ROW_002_TEXT`→`PF_ROW_003_TEXT` made **row 3
active** (screenshot `rowselect-retarget-shot/.../0-before.png`: row 3 highlighted). (The surrounding `e0 4b 55`
Table frames are the scroll/sort of the search interaction; the column+value frame above is the actual select.)

## Capture-free WRITE INTO A SPECIFIC EXISTING ROW — ✅ PROVEN

Because the cell SET hits the ACTIVE row, a capture whose SETUP selects the target row writes into that row.
Capture `genuine-card90-row2write-20260617` (connect + open + position to row 2 + edit `PF_TABLE_TEXT="R2WROT"`
+ commit). Live (Vanessa): row 2 → `R2WROT`, rows 1/3 unchanged, marker `PF_ROW_IDX_2:PF_ROW_002`. **Capture-free
replay** (`set_table_cell_row_shot.py`: `NativeWriteSession` + `derive_table_cell_write(captured_value="R2WROT",
commit_partner_value="C90RC")` + `set_table_cell("ROW2OK")`): on a fresh native client the grid shows
**`PF_ROW_002 = ROW2OK`** while **`PF_ROW_001` is UNCHANGED** (`PF_ROW_001_TEXT`) — the write landed in row 2,
not the default active row 1. Screenshot: `runtime/protocol-research/table-cell-row-shot/20260617-132052/`.

⇒ Productization (row addressing by value): `NativeWriteSession(setup_retargets=…)` applies fixed-width value
swaps to the setup frames; `set_table_cell(value, …, row_match=<col value>, captured_row_match="PF_ROW_002_TEXT")`
re-points the genuine row-select's search value so the row whose column equals `row_match` becomes active and the
cell SET lands there; standalone `select_table_row(template, row_match, …)` selects only. MCP tools:
`set_table_cell(row_match=…)` + **`select_table_row`** (16th tool). +2 unit tests (suite **220**). Live-verified:
the productized `set_table_cell(row_match="PF_ROW_003_TEXT")` left rows 1/2 unchanged (write went to row 3) —
`set_table_cell_rowmatch_shot.py`, `rowselect_retarget_shot.py`, `set_table_cell_row_shot.py` (write to the
captured row).

## add-row (`add_table_row`) — ✅ DONE (custom command)

The standard «в таблице … я добавляю строку» does NOT persist (1C discards an uncommitted empty new row). So the
fixture now exposes a custom **`PF_ADD_ROW`** command+button (handler: `PF_TABLE_ITEMS.Добавить()` + a distinct
marker `PF_ROW_ADDED_<n>` / `PF_ADDED_TEXT` + activate the new row + `PF_LAST_ACTION`). Deployed via manual
`ibcmd` (gen `abce119a…` → `98fc8582…`; backups `*.bak-card90-addrow`). Live (Vanessa): clicking it made the
table **4 rows** (`PF_ROW_ADDED_4` persisted + active).

Decode: a form-command click activates the `…Group[PF_COMMAND_BAR_MAIN].Button[PF_ADD_ROW]` element
(`88 81 81 e1` command-execute) — the Button twin of switch_page/toggle_checkbox; the form-open render is an
earlier Button[…] run, the click is the LAST run. Capture `genuine-card90-addrow-20260617`.

Productized: `derive_command_click` + `click_command(target_button)` (GENERIC capture-free form-command click —
retargets the `Button` leaf) + `add_table_row` (clicks `PF_ADD_ROW`) + MCP tools `click_command` / `add_table_row`
(now **18** qa-mcp tools) + 2 unit tests (suite **222**). Live-verified capture-free (`add_table_row_shot.py`):
on a fresh native client `PF_LAST_ACTION=PF_ADD_ROW`, `PF_ACTION_COUNTER=1`,
`PF_SELECTED_ROW_MARKER=PF_ROW_IDX_4:PF_ROW_ADDED_4` (screenshot). No value read-back — verify via PF_LAST_ACTION
or screenshot.

## Follow-ups (§8)

1. ✅ **DONE** — arbitrary-row select capture-free (retarget the row-select VALUE; `select_table_row` /
   `set_table_cell(row_match=…)`). Remaining nuance: selection is by a column VALUE (not a raw index); selecting
   by index would need reading the table first to map index→value.
2. ✅ **DONE** — `add_table_row` (custom `PF_ADD_ROW` command) + a GENERIC `click_command(button)` for any form
   command button (capture-free). See the add-row section above.
3. ✅ **DONE** — grid cell read-back. The SET response echoes the committed cell value via
   ``EditField[<col>] <counter> e0 41 81 81 ba <varint-len><value>`` (the middle counter byte varies, e.g.
   ``\x82``, which the old ``read_field_value_near`` `\x81\x81\x81` anchor missed). New ``read_table_cell_value``
   parses it; `set_table_cell` now returns a REAL read-back — live-verified: `set PF_TABLE_TEXT='HELLO9' →
   readback='HELLO9' committed=True` (no screenshot needed). +1 unit test (suite **223**).
