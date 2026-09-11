# Card 97 change 2 — number / date grid cells

**Date:** 2026-06-19. **Result:** the NUMBER grid cell is SOLVED (no new code — the card's "different per-type
buffer" assumption is disproven for grid cells); the DATE grid cell's protocol path is characterized + bounded
(the date control rejects text input). Fixture gained a `PF_TABLE_DATE` column for future date work.

## ✅ Number cell — SOLVED (assumption disproven)

The card assumed number/date grid cells use "a different per-type value buffer (like the plain fields, card
86c)". **Not true for grid cells.** The genuine `PF_TABLE_NUMBER` cell SET is **byte-identical to the string
cell SET**:

```
EditField[PF_TABLE_NUMBER] 88 82 81  e0 41 81 81 ba  03  37 37 37  20 20 20 …
                                     └ value-SET tag ┘ len  "777"  (ASCII text)
```

Same `e0 41 81 81 ba` tag, LEB128 length, value as ASCII text — exactly the string-cell buffer. So the existing
`set_table_cell` writes a number cell via the column-leaf retarget with ZERO new code. **Live-proven 2026-06-19:**
`set_table_cell(value="999", column="PF_TABLE_NUMBER")` → readback_value="999", committed=True. (The per-type
buffer difference is real for plain FIELDS — card 86c PF_EDIT_NUMBER "777,77" — but the grid cell editor sends
the value as text.) `set_table_cell` docstring updated.

## ⚠️ Date cell — characterized + bounded (follow-up)

Adding a date grid cell to drive: the fixture table gained a **`PF_TABLE_DATE`** column (DateTime; baseline
dates per row), deployed (gen 5569447…). But:
- `в таблице "PF_TABLE_ITEMS" в поле с именем 'PF_TABLE_DATE' я ввожу текст "15.08.2026"` →
  **«Неподходящий тип элемента управления для вызванного действия»** (the date control rejects the text-input
  action; nothing captured — 0 `EditField[PF_TABLE_DATE]` frames).
- Vanessa's only date-input steps are `у поля календаря [с именем 'ИмяПоля'] я выбираю дату` — they target a
  standalone **calendar field**, NOT a grid cell. There is no grid-date-cell text step.

So a date GRID cell is not drivable via the captured text-SET path. The genuine date-cell entry needs either a
calendar-field interaction (the inline cell editor surfaced as a calendar element) or OS-level input (the
object-attr-write / page-field class of problem). Follow-up: capture the calendar-field date pick (the
`у поля календаря …` step) against `PF_TABLE_DATE` and decode whether it rides the protocol or VanessaExt.

## Artifacts

- Fixture: `PF_TABLE_DATE` column + FormField + BSL populate (`ДобавитьСтрокуPF` date arg, baseline dates).
- Capture: `runtime/protocol-research/captures/genuine-card97-numdate-20260619/traffic-selfcontained/` (genuine
  PF_TABLE_NUMBER cell SET; the date step failed so no date frames). Feature:
  `tools/protocol-research/qa-card97-numdate-capture.feature`.
- Code: `set_table_cell` docstring (number-cell proof) in `src/qa_mcp/mcp_server.py`. No new tool needed —
  number cells reuse the proven string-cell path.

## Deferred

- Date grid-cell entry (calendar-field pick or OS-level) — the fixture column + the `у поля календаря` step lead
  are in place for a focused follow-up.
