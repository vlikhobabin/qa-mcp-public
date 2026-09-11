# Card 97 change 3 — report / ТабличныйДокумент: run + the spreadsheet-read boundary

**Date:** 2026-06-19. **Scope:** run a report (fill a ТабличныйДокумент) + read the resulting spreadsheet,
capture-free, no Vanessa. **Outcome:** the report-RUN is productized & live-verified; reading individual
spreadsheet CELLS capture-free is an honest boundary (the .mxl rides the wire as a 1C-packed binary blob).

## Fixture extension (deploy)

Added to the fixture form (the embedded DataProcessor `ФикстураПротоколаTestClient`):
- a form attribute `PF_REPORT` of type **SpreadsheetDocument** + a `SpreadsheetDocumentField` to display it;
- a command `PF_RUN_REPORT` + its command-bar button + a Module.bsl handler that fills PF_REPORT **on the
  server** (cells `PF_RPT_R1C1` / `R1C2` / `R2C1` / `R2C2`) and sets `PF_LAST_ACTION = "PF_RUN_REPORT"`.
Deployed via `deploy_fixture.sh` (`TAG=card97-ch3`): gen `08d5aabf…` → **`38bc7fac8858…`**. Backups
`Form.form.bak-card97-ch3-report` / `Module.bsl.bak-card97-ch3-report`. ⚠️ The first export hit a TRANSIENT EDT
glitch (`IllegalArgumentException … Constant … feature "type"`) that truncated an UNRELATED CommonForm's export
→ import failed, gen unchanged (no harm); a **retry exported cleanly** and deployed. (My fixture XML validated
well-formed throughout — the glitch was EDT-side, not the edit.)

## Report-RUN ✅ — `run_report` (MCP #37), capture-free + live-verified

A report-run is a standard FORM-COMMAND click — the `click_command` family (`…Button[PF_RUN_REPORT] 88 82 81 20
20 20`). `run_report(command="PF_RUN_REPORT")` derives the command-click from the genuine capture
(`genuine-card97-ch3-report-20260619`, a connect+open+click) and replays it. Live-verified by screenshot
(`runtime/protocol-research/report-shot/20260619-114256/run_report.png`): **PF_LAST_ACTION = "PF_RUN_REPORT"**
+ PF_ACTION_COUNTER = 1 + the spreadsheet-field toolbar (save/print/preview) present — the report command fired
and filled the spreadsheet server-side, no Vanessa. The cell content was confirmed via the in-client read
(`get_form_analysis`): `табличный документ 'PF_REPORT' равен: | PF_RPT_R1C1 | PF_RPT_R1C2 | / | PF_RPT_R2C1 |
PF_RPT_R2C2 |`.

## Spreadsheet CELL-READ — honest boundary: the .mxl is a 1C-packed BINARY blob on the wire

The cell text does NOT ride the wire as readable strings. Verified across three captures (the click response;
a cached read sweep; a FRESH-client FIRST read after the fill — 290 KB client→manager):
- the cell text `PF_RPT_R1C1` / fragments `RPT` / `R1C1` are **absent in BOTH directions, in UTF-16LE and
  UTF-8**;
- **no zlib (`78 9c`/`78 da`) and no raw-deflate** stream inflates to the marker (naive offset scan);
- only the field PATH `EditField[PF_REPORT]` appears (its scalar "value" is just the field name) — the
  spreadsheet content travels as a separate 1C-packed binary `ТабличныйДокумент` (.mxl) blob (a large
  high-entropy frame), with the cell text encoded inside it in a non-plain form.

## ⭐ CELL-READ RESOLVED — it is an in-client TARGETED read, NOT a .mxl wire-decode (2026-06-19, follow-up)

The full form-read (`get_form_analysis`) carrying a binary blob was a **red herring** — that is the form-RENDER
path, and it does NOT carry the cell text (only a 20-byte handle for the spreadsheet field). A **TARGETED cell
read** is a small **in-client** operation, and it rides the protocol as PLAIN strings we already decode.
Captured (`genuine-card97-ch3-cellread-20260619`): connect+open → PF_RUN_REPORT → «в табличном документе
"PF_REPORT" я перехожу к ячейке "R1C1"» → «я запоминаю значение текущей ячейки … в переменную "CELL11"» →
**CELL11 = "PF_RPT_R1C1"** (the client read the live ТабличныйДокумент object). The whole exchange is **6.5 KB**
(vs 290 KB for get_form_analysis). On the wire:
- **navigate-to-cell** (manager→client): `…EditField[PF_REPORT] 88 82 81  fa 04 "R1C1"  20 20 20` — the cell
  ADDRESS as a plain UTF-8 string (`fa <len> <addr>`), re-targetable like any value.
- **read-current-cell** (client→manager): `…EditField[PF_REPORT] 81 81 81 e1  9a 0b "PF_RPT_R1C1"` — the cell
  VALUE as a plain length-prefixed string (`9a <len> <utf-8>`) — **the exact shape the card-79 value-read
  decodes.**

⇒ **option (b) confirmed:** the cell content is read IN THE CLIENT (a 1C method on the live object) and returned
as a small plain value; the binary form-render blob never carries the cells. ⇒ **the .mxl boundary is LIFTED —
no binary decode needed.** (This matches the architecture: we drive a test CLIENT and read cells by an in-client
method — we never needed the manager-side .mxl deserialization.)

### ✅ PRODUCTIZED + LIVE-VERIFIED — `read_spreadsheet_cell` (MCP #38)

`protocol/native_write.py`: `ReadSpreadsheetCellTemplate` + `derive_read_spreadsheet_cell` + `read_spreadsheet_cell`
+ `retarget_cell_address`. Replays the genuine flow (open form → run_report → navigate-to-cell) with the navigate
ADDRESS re-targeted (`\xfa<len><utf-8>`, same-length R1C1 notation) and the value parsed from the client response
by the card-79 `read_field_value_near` (the cell value rides the SAME `\x9a<len><utf-8>` shape — the navigate ACKs
use a `\x81\x82\x81` counter so the parser correctly anchors on the `\x81\x81\x81` value response). MCP tool
`read_spreadsheet_cell(address, field="PF_REPORT", …)` — the **38th** tool. **Live-verified PASS 4/4** on fresh
native clients: `R1C1→PF_RPT_R1C1`, `R1C2→PF_RPT_R1C2`, `R2C1→PF_RPT_R2C1`, `R2C2→PF_RPT_R2C2`
(`read_spreadsheet_cell_verify.py`). 2 unit tests (261 suite). Capture `genuine-card97-ch3-cellread-20260619`,
feature `qa-card97-ch3-cellread.feature`. The report verification is ALSO available via the readable
`PF_LAST_ACTION` marker + the screenshot.

### Address length — VARIABLE-length works (via frame RESIZE, not padding)

`retarget_cell_address` re-targets ANY-length R1C1 address — the navigate command is
`…EditField[PF_REPORT] 88 82 81  fa <len><addr>  20 20 20  <nonce>`, and the `20 20 20` is a **fixed 3-space
structural suffix, NOT padding**. Decisive experiment (`cell_resize_experiment.py`, 12×12-grid fixture, gen
`38bc7fac…`→`d8a70b86…`): a longer address by **consuming** the spaces is silently ignored (the navigate no-ops,
the cell stays at R1C1) — but a longer address by **RESIZING** the frame (keep the 3 spaces, grow by the
address-length delta) navigates correctly. Unlike a value-SET frame (which desyncs on resize — card 80), the
navigate frame TOLERATES resize. So `retarget_cell_address` just swaps the `\xfa<len><addr>` block and lets the
frame grow/shrink — **arbitrary-length addresses, no budget**. Live-verified PASS 4/4 on the 12×12 grid:
`R1C1→PF_RPT_R1C1` (4-char), `R1C12→PF_RPT_R1C12` / `R12C1→PF_RPT_R12C1` (5-char), `R12C12→PF_RPT_R12C12`
(6-char). (The earlier "same-length only" note was a wrong first guess — padding-consume failed; resize is the
real answer.)

## Tools / evidence

- `run_report` MCP tool (#37) — reuses `derive_command_click` + `click_command`. No new unit test (click_command
  is already covered); 259 suite unchanged. Probe `run_report_verify_shot.py`. Decoder `card97_report_decode.py`.
- Capture feature `qa-card97-ch3-report.feature`. Captures: `genuine-card97-ch3-report-20260619` (click) +
  `…-firstread-20260619` (the fresh-client first read used to rule out plain/zlib cell text).
- Fixture edits: `Forms/Форма/Form.form` (PF_REPORT attribute + SpreadsheetDocumentField + PF_RUN_REPORT command
  + button) + `Module.bsl` (PF_RUN_REPORT client+server handlers; PF_REPORT cleared in СброситьСостояниеФикстуры).
