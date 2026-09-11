## Why

On the real demo10413 `Catalog.ДоговорыКонтрагентов` create form, `write_form_fields_by_label`
cannot drive the short owner label «Владелец»: `locate_text` reports `"label not located"`
while the longer labels «Номер договора» / «Дата договора» locate fine (confirmed live
2026-06-30, evidence `.artifacts/openspec/card125-runtime-blocker-live-recheck/20260630T180336Z/`,
shot `07-REAL-FORM-*`). Two distinct short-label failure modes were observed:

- **Not located.** `locate_text` (`src/qa_mcp/protocol/native_xtest.py:252`) is not OCR — it renders
  the label as a Liberation-Sans 13pt needle and runs ImageMagick `compare -subimage-search` with
  `max_score=0.2` (normalized RMSE). The «Владелец:» needle exceeds the threshold versus the
  on-screen render; multi-word labels pass. The failure is glyph/render-sensitive, not monotonic in
  length (the 3-char «Код» on the Валюты form *did* locate).
- **Located but mis-clicked + falsely reported OK.** Where a short label *is* located (e.g. «Код» on
  the Валюты create form), the fixed `input_offset=170` from the label CENTER lands left of the
  right-aligned input column (aligned to the longest label), so the value is typed into whatever
  field had focus — it landed in «Наименование основной валюты», «Код» stayed empty — yet the tool
  returned `targeted:true, all_selected:true` (a false-positive verification).

So short/single-word/reference labels cannot be written reliably from the UI, and a caller cannot
trust the success flags.

## What Changes

- Make `locate_text` tolerant for short/single-word/reference needles (e.g. per-length scale/threshold
  tuning, multi-pointsize attempts, or an OCR fallback when subimage RMSE > `max_score`), and expose
  the chosen knobs from `write_form_fields_by_label`.
- Make the click target reach the input column for short labels — derive the click point from the
  field box (snap into the input), not a fixed pixel offset from the label center.
- Make verification honest: a write reports success only when the value is actually present in the
  TARGETED field (read-back / screenshot crop of the field), not merely that some value was located
  somewhere on screen.

## Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: add requirements for short/single-word/reference label localization, for
  click-offset geometry that reaches the right-aligned input column, and for honest write
  verification (no false-positive `targeted`/`all_selected`).

## Impact

- Protocol tools: `src/qa_mcp/protocol/native_xtest.py` (`locate_text`, click-point derivation).
- Python manager: `src/qa_mcp/mcp_server.py` (`write_form_fields_by_label` and the shared open-link
  label-writer used by `write_form_date` / `write_form_value`).
- Requires offline tests (a short-label needle the current default would miss; an offset/geometry
  case) plus live demo10413 verification on the `ДоговорыКонтрагентов` create form.
- Live 1C runtime required for the demo10413 leg (TestClient + display backend); offline ImageMagick
  for the localization unit tests. No Vanessa/EDT/meta snapshots needed.
