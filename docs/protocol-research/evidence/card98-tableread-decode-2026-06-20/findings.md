# Card 98 — TABLE-CELL READ command DECODED (genuine Vanessa capture)

**Date:** 2026-06-20. **Result:** the genuine Vanessa table-cell-read command (`И я запоминаю значение поля с
именем 'F' таблицы "T" как "V"`, type `Переменные.Сохранить значение.Таблица.Поле таблицы`) is captured + decoded.
It is a TABLE command (addresses the Table element + the column NAME as a suffix), NOT a `Table[T].EditField[col]`
path-leaf value-read — which is why the earlier `dynlist_column_read_probe` (a path-leaf retarget) resolved but
returned no value. The response carries the cell value in the same `e0 4b 53 9a <len> <value>` envelope the
existing `extract_form_field_values` already decodes.

## The capture

Genuine manager (Xvfb :77, MCP :9874) ran `qa-card98-capture-tableread.feature`: connect a TestClient to
vanessa_client → open the fixture → add a row → write `CELLREAD7` into `PF_TABLE_TEXT` → commit (focus-change to
PF_EDIT_STRING) → **read** the cell by name. tcpdump on lo 48000-48400; client TPort 48001; dominant manager port
35958; `pcap_to_traffic … 48001 … 35958` → `captures/genuine-card98-tableread` (47 mgr→cli / 38 cli→mgr chunks).
The read step is the last action → its command + response are chunks **[73]/[74]**.

## The command (manager→client, chunk [73], 264 B)

```
<header … cb 23 95> <33B nonce> 9a <pathlen> <PATH> 88 81 81 e0 4b 55 eb 53 9a <collen> <COLUMN> 20 20 20 20 66 53 b2 a6
```

- `PATH` = `SecondaryFrame[S].ManagedForm[F].Group[PF_GROUP_MAIN].Table[PF_TABLE_ITEMS]` — the Table element path
  (its enclosing groups + the Table leaf), as the `9a <byte-len> <latin1>` / `97 <char-count> <utf-16le>` block.
- `88 81 81 e0 4b 55 eb 53` — the read-cell opcode. **`e0 4b 55`** is the activate/read-with-action prefix (cf.
  `e0 4b 53` = choose-variant, `e0 4b 55` = the table read here); `eb 53` precedes the column name block.
- `COLUMN` = the field NAME (`PF_TABLE_TEXT`) as a `9a <len> <name>` (ASCII) / `97 <count> <utf-16>` (Cyrillic)
  string block — addressed by NAME, like the form-field reads.
- `20 20 20 20` pad + `66 53 b2 a6` frame tail.

So the cell is read of the table's CURRENT ROW (no row index in the command — it reads the active row).

## The response (client→manager, chunk [74], 235 B)

```
<header cb 23 95> <nonce> 9a <pathlen> <PATH> 81 81 81 e0 4b 53 9a 09 "CELLREAD7" eb 53 9a 0d "PF_TABLE_TEXT" 20 20 a1 a3 66 53 b2 a6
```

- `81 81 81` response opcode, then **`e0 4b 53 9a 09 CELLREAD7`** — the value rides the canonical
  `e0 4b 53 9a <len> <value>` «стал равен» envelope, exactly what `extract_form_field_values` /
  `extract_edit_field_value` already decode. Then the column name is echoed (`eb 53 9a 0d PF_TABLE_TEXT`).
- ⇒ **no new response parser needed** — the existing value decoder reads `CELLREAD7`.

## Productization plan (splice, like descriptor/window-list)

The command body after `cb 23 95` is session-independent apart from the path GUIDs + the echoed nonce (not
validated), so it splices onto a live value-read header (`_splice_header_no_form`):

```
splice_table_cell_read(header, S, F, groups, table, column) =
  header + NONCE + encode_element_path_block("SecondaryFrame[S].ManagedForm[F].<Group[g].>*Table[table]")
         + b"\x88\x81\x81\xe0\x4b\x55\xeb\x53" + encode_element_path_block(column) + b"\x20\x20\x20\x20" + b"\x66\x53\xb2\xa6"
```

dual-encoding (ASCII 0x9a / Cyrillic 0x97) for both the path and the column. Parse the response with
`extract_form_field_values`. This reads the CURRENT ROW's cell — a `read_table_cell(table, column)` /
`read_list_column(column)` MCP tool. It ALSO unblocks the non-empty navigated value-read (a list row's data is
populated). Constants: `NONCE=49e435875c8d1b408e6db0b800402d80d57169d3613479a845ad5b8f42f5e21bec`,
`SUFFIX=888181e04b55eb53`, `PAD=20202020`, `TAIL=6653b2a6`.

## Live replay — the command REPLAYS structurally; value needs a current row

`splice_table_cell_read` is built (dual-encoding, +1 test → 327) and **replays on the demo Валюты dynlist**: the
spliced command resolves (the response path is the live `…Table[Список]` in UTF-16, the column name echoed) and
the read opcode round-trips — but it returns **no value envelope**. The demo response is
`<header> <nonce> 97 <pathlen> SecondaryFrame[…].ManagedForm[…].Table[Список] 8a 81 81 e0 4b 55 eb 53 97 0c
Наименование 20 20 a1 a3 <tail>` — i.e. the client echoes the command (`8a 81 81 e0 4b 55`, NOT the genuine
response's `81 81 81 e0 4b 53 9a <value>`), with **no `e0 4b 53 <value>`**. So the read reaches the dynlist but
there is **no current-row value to return**: the genuine capture read a form table whose CURRENT ROW was the row
just added + edited (cursor on it), whereas a dynlist freshly opened by nav-link has **no active/loaded current
row** at read time. ⇒ the decode + splice are correct; an end-to-end VALUE read needs a current row established
first (select/activate a row, or read after the list loads + a row is current). The cleanest value-replay proof
is the captured scenario itself — open the fixture, add a row + write a cell (shipped row-op + set_table_cell),
then `splice_table_cell_read` — reading the value back in one session.

## Productized — `read_table_cell` (form tables) ✅ live-verified; `read_list_column` (dynlist) pending current row

`extract_table_cell_value` (responses.py) decodes the response value directly (the `81 81 81 e0 4b 53 <type> …`
envelope after the Table path — `extract_form_field_values` anchors on EditField leaves and misses it; the
genuine `CELLREAD7` decodes). MCP tools `read_table_cell(table, column, open_link?)` + `read_list_column(column,
open_link)` (#46/#47): open the fixture (frames 11-17) or ANY form (`open_link`, config-agnostic), discover the
table's enclosing groups from the live descriptor (`_table_groups`), splice the read, decode the value. **330
tests.**

**Live-verified — fixture form table (3 default rows, row 1 current on open):**
```
read_table_cell("PF_TABLE_ITEMS","PF_TABLE_TEXT")   → "PF_ROW_001_TEXT"   groups=['PF_GROUP_MAIN']
read_table_cell("PF_TABLE_ITEMS","PF_TABLE_NUMBER") → "1,10"
read_table_cell("PF_TABLE_ITEMS","PF_TABLE_MARKER") → "PF_ROW_001"
```

A FORM table populated at `ПриСозданииНаСервере` has row 1 current on open → the read returns the canonical
value (string / number, ASCII + Cyrillic). A DYNLIST (`read_list_column`) freshly opened by nav-link returns no
value (the response carries `e0 4b 55` echo, no `e0 4b 53` value) — its rows load from a server query and no row
is the «current data» yet; establishing a dynlist current row (row-select/activate, or read-after-load) is the
open follow-up.

## Dynlist read — current-row positioning DECODED; read-by-name does not reproduce (honest boundary)

A second genuine capture (`genuine-card98-dynlist-read`: the fixture dynlist `ДенамическийСписокИерархия` over
Catalog.Товары — «перехожу к первой строке» + «я запоминаю значение поля с именем 'Наименование' …») decoded the
**dynlist row-position commands** — table-level invokes at `Table[name]`, a 2-frame pair each:
`<nonce> <Table path> 88 82 81 20 20 20` + `… 81 81 81 20 20 20` (and a `… 88 82 81 e1 20 20 20` / `81 81 81 e1`
variant). The read command [41] is the same `88 81 81 e0 4b 55 …` family. **But the genuine read FAILED** in
Vanessa: `ПолучитьТекстЯчейки … В элементе управления отсутствует указанное значение` — the fixture's dynlist has
AUTO-generated (unnamed) columns, so "Наименование" is not an addressable cell even for Vanessa.

Replaying the position pairs + the read via splice yields **no value** on EVERY dynlist tried — demo Валюты
(possibly empty) AND **vanessa_client `Справочник.Товары` (definitely populated: Молоко/Творог, named columns)**:
the response is the read command echoed (`e0 4b 55`, no `e0 4b 53` value). So the `e0 4b 55` table-cell read is a
**FORM-TABLE mechanism** — it reads a form table's current row (verified) but does NOT reproduce a dynlist column
read via splice (even with positioning, even on a populated named-column list). A dynlist column read is a
distinct surface (Vanessa's `ПолучитьТекстЯчейки` for a dynlist), not yet reproduced capture-free. **`read_table_cell`
(form tables) is the verified deliverable; `read_list_column` (dynlist) returns None pending that distinct
mechanism.** Positioning commands are decoded (`genuine-card98-dynlist-read` [33]/[35]/[37]/[39]) for the next step.

## ⭐ DYNLIST read DECODED on a REAL catalog list form — same command, value verified («Обувь»)

A third genuine capture (`genuine-card98-listform-read`) opened a REAL catalog LIST form — «Я открываю основную
форму списка справочника "Товары"» (vanessa_client Товары: Молоко/Творог/Обувь, NAMED columns) — positioned to
the first row, and read column «Наименование». **The genuine read SUCCEEDED.** The command [41] and response [42]:

- **Command [41]** = `<nonce> <path: SecondaryFrame[S].ManagedForm[F].Table[Список]> 88 81 81 e0 4b 55 eb 53
  97 0c Наименование 20 20 20 20 <tail>` — **BYTE-IDENTICAL to what `splice_table_cell_read(groups=[],
  "Список", "Наименование")` builds.** The dynlist read does NOT differ from the form-table read — same
  `e0 4b 55` command, table by name + column by name, groups=[] (Table directly under ManagedForm).
- **Response [42]** = `… 81 81 81 e0 4b 53 97 05 <utf-16> …` → **`extract_table_cell_value` decodes it as
  «Обувь»** (the first Товары row). The parser + splice are CORRECT.

So the dynlist column read is the SAME mechanism as the form-table read — **the earlier "distinct surface"
conclusion is WRONG**. The actual gap is FORM STATE: the genuine opened the list via a Vanessa form-open command +
positioned to row 1 (the table-action commands [33]/[35] `88 82 81 20 20 20` + [37]/[39] `88 82 81 e1 …`, with a
preceding `88 81 81 e0 4b 55 <spaces>` activate [27]), whereas the engine's nav-link open + a SPLICED position did
not establish a current row. **Positioning is a TABLE-ACTION** (the `88 82 81` family — same as the shipped
row-ops delete/move/copy, which use full-stream replay + GuidRebinder, NOT a splice), so `read_list_column` needs
to position via the row-op-style replay (or the genuine open sequence) THEN splice the read. The READ + parser are
done + value-verified; the bounded next step is positioning the dynlist current row as a table-action.

## Dynlist positioning — the gap is the INTERACTION-ready open, not the read or the sequence

Decoding the genuine list-form capture's full command order between the open and the read:

```
[23]/[25]  navigate  88 82 81 f7 1c <e1cib/list/Справочник.Товары> / 81 81 81 f7 …   (open the list — the SAME f7
                     nav-link navigate the engine's splice_navigate uses; «открываю основную форму списка
                     справочника» NAVIGATES internally)
[27]       activate  88 81 81 e0 4b 55 <spaces>   (no path)
[29]/[31]  render    88 81 81 e1 82 82 84 …  /  88 81 81 e1 82 82 86 … 97 06   (form data-load / render queries)
[33]/[35]  position  Table[Список] 88 82 81 20 20 20 / 81 81 81 20 20 20   (go-to-first-row, 2-frame)
[37]/[39]  position  Table[Список] 88 82 81 e1 20 20 20 / 81 81 81 e1 20 20 20
[41]       read      Table[Список] 88 81 81 e0 4b 55 eb 53 97 0c Наименование → value «Обувь»
```

Sequence counters increment +1 per frame (32050…32057). **Tested the increment hypothesis** (each spliced
command `_set_seq`-bumped) on the populated Товары list — STILL no value. So the gap is NOT the sequence and NOT
the open method (the genuine open is the same nav-link navigate). The gap is that the engine's `_open_form_by_link`
does navigate + window-list + resolve + **descriptor** (an INTROSPECTION open), whereas the genuine does navigate +
**activate [27] + render queries [29]/[31]** (an INTERACTION-ready open) that load the dynlist's data + make the
table the active control, so positioning then takes effect and the read returns the row value. ⭐ **NEXT: an
INTERACTION-ready open** — after the navigate, replay the activate [27] + the render queries [29]/[31] (retargeted
to the live S.F), THEN position + read. (A full-stream replay of `genuine-card98-listform-read` with GuidRebinder
would confirm the whole sequence end-to-end.) The READ + parser + position-command bytes are decoded; the missing
piece is the activate/render that makes the navigated dynlist interaction-ready.

**Four reconstruction attempts FAILED** (Товары list, populated): (1) splice position + read at one sequence;
(2) settle (window-list rounds) + a `88 82 81` table-activate; (3) **incrementing** sequences per command
(`_set_seq`); (4) replay activate [27] + render queries [29]/[31] (retargeted to the live S.F) + position + read,
all sequence-bumped. All return None. The decoded [29]=`<nonce> 9a 34 SecondaryFrame[S] 88 81 81 e1 82 82 84 …`
(S-only) and [31]=`<nonce> 9a 66 SecondaryFrame[S].ManagedForm[F] 88 81 81 e1 82 82 86 … 97 06 Список …` (the
dynlist DATA query, references the table) are session-level/retargetable, but piecemeal replay does not reproduce
the genuine state — the engine's `_open_form_by_link` inserts window-list / resolve / descriptor queries that the
genuine INTERACTION flow does not, so the session's active-form/focus state differs and positioning never takes.
⇒ **the dynlist read needs a FAITHFUL FULL-SEQUENCE replay** (navigate → activate → render → position → read, in
the genuine order, retargeted via GuidRebinder — the card-80 full-stream replay machinery), NOT piecemeal splices.
The READ command + value parser are verified («Обувь»); reproducing the interaction-ready open faithfully is the
bounded next step (its own session with the full-replay harness). `read_table_cell` (form tables) is unaffected
and shipped + verified.

## ⭐⭐ DYNLIST read SOLVED — faithful FULL-SEQUENCE replay (no Vanessa), generalized + value-verified (2026-06-20)

The bounded next step landed: a **faithful full-sequence replay** of `genuine-card98-listform-read` reads a
dynlist column END-TO-END, capture-free. NOT a splice — the WHOLE manager stream replays in the genuine order
(navigate the list form → activate → render/data-load → position to the first row → read), with `GuidRebinder`
rebinding the per-session window GUIDs (the card-80 `set_reference_field` / `read_spreadsheet_cell` loop). The read
frame's response carries the canonical `81 81 81 e0 4b 53` value envelope; `extract_table_cell_value` decodes it.

**Live (vanessa_client), the verbatim case:** replaying the capture as-is returns **«Обувь»** (the first Товары
row) — `dynlist_fullreplay_read_probe.py`: the read frame `mgr[20]` response is
`… 81 81 81 e0 4b 53 97 05 <utf-16 Обувь> eb 53 97 0c <Наименование> …`.

**Generalization — 4/4 COLD cases PASS** (`dynlist_read_freshcase_probe.py`, each a fresh client), the nav-link +
column re-targeted in-frame, verified vs OData ground truth:

| case | nav-link | column | value | OData first row |
| --- | --- | --- | --- | --- |
| verbatim | Справочник.Товары | Наименование | «Обувь» | Обувь (Code 000000001) |
| column-rt | Справочник.Товары | Код | «000000001» | 000000001 |
| list-rt | Справочник.Контрагенты | Наименование | «Покупатели» | Покупатели |
| list-rt | Справочник.Валюты | Наименование | «EUR» | EUR |

So the dynlist read **generalizes across any catalog LIST (nav-link retarget) and any COLUMN (column retarget)**,
reading the first/current row. The navigate tolerates the nav-link resize; `retarget_list_read_frame` swaps the
nav-link (UTF-16 + precise `f7` char-count fix) and the read column block (`eb 53 <path-block>`).

### Root cause of the 4 prior splice failures — CONFIRMED: not the retarget, the SEQUENTIAL replay

`dynlist_read_diag_probe.py` ran verbatim **twice** + the retargets on one client. **`verbatim#2` (byte-identical
to the working `verbatim#1`) ALSO returned None.** So the failure is NOT the retarget — it is replaying against a
client that already served one replay. On the 2nd+ replay the render/data-load responses **shrink** (`mgr[14]`/
`mgr[15]`: cold 343/467 B → warm 118/182 B): the warm on-disk form cache answers with a reduced response so the
dynlist's current-row DATA isn't materialised, and the read echoes the command (`88 81 81 e0 4b 55`, no value).
The piecemeal-splice attempts all failed for the same reason — they ran after `_open_form_by_link`'s introspection
queries (window-list/resolve/descriptor) left the client warm/in a different state; a faithful replay from a fresh
handshake is what reaches the cold interaction-ready open. ⇒ **COLD-CLIENT BOUNDARY:** one dynlist read per fresh
`launch_test_client`; reading several rows/columns per client (a cache reset between replays) is the open follow-up.

### Productized

- `native_write.py`: `ReadListColumnTemplate` + `derive_read_list_column(capture_dir, nav_link, column)` +
  `read_list_column_replay(template, open_link?, column?, …)` + the pure `retarget_list_read_frame(...)` helper.
- MCP `read_list_column(column, open_link, host, port, capture_dir="genuine-card98-listform-read")` **rewired** off
  the (non-working) splice path onto the faithful full-replay. `read_table_cell` (form tables) is unchanged.
- Tests (333 total, +3): `derive_read_list_column` from the real capture (recovers «Обувь»), `retarget_list_read_frame`
  byte-shapes, and the rewired tool shape. Probes: `dynlist_fullreplay_read_probe.py` (verbatim),
  `dynlist_read_freshcase_probe.py` (4-case cold generalization), `dynlist_read_diag_probe.py` (root-cause trace),
  `dynlist_read_generalize_probe.py` (one-client demo of the cold-client boundary).

## ⭐ MULTI-COLUMN read in ONE cold session — `read_list_row` (2026-06-20)

The cold-client boundary is **per-CLIENT-PROCESS**, not the on-disk cache: the `dynlist_read_freshcase_probe`
restarted the client process per case and all 4 passed **despite a warm on-disk form cache** from the prior
process — so the lever is to read everything inside the ONE cold session where the row data is materialised,
rather than one read per fresh client.

`dynlist_multiread_variants_probe.py` proved it, and isolated the trap. After the cold full-replay's captured read
(«Обувь»), an injected extra table-cell read on the SAME socket returns the new column's value **iff the read
frame keeps its message-id** (offset 2):

| variant | extra-read frame | result |
| --- | --- | --- |
| V1 verbatim-ids | column re-targeted, KEEP msg-id(@2) + seq(@19) | «000000001» (VALUE-ENV) |
| V2 bump-seq | column re-targeted, KEEP msg-id, seq+1 | «000000001» (VALUE-ENV) |
| V3 fresh-ids | column re-targeted, **regen msg-id** + seq+1 | None — 481-byte error (OTHER) |

So **offset 2 is a session-validated correlation id — keep it**; regenerating it makes the client answer with a
481-byte Cyrillic error envelope (not the value). With the message-id kept (and the sequence bumped per read), one
cold session reads any number of the current row's columns.

**Productized `read_list_row(open_link, columns)` (MCP, +1 tool):** `read_list_row_replay` does the cold full-replay
THROUGH the captured read, then one extra read per column on the same socket (rebound read frame, column block
re-targeted, message-id kept, sequence bumped). `read_list_column_replay` now delegates to it (single column).
**Live-verified:** `read_list_row("e1cib/list/Справочник.Товары", ["Наименование","Код"])` →
`{Наименование: «Обувь», Код: «000000001»}`. 334 tests. ⚠ Still ONE ROW (the first) per fresh client — reading
further rows needs a captured «next row» command (separate follow-up). Probe:
`dynlist_multiread_variants_probe.py` (+ `dynlist_multiread_probe.py` showing the msg-id-regen failure).

## GO-TO-ROW-BY-VALUE command DECODED; cross-form splice onto a dynlist does NOT reposition (2026-06-20)

Toward reading a SPECIFIC row (by key) / iterating the grid, the «в таблице "T" я перехожу к строке: | col |
value |» command was decoded offline from `genuine-card90-rowaddr` (a FORM table, captured for row 2 then row 3 —
the byte-diff is only the search VALUE + a per-command nonce + the sequence). Body after the `cb 23 95` header:

```
<33B nonce> <path: SecondaryFrame[S].ManagedForm[F].(Group[g].)*Table[T]>
88 81 81 e1 81 81 82  cb 23 95 <16B nonce>  c0 4b 53 <search-column block>  eb 53 <search-value block>  <7sp pad> <tail>
```

The path-block prefix is IDENTICAL to the table-read command's, so `row_select_from_read_frame` builds it by
reusing a live rebound read frame's header+nonce+path and swapping the read action (`88 81 81 e0 4b 55 …`) for the
row-select suffix (`88 81 81 e1 81 81 82 … c0 4b 53 <col> eb 53 <value>`). Byte-shape is correct + unit-tested.

**⚠ NEGATIVE live result — the form-table command does NOT splice onto a live DYNLIST.** Injecting the synthesized
row-select before the reads (Товары, WHERE Наименование=«Молоко») left the current row UNCHANGED — the reads still
returned row 1 («Обувь»/«000000001»), not «Молоко»/«000000026». So a dynlist row-select is a distinct surface from
the form-table one (the dynlist is server-backed; «перехожу к строке» likely drives a server-side find, not the
client-side table-find the form-table command does). The `where_column/where_value` wiring was therefore REVERTED
(not shipped — a param that silently returns the wrong row is worse than none); `read_list_row` reads the FIRST row
only. `row_select_from_read_frame` + the `ROW_SELECT_*` constants are KEPT (correct decode, unit-tested) for the
follow-up. ⭐ NEXT for multi-row: a genuine DYNLIST row-navigation capture (boot the Vanessa manager →
«открываю … список Товары» + «перехожу к строке Наименование=Молоко» / «перехожу к следующей строке» → read →
decode) — the proven recipe; then wire it into `read_list_row` (row-by-value) and add a «next row» iterator.

## Artifacts

- Capture: `runtime/protocol-research/captures/genuine-card98-tableread/` (feature
  `tools/protocol-research/qa-card98-capture-tableread.feature`).
- Decode: chunks [73] (command) / [74] (response). Code: `src/qa_mcp/protocol/native_write.py`
  (`splice_table_cell_read` + `TABLE_READ_*`). Test: `tests/test_form_descriptor.py`
  (`test_splice_table_cell_read_matches_genuine_shape`). Probe: `tools/protocol-research/table_cell_read_probe.py`.
- ⭐ NEXT: establish a current row (row-select/activate splice, or read after load) → end-to-end value; then the
  `read_table_cell`/`read_list_column` MCP tool. This also closes the non-empty navigated value-read.
