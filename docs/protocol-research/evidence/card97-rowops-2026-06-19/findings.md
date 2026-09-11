# Card 97 change 1 — table row operations (delete / move up-down / copy) — SHIPPED capture-free

**Date:** 2026-06-19. **Result:** the three remaining table row operations are productized capture-free (no
Vanessa): `delete_table_row`, `move_table_row(direction)`, `copy_table_row` (MCP tools #28–#30; 30 tools, 241
tests). Multi-row select is the only row-op item deferred (see below).

## What shipped

| MCP tool | Fixture command | Effect (live-proven 2026-06-19) |
| --- | --- | --- |
| `delete_table_row` | `PF_DELETE_ROW` (`ДанныеФормыКоллекция.Удалить`) | baseline `[001\|002\|003]` active row 1 → `PF_TABLE[2]=PF_ROW_002\|PF_ROW_003` |
| `move_table_row("down")` | `PF_MOVE_ROW_DOWN` (`Сдвинуть(+1)`) | → `PF_TABLE[3]=PF_ROW_002\|PF_ROW_001\|PF_ROW_003` |
| `move_table_row("up")` | `PF_MOVE_ROW_UP` (`Сдвинуть(-1)`) | active row 1 = top → no move; `PF_LAST_ACTION=PF_MOVE_ROW_UP` proves fire |
| `copy_table_row` | `PF_COPY_ROW` (`Вставить` a copy `_COPY`) | → `PF_TABLE[4]=PF_ROW_001\|PF_ROW_001_COPY\|PF_ROW_002\|PF_ROW_003` |

## Fixture extension (deployed, generation b5802e…)

`ФикстураПротоколаTestClient` (`Module.bsl` + `Form.form`, append-only so existing element ids stay stable):
- **Read-back marker `PF_TABLE_SNAPSHOT`** (new form attr + read-only field) = `PF_TABLE[<count>]=<marker>|<marker>…`,
  recomputed in `PF_ПересчитатьСнимокТаблицы[НаСервере]` on every table mutation + `OnActivateRow` + reset.
- **Custom commands** `PF_DELETE_ROW` / `PF_MOVE_ROW_UP` / `PF_MOVE_ROW_DOWN` / `PF_COPY_ROW` (+ buttons in
  `PF_COMMAND_BAR_MAIN`), mirroring the proven `PF_ADD_ROW`. They act on the ACTIVE row (id from
  `Элементы.PF_TABLE_ITEMS.ТекущаяСтрока` → `НайтиПоИдентификатору`). API verified via help-mcp:
  `Сдвинуть(<Индекс>,<Количество>)`, `Удалить(<Индекс>)`, `Вставить(<Индекс>)`.

## Decode (the key findings)

- A row-op command click is the SAME form-command invoke as `PF_ADD_ROW`:
  `…Group[PF_COMMAND_BAR_MAIN].Button[<CMD>]` with tail **`88 82 81 20 20 20`** (the window-command family from
  card 96 close/activate — NOT the `88 81 81 e1` seen on the get_form_analysis re-render).
- All four buttons are byte-identical apart from the name, so they replay from ONE genuine capture by
  retargeting the `Button` leaf (`retarget_element_leaf` is length-aware → `PF_COPY_ROW`(11) →
  `PF_MOVE_ROW_DOWN`(15) recomputes the path-length prefix). This is exactly `click_command`'s `target_button`.
- **Capture-must-be connect+open+click**, NOT action-only: an action-only capture's setup is mid-session polls,
  not a form-open, so it can't be replayed against a fresh client. **And NO trailing `get_form_analysis`** in the
  capture window — its form-structure dump re-emits every `Button[NAME]` (in layout order, `88 81 81 e1`), which
  pollutes `_find_command_click`'s "last run = click" rule. The shipped capture is connect+open + the 4 clicks;
  the FIRST click (`PF_COPY_ROW`) carries the form-open setup, and all tools derive from it + retarget.

## How the tools work

`derive_command_click(capture, "PF_COPY_ROW")` (setup = full form-open) → `click_command(template,
target_button=<CMD>)`. A click has no value read-back and the effect is **session-local form state** (reset on a
fresh form-open), so verify in the SAME session via `read_form_value('PF_TABLE_SNAPSHOT')` /
`('PF_LAST_ACTION')` or `capture_screenshot`. To target a specific row, `select_table_row` first.

## Artifacts

- Capture (replay template): `runtime/protocol-research/captures/genuine-card97-rowops-combined-20260619/traffic-selfcontained/`
  (connect+open+COPY/MOVE_DOWN/MOVE_UP/DELETE; client 48002, mgr port 45576 isolated). Decode-only clean capture:
  `genuine-card97-rowops-clean-20260619`.
- Features: `tools/protocol-research/qa-card97-connect-open-rowops.feature` (+ `…-connect-open` / `…-capture-rowops`).
- Live-verify: `tools/protocol-research/rowops_verify_shot.py` → screenshots in
  `runtime/protocol-research/rowops-shot/20260619-035928/` (PF_DELETE_ROW.png / PF_MOVE_ROW_DOWN.png / etc.).
- Code: `src/qa_mcp/mcp_server.py` (delete_table_row/move_table_row/copy_table_row); reuses
  `derive_command_click`/`click_command` (native_write.py). Tests: `tests/test_native_write.py`
  (`test_rowops_derive_first_click_carries_form_open_setup`, `test_rowops_retarget_copy_to_longer_command_is_length_aware`).

## Deferred (card 97 change 1 remainder)

- **Multi-row select** — selection state (`Элементы.PF_TABLE_ITEMS.ВыделенныеСтроки`), not a single command;
  needs its own decode + a `ВыделенныеСтроки`-count read-back. Pull when a real scenario needs multi-select.
