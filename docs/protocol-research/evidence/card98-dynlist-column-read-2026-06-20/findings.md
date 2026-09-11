# Card 98 follow-up — dynlist-column read: STRUCTURE done; VALUE needs Vanessa's table-read command (a capture)

**Date:** 2026-06-20. **Result:** a list form's dynlist columns are enumerated from the descriptor (structure
done), but reading their VALUES is NOT reachable via the form-field value-read — a dynlist cell is per-row data
that needs Vanessa's table-read command, which requires a genuine-manager capture to decode. This is a scoping
finding + the precise next step. 45 MCP tools, 326 tests (no code change).

## What works — column STRUCTURE (already shipped)

`read_form_descriptor(open_link="e1cib/list/Справочник.Валюты")` enumerates the dynlist's columns:
`Table[Список]` + `EditField[Наименование]` / `EditField[Код]` / `EditField[НаименованиеОсновнойВалюты]` /
`EditField[НаименованиеРазменнойВалюты]`. So the list's column SET is introspectable capture-free (the
`extract_descriptor_elements` surface — these EditFields are nested under `Table[Список]`, which is why
`extract_descriptor_fields` correctly excludes them from form-field VALUES).

## What does NOT work — column VALUES via the value-read

Retargeting the value-read query to `SecondaryFrame[S].ManagedForm[F].Table[Список].EditField[<col>]` (a custom
Table-path rewrite, ASCII→UTF-16 reencode for the Cyrillic column names) on the populated demo Валюты list:

```
descriptor 22410B → 4 EditField columns: ['Наименование', 'Код', 'НаименованиеОсновнойВалюты', 'НаименованиеРазменнойВалюты']
  col Наименование:               resp 1274B, value-envelope=False, parsed={}
  col Код:                        resp 1220B, value-envelope=False, parsed={}
  col НаименованиеОсновнойВалюты:  resp 1358B, value-envelope=False, parsed={}
  col НаименованиеРазменнойВалюты: resp 1364B, value-envelope=False, parsed={}
```

The query RESOLVES the Table column (per-column responses, ~1.2–1.4 KB, growing with the column-name length, the
name echoed) but returns **no `e0 4b 53` «стал равен» value envelope**. A dynlist `Table[…].EditField[col]` is
NOT a single-value form attribute — it is the column DEFINITION over many rows; the value-read (which reads one
form attribute's value) has no row to resolve, so it returns no value. This mirrors the form-field case where the
value-read reads `Group[…].EditField[name]`: the same query shape does not address per-row table data.

## The real mechanism — Vanessa's table-read command (needs a genuine capture)

Reading a dynlist cell is the test-manager's TABLE/row API (Vanessa's `ТаблицаФормы … ТекущиеДанные` / a
get-row-value command), not the form-field value-read. To decode it capture-free, follow the lab recipe
([[genuine-action-capture-recipe]]): boot the genuine Vanessa manager, connect a client, run a feature that reads
a table cell (e.g. «в таблице "Список" … значение колонки …»), tcpdump the manager↔client traffic,
`pcap_to_traffic.py`, and decode the table-read command + its row-data response. Then productize as a
`read_list_column` / `read_table_cell(row, column)` MCP tool (the proven derive_+replay+splice pattern). This is
a full capture+decode cycle — its own session, not a value-read retarget.

This also unblocks the **non-empty navigated value-read** (card98-navigated-record-valueread): a list's row data
is populated, so a decoded table-read yields a real value AND a row ref (`e1cib/data/Справочник.X?ref=…`) to open
a populated record form.

## General `set_table_date_cell` — status (the other half)

Unchanged from card 97: the DATE grid cell is SOLVED as a mechanism (protocol-activate + mouse calendar pick;
`calendar_{month,day}_cell` geometry shipped + tested), but a GENERAL MCP tool needs **on-screen cell
localization** — the calendar-button + popup-origin screen coords (the probe hardcodes fixture coords). The
home for this is the descriptor's element BOUNDS (if derivable) or a screenshot-localization step. Same
dependency as a general table-cell-by-coords tool: element geometry. Deferred pending element-bounds in the
descriptor.

## Artifacts

- Probe: `tools/protocol-research/dynlist_column_read_probe.py` (the value-read-retarget feasibility test).
- No code change (a scoping finding). Next: capture Vanessa's table-read command, then productize.
