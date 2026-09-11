## Context

`write_form_fields_by_label` (`src/qa_mcp/mcp_server.py:1670`) localizes each label by
`locate_text(shot, f"{label}:")` (`:1745`) and then clicks `input_offset` px to the right of the
label center, types Unicode-safe, Tabs, and "verifies" by re-locating the typed value on screen.

`locate_text` (`src/qa_mcp/protocol/native_xtest.py:252`) is **not OCR**: it renders the label as a
`Liberation-Sans` 13pt needle (`imagemagick_label_argv`) and runs `compare -subimage-search`
(`imagemagick_compare_argv`), accepting the match only when normalized RMSE ≤ `max_score` (0.2).

Live evidence (2026-06-30, `.artifacts/openspec/card125-runtime-blocker-live-recheck/20260630T180336Z/`):

- On the real `ДоговорыКонтрагентов` create form, «Владелец» → `"label not located"` while
  «Номер договора»/«Дата договора» locate (shot `07-REAL-FORM-*`). The needle for the short label
  exceeds the RMSE threshold; the failure is glyph/render-specific (the 3-char «Код» on Валюты *did*
  locate, so it is not a simple length rule).
- On the Валюты create form, «Код» located (`targeted:true`) but its value landed in
  «Наименование основной валюты»: the click at `label_center_x + 170` (≈x436) fell left of the input
  column (≈x472, aligned to the longest label). The tool still returned
  `targeted:true, all_selected:true` — a false-positive verification (shots `03`, `02`).

## Goals / Non-Goals

**Goals:**
- Locate short/single-word/reference labels («Владелец», «Код», «Основной») on a live create form.
- Click into the field's input box for short labels so the value lands in the intended field.
- Report write success only when the value is verified in the targeted field.

**Non-Goals:**
- Removing the «Владелец»→«Контрагент» alias (that is `native-write-owner-label-from-live-form`).
- Date-field commit behaviour (that is `native-write-open-link-date-commit`).
- Re-architecting `locate_text` into a general OCR engine; an OCR *fallback* is acceptable but the
  fast subimage path remains the default.

## Decisions

- **Localization fallback:** when `compare -subimage-search` RMSE > `max_score`, retry with a small
  set of point sizes / a scale sweep, and as a last resort an OCR fallback (e.g. tesseract) scoped to
  the label band. Keep the fast subimage path as the default; expose the chosen knob in the result.
- **Click geometry:** derive the click point from the located label's box plus the on-screen input
  box rather than a fixed `input_offset` from the label center — snap into the input column so a
  short label and a long label both land in their own input. `input_offset` stays as an override.
- **Honest verification:** verify by reading the targeted field back (descriptor value read) or a
  field-scoped screenshot crop of the value, and set `targeted`/`all_selected` from that, not from a
  global on-screen value search.

## Residuals

- **Click geometry for far-right-aligned columns.** The default `input_offset` reaches the input for
  the owner label «Владелец» on the demo10413 create form (live-proven — «Корнет ЗАО» lands). A very
  short label whose input column is right-aligned to a much longer sibling (e.g. «Код» beside
  «Наименование разменной валюты» on the Валюты form) can still under-reach the column; a two-pass
  input-column derivation is a follow-up, out of this change's proven scope.
- **Read-back verification.** Per-field text/date commit is not read back inside the writer (marked
  `verification: screen_targeted`); authoritative commit verification is the post-save read-back in
  `native-write-demo10413-real-proof`.

## Risks / Trade-offs

- OCR fallback adds a dependency and latency; gate it behind the RMSE-miss path only and document it.
- Snapping to the input box needs the field box; where only the label is known, fall back to a
  bounded offset and report which path was used.
- Safety: tests open create forms only; `save=false`; no records are persisted. Live runs use the
  demo10413 TestClient with a clean-state Escape sweep and leave no junk (verified by DB-size /
  cmp checks in the proof change).
