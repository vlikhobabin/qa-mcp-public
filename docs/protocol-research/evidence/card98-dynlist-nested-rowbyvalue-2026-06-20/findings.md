# Card 98 follow-ups — DYNLIST nested-row read (flat view) + go-to-row BY VALUE (2026-06-20)

Two dynlist read follow-ups from the capture-free epic handoff, both SOLVED + PRODUCTIZED + live-verified on a
real catalog list form (vanessa_client `Справочник.Товары`), no Vanessa.

## 1. Nested rows — `read_list_grid(flat=True)`

**Problem.** `read_list_grid` walks the list's CURRENT view. Товары is a HIERARCHICAL catalog (36 items: 4
top-level folders Обувь/Продукты/Услуги/Электротовары, 32 nested), so the default grouped view exposes only the
4 top-level folders — the baseline read returned exactly those 4. The nested items were invisible.

**Why `set_list_view` could not compose.** `set_list_view` replays the FIXTURE capture
(`genuine-card97-ch4-viewmode`) — it opens the fixture DataProcessor form and clicks the fixture dynlist's
view buttons. It never opens the Товары list, and a piecemeal splice of a view-switch onto a live dynlist does
not reproduce the interaction-ready state (the same reason the dynlist READ needed a faithful full-sequence
replay). So composing two separate MCP calls cannot flatten the Товары view.

**Solution — bake the view-switch into the capture.** Captured a genuine flat-view next-row sequence on Товары
via the Vanessa manager (`genuine-card98-nextrow-flat`): open the list → click «Список» (the standard catalog-
list-form view-mode command, **named `ФормаСписок`** — NOT `СписокСписок`; recon via `get_form_analysis` showed
the «Режим просмотра» group has `ФормаИерархическийСписок` / `ФормаСписок` / `ФормаДерево`) → first row → read →
next-row → read → next-row → read. The view-switch lands at mgr frames 20-21, BEFORE the first read (frame 29),
so `read_list_grid_replay`'s cold full-replay "through the first read" already replays the flatten — **zero
engine change**; the capture drops in. `read_list_grid(flat=True)` selects `genuine-card98-nextrow-flat`.

**Live (cold, vanessa_client Товары, max_rows=12):** 12 NESTED rows, codes vs OData ground truth —
Bosch1234/000000017, Bosch15/000000018, Sony К3456P/000000040, Veko345MO/000000028, Veko67NE/000000022,
Veko876N/000000034, VekoNT02/000000033, Босоножки/000000031, Ботинки/000000006, Валенки/000000020,
Вихрь/000000015, Доставка/000000037 — all in subgroups (Чайники/Телевизоры/Пылесосы/Обувь/Услуги), all
invisible in the hierarchical baseline. Flat view sorts by Наименование.

## 2. Go-to-row BY VALUE — `read_list_row(where={column: value})`

**Problem.** `read_list_row` read only the FIRST row. The FORM-table «перехожу к строке» command
(`row_select_from_read_frame`, decoded from `genuine-card90-rowaddr`) does NOT splice onto a live dynlist — it
still read row 1 (documented NEGATIVE). A genuine DYNLIST «перехожу к строке» capture was the missing piece.

**Solution — genuine dynlist row-by-value capture + full-sequence replay.** Captured
`genuine-card98-rowbyvalue` on Товары (flat view → «перехожу к строке Наименование=Сапоги» → read Код → «…=Туфли»
→ read Код). Decode-by-diff (Сапоги 6 chars / 403 B vs Туфли 5 chars / 401 B) isolates the structure: the
go-to-row command is `…Table[Список] 88 81 81 e1 81 81 82 cb 23 95 <16B action GUID> c0 4b 53 <WHERE column>
eb 53 <match value> …` — the SAME `c0 4b 53 <col> eb 53 <value>` shape `row_select_from_read_frame` decoded from
the form table, confirming the byte structure was right all along; the splice failed only because a dynlist needs
the full-sequence replay, not a graft. `read_list_row_by_value_replay` replays the genuine stream cold through
the open + flat-view + first go-to-row + read, with the match value (`eb 53 <block>`) retargeted, the WHERE
column (`c0 4b 53 <block>`) and read column retargeted, GuidRebinder rebinding session GUIDs; extra read columns
ride the same socket (message-id kept, sequence bumped).

**Live (cold, vanessa_client Товары):**
- `where={Наименование: Молоко}` (6 chars, = captured length) → {Наименование: Молоко, Код: 000000026} ✓
- `where={Наименование: Кроссовки}` (9 chars, ≠ captured length) → {Наименование: Кроссовки, Код: 000000024} ✓
  (confirms the go-to-row command tolerates the value resize — variable-length match values work).

Reads the read code (000000002 Сапоги / 000000003 Туфли in the capture) all match OData.

## Surface

- `read_list_grid(open_link, columns, max_rows, flat=False)` — `flat=True` reads nested items (the flat view).
- `read_list_row(open_link, columns, where={column: value} | None)` — `where` positions to the row by value;
  omit it for the first row. Matching by «Наименование» is the verified path.
- Engine: `read_list_row_by_value_replay` (native_write.py); `read_list_grid_replay` unchanged (flat capture
  drops in). 4 new unit tests (capture-shape + two MCP-tool-shape + the where-multikey guard); 340 tests.

## Captures / features / probes

- `runtime/protocol-research/captures/genuine-card98-nextrow-flat` (40/41 chunks),
  `…/genuine-card98-rowbyvalue` (32/33 chunks).
- Features: `tools/protocol-research/qa-card98-capture-{nextrow-flat,rowbyvalue,recon-listform}.feature`.
- Probes: `tools/protocol-research/dynlist_{flat_grid,rowbyvalue}_probe.py`,
  `nested_rows_baseline_probe.py`.

## Cold-client boundary (unchanged)

One dynlist read per fresh `launch_test_client` (per CLIENT PROCESS). `read_list_grid` iterates many rows inside
the one materialised session; `read_list_row` reads all requested columns of the one positioned row inside it.

## Recipe notes (this capture)

- Recon the view-mode command names with `get_form_analysis` BEFORE the capture — a standard catalog list form
  names them `Форма<Mode>`, not `<dynlist><Mode>` (the fixture's `ДенамическийСписокИерархия<Mode>` is fixture-
  specific). Caught a wrong button name offline.
- Window each feature in its own tcpdump capture and use a FRESH client name per capture (forces a new connect/
  bootstrap in the pcap; idle prior clients still emit keepalives → isolate by client TPort + dominant manager
  ephemeral port). Client TPort = the SYN destination; manager port = the heaviest ephemeral connection to it.
