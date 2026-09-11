# Card 97 change 1 — multi-row select — DECODED (protocol) + command productized + read-back boundary

**Date:** 2026-06-19. **Result:** multi-row select is **protocol-drivable** (not OS-level): the genuine Vanessa
"выделяю все строки" step is a TABLE-level command invoke, productized as `select_all_table_rows` (MCP #31; 31
tools, 242 tests). A genuine read-back boundary was found and is documented honestly below. This closes card 97
change 1 (table row operations).

## Decode (the key finding)

`search_for_steps_by_keywords` shows Vanessa has a rich `UI.Таблицы.Выделение строк` family:
`ВТаблицеЯВыделяюВсеСтроки` (select all), `ВТаблицеЯВыделяюВсеСтрокиВыше/НижеТекущей` (Shift),
`ВТаблицеЯПерехожуКСтрокеСПереключениемВыделения` (Ctrl-toggle arbitrary rows), deselect-all, and the read step
`ЯЗапоминаюВыделенныеСтрокиТаблицыКак`.

Captured genuine "выделяю все строки" twice (connect+open+select-all). It is a **protocol command**, NOT OS
input: `…ManagedForm[…].Table[PF_TABLE_ITEMS]` with tail **`88 82 81 20 20 20`** — the SAME command-invoke
family as the row-op buttons (card 97 #1) and the card-96 window close/activate commands, but addressed at the
**Table element** itself (not a `Button`). So it replays via the same machinery: `derive_table_command(capture,
"PF_TABLE_ITEMS")` finds the `Table[…]` invoke (setup = form-open) and `click_command(template, None)` replays
it with no leaf retarget. `_find_command_click` was generalized to `_find_element_command(mgr, leaf)` (any leaf).

## What shipped

| MCP tool | Mechanism | Status |
| --- | --- | --- |
| `select_all_table_rows` | replay setup + the `Table[PF_TABLE_ITEMS] 88 82 81` select-all invoke | fires (accepted=True live) |

Fixture extended (deployed, gen c94ebf…): `PF_SELECTED_ROWS` read-back marker
(`PF_SEL[<count>]=<marker>,…`, computed in `PF_ПересчитатьСнимокТаблицы` from
`Элементы.PF_TABLE_ITEMS.ВыделенныеСтроки`) + a `PF_REFRESH_SELECTION` command to materialize it.

## ⚠️ Read-back boundary (honest finding)

The resulting multi-selection is **TRANSIENT table-focus UI state**. Reading it back capture-free is blocked by
standard 1C behaviour, NOT by a replay defect:

- After `select_all_table_rows` (or the genuine step), clicking `PF_REFRESH_SELECTION` to materialize
  `PF_SELECTED_ROWS` reads **`PF_SEL[1]=PF_ROW_001`** (only the active row) — because clicking a command button
  moves focus off the table, and 1C collapses `ВыделенныеСтроки` to the active row.
- **Decisive control:** the GENUINE Vanessa flow (manager-driven `выделяю все строки` + `PF_REFRESH_SELECTION` +
  `get_form_analysis`) reads the SAME `PF_SEL[1]=PF_ROW_001`. Genuine == replay ⇒ this is 1C's transient-focus
  semantics, not a capture-free engine limitation.
- `select-all` does not change the active row, so the row-activation hook (`OnActivateRow` →
  `PF_ПересчитатьСнимокТаблицы`) never recomputes the marker with the multi-selection either.

Implication: a LIVE multi-selection is not capture-free-readable across separate commands. The only
non-collapsing read is the in-session testing API `ТестируемаяТаблицаФормы.ПолучитьВыделенныеСтроки` — Vanessa's
domain (one persistent session). Composing select-then-act multi-row operations capture-free therefore requires
capturing the WHOLE flow in one session (the selection + the dependent action together), not chaining two
separate per-command replays. The select-all COMMAND itself is protocol and replays; that is what's shipped.

## Artifacts

- Captures: `runtime/protocol-research/captures/genuine-card97-multiselect-20260619` (investigation),
  `genuine-card97-multiselect-capture-20260619/traffic-selfcontained/` (productize template:
  connect+open+select-all+refresh; client 48001, mgr port isolated).
- Features: `tools/protocol-research/qa-card97-multiselect-{probe,capture}.feature`.
- Live-verify: `tools/protocol-research/multiselect_verify_shot.py` → `runtime/protocol-research/multiselect-shot/`
  (full-replay + tool shots; both confirm the command fires and the `PF_SEL[1]` read-back boundary).
- Code: `derive_table_command` / `_find_element_command` (native_write.py), `select_all_table_rows`
  (mcp_server.py). Test: `tests/test_native_write.py::test_derive_table_command_locates_table_level_invoke`.

## Deferred (same Table-command family, on demand)

- Arbitrary multi-select via Ctrl-toggle (`ВТаблицеЯПерехожуКСтрокеСПереключениемВыделения`) and deselect-all —
  decode identically; only useful with the same-session composition above.
