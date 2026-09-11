# Card 98 — DYNLIST whole-grid read: «перехожу к следующей строке» captured + decoded + `read_list_grid` shipped

**Date:** 2026-06-20. **Result:** the dynlist NEXT-ROW navigation command is captured (genuine Vanessa manager),
decoded, and productized — `read_list_grid(open_link, columns, max_rows)` reads MANY rows × columns of a dynamic
list in ONE cold session (no Vanessa). Live-verified on the vanessa_client Товары list.

## The capture (genuine Vanessa manager)

Booted the genuine manager (Xvfb :77, MCP :9874) + auto-allow, stopped apache, tcpdump `lo` portrange
48000-48400, ran `qa-card98-capture-nextrow.feature`:

```
И я открываю основную форму списка справочника "Товары"
И в таблице "Список" я перехожу к первой строке
И я запоминаю значение поля с именем 'Наименование' таблицы "Список" как "Р1"
И в таблице "Список" я перехожу к следующей строке          ← the NEXT-ROW step (ВТаблицеЯПерехожуКСледующейСтроке)
И я запоминаю значение поля с именем 'Наименование' таблицы "Список" как "Р2"
И в таблице "Список" я перехожу к следующей строке
И я запоминаю значение поля с именем 'Наименование' таблицы "Список" как "Р3"
```

Scenario **Success**. Client TPort 48001, manager port 41806 → `pcap_to_traffic … 48001 … 41806` →
`captures/genuine-card98-nextrow` (33 mgr / 32 cli). The reads decode to **Обувь → Продукты → Услуги** (3
distinct rows — the cursor advanced), confirming «перехожу к следующей строке» works on a real catalog list.

## The decode

The go-to-row command is a **4-frame block** (`88 82 81 20 20 20` frame A + partner, then `88 82 81 e1 20 20 20`
frame B + partner) at `Table[Список]`. Byte-diff first-row vs next-row:

- **Frame A is BYTE-IDENTICAL** for first-row and next-row (only the seq @19 + a 16B nonce @70-85 differ).
- **Frame B carries a 16-byte ACTION GUID at offset 53** (right after the `cb 23 95` header marker) that selects
  the action — and it is **constant across invocations**:
  - go-to-FIRST-row: `3e312772-a733-f14a-928d-66945ecff123`
  - go-to-NEXT-row:  **`d267315b-1d90-0041-8c4e-c1ff077822d5`**  (next#1 == next#2)

So advancing the dynlist cursor = replaying the genuine next-row block (the `d267315b…` action), then the
table-cell read returns the now-current row.

## Productized — `read_list_grid` (MCP, +1 tool)

`read_list_grid_replay` (native_write.py): cold full-replay of `genuine-card98-nextrow` THROUGH the first read
(setup + open + first-row, nav-link re-targeted), then a loop — replay the genuine NEXT-ROW block (mgr frames
between read#1 and read#2, rebound + sequence-bumped) to advance, then one table-cell read per requested column
(read frame column-retargeted, **message-id kept**, sequence bumped) — all on the SAME socket (the cold-client
materialised session). Stops at `max_rows` or when a row repeats / reads empty (end of list). MCP
`read_list_grid(open_link, columns, max_rows)`. `NEXT_ROW_ACTION_GUID`/`FIRST_ROW_ACTION_GUID` recorded as
constants. 336 tests (+2).

**Live-verified (vanessa_client Товары, columns Наименование+Код, max_rows=6):**

| row | Наименование | Код | note |
| --- | --- | --- | --- |
| 1 | Обувь | 000000001 | matches capture |
| 2 | Продукты | 000000011 | matches capture |
| 3 | Услуги | 000000036 | matches capture |
| 4 | **Электротовары** | 000000012 | **NOT in the capture — iteration beyond the captured 3 rows** |

(`row 4` reads «Электротовары»; codes verified vs OData.) The reader auto-detected end-of-list (the visible
hierarchical view shows 4 top-level group rows; the 5th next-row repeated «Электротовары» → break). So it reads
MANY rows × MANY columns, advancing past the captured count, with correct end-of-list — capture-free, no Vanessa.

## Boundaries (honest)

- Reads the list's **current view/sort order**. The Товары default view is HIERARCHICAL → only the 4 top-level
  group rows are walked; reading nested items needs a flat view first (`set_list_view` «Список») — a compose step,
  not a new mechanism.
- One grid read per fresh `launch_test_client` (the cold-client boundary — per CLIENT PROCESS).
- Row-by-VALUE («перехожу к строке» exact match) is still the earlier NEGATIVE (the form-table command doesn't
  splice onto a dynlist); a genuine dynlist «перехожу к строке» capture would add it (now easy — same recipe).

## Artifacts

- Capture: `runtime/protocol-research/captures/genuine-card98-nextrow/` (feature
  `tools/protocol-research/qa-card98-capture-nextrow.feature`).
- Code: `src/qa_mcp/protocol/native_write.py` (`read_list_grid_replay`, `NEXT_ROW_ACTION_GUID`,
  `FIRST_ROW_ACTION_GUID`); MCP `read_list_grid` in `mcp_server.py`.
- Tests: `tests/test_form_descriptor.py` (`test_read_list_grid_tool_shape`).
