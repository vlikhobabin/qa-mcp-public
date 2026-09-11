# Card 90 — table-cell input: deploy + capture + decode (2026-06-17)

## Summary

The table-cell **FIXTURE GAP IS CLOSED** (table made editable + deployed live) and the table-cell input
protocol is **DECODED**: a table cell commits via the **exact same value-SET as a plain string field**, only the
element path differs (a `Table[NAME]` segment with the **column** as the `EditField` leaf, **no row index** —
the edit hits the *active* row). Productization therefore reuses the existing card-86b/c string-commit
machinery; it is the checkbox/choice/page-switch `derive_* + retarget` pattern, not a new mechanism.

## Deploy (done + live-verified)

Form.form table-cell fix (remove editing `<excludedCommands>` + `<readOnly>` on PF_TABLE_TEXT/PF_TABLE_NUMBER)
deployed to the live `vanessa_client` file infobase. generation `bf03a87f…`→`e1496ab9…`. Genuine-manager run:
`в таблице "PF_TABLE_ITEMS" в поле с именем 'PF_TABLE_TEXT' я ввожу текст "TBLOK"` → **Success** (+ add-row
Success). Procedure: manual `ibcmd export/import/apply` (because `run_dev_infobase_apply` is structurally
workspace-locked in-session) — full detail in `../../capture-free-epic-state.md` §7 Step 1.

## Capture

Self-contained replayable capture: `tools/protocol-research/qa-card90-capture-table-selfcontained.feature`
(connect + open + add 2 rows + edit PF_TABLE_TEXT = "CELLAA" then "CELLBB" + a focus-change commit). Genuine
manager↔client traffic (client TPort 48003, manager port 54484):
`runtime/protocol-research/captures/genuine-card90-table-20260617/traffic-selfcontained/traffic.jsonl`
(767 chunks). Decoder: `tools/protocol-research/card90_table_decode.py`.

## Decode (the key finding)

The genuine cell-SET frame (manager→client, chunk #29/#30 for CELLAA, #42/#43 for CELLBB):

```
…Group[PF_GROUP_MAIN].Table[PF_TABLE_ITEMS].EditField[PF_TABLE_TEXT]  <counter 3B>  e0 41 81 81 ba 06 "CELLAA" 20 20 20  <nonce>
                       └────── Table[] segment ──────┘└── column leaf ──┘                 │  │  └ value (latin1)
                                                                                          │  └ varint length = 6
                                                                                          └ value-SET tag (IDENTICAL to a plain string field)
```

- Element path = `SecondaryFrame[S].ManagedForm[F].Group[PF_GROUP_MAIN].Table[PF_TABLE_ITEMS].EditField[PF_TABLE_TEXT]`.
  The table is a `Table[NAME]` path segment (kind `Table`), the **column** is the `EditField[NAME]` leaf.
- **No row index anywhere in the frame** — the value commits into the **active/selected row** (both CELLAA and
  CELLBB landed on row 1; read-back showed row 1 PF_TABLE_TEXT = "CELLBB"). Row selection is a *separate*
  concern (select the row first; not part of the cell-SET).
- The value buffer (`e0 41 81 81 ba <varint-len> <value> <pad>`) and the per-type commit law (SET + a
  focus-change to any other field) are **byte-identical to the plain string SET** (card 86c).

## Productize — ✅ DONE + LIVE-VERIFIED (2026-06-17)

Implemented (reuses the card-86c commit machinery, since a cell SET *is* a string SET):
- `element_ref.retarget_element_segment(frame, old, new, kind="Table")` — retarget a MID-path `Table[…]`
  segment (the column stays the `EditField` leaf; `retarget_element_leaf` handles the column).
- `native_write.derive_table_cell_write(cap, column="PF_TABLE_TEXT", captured_value="CELLAA",
  commit_partner_field="PF_EDIT_STRING", commit_partner_value="C90CMT")` → a commit-partner `WriteTemplate`
  (on the real capture: setup_end=26, write_block=(27,30), commit_block=(45,46)).
- `NativeWriteSession.set_table_cell(value, column=…, table=…)` + standalone `set_table_cell(template, value, …)`
  — write block (cell activate+SET, value+column+optional Table retarget) → synthesized focus-change commit.
- MCP tool `set_table_cell(value, column, table, …)` — the **14th** qa-mcp tool.
- Unit tests (4 new, offline) in `tests/test_native_write.py`; full suite **216 passed**.
- Probes: `tools/protocol-research/{set_table_cell_probe,set_table_cell_shot,set_table_cell_debug}.py` +
  `run_table_cell_test.sh`.

**Live proof (native client, no Vanessa):** `set_table_cell_shot.py` (launch_test_client owned display → write →
screenshot) wrote `HELLO9` into the active row's PF_TABLE_TEXT — the grid cell `PF_ROW_001` changed
`PF_ROW_001_TEXT` → **`HELLO9`** and focus moved to PF_EDIT_STRING (the commit). Screenshots:
`runtime/protocol-research/table-cell-shot/20260617-094510/{0-baseline,1-after}.png`. Also the SET response
echoes the written value (`set_table_cell_debug.py`).

**READ-BACK caveat:** a committed table cell renders into the GRID, NOT as a plain `EditField` value-read, so
`read_field_value_near` returns None for table columns → `set_table_cell`'s `readback_value`/`committed` are
best-effort (typically None/False even on success). Verify visually (capture_screenshot), like page-switch. A
proper grid read-back (decode the table sweep) is a future nicety.

**Active-row semantics (not yet productized):** the write hits the ACTIVE row. The captured setup leaves row 1
selected (the active cell), so the write targets row 1. To target other rows, decode/productize row-select +
add-row (the add-row command IS in this capture) — future work for a full row-addressed `set_table_cell`.
