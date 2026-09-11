## Why

On the demo10413 `Catalog.ДоговорыКонтрагентов` create form, writing «30.06.2026» into «Дата договора»
through the open-link route OPENS the calendar picker (navigated to 30 Jun 2026) and leaves the field
empty — no commit (confirmed live 2026-06-30; evidence
`.artifacts/openspec/card125-runtime-blocker-live-recheck/20260630T180336Z/`, shots `07-REAL-FORM-*`,
`09-real-form-date-empty-not-committed`). Without `ДатаДоговора` the object-module auto-name handler
(`Если ЗначениеЗаполнено(ДатаДоговора) И ЗначениеЗаполнено(НомерДоговора)`) never builds `Наименование`.

The date field itself is not the problem: typing DD.MM.YYYY digits directly into the focused field
commits cleanly (proven live on the `РегистрСведений.КурсыВалют` «Период» field — typed 15.03.2025 +
Tab read back committed; shots `05`,`06`). The failure is how the tool drives the field: its
locate + `input_offset` click lands on/near the field's calendar button and/or typing the dotted
date triggers the dropdown calendar instead of an inline commit.

## What Changes

- Drive `ДатаДоговора` so `DD.MM.YYYY` commits on an open-link create form: masked-input digit typing
  into the field's text input (avoiding the calendar button) or a deterministic calendar pick.
- Verify the date by read-back (field is the typed value, calendar not left open).
- Integrate with `write_form_fields_by_label` and `write_form_date(open_link=…)`.

## Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: add requirements that a date value commits on an open-link create form
  (read-back verified) and that the date write does not get stuck on the calendar picker.

## Impact

- Python manager: `src/qa_mcp/mcp_server.py` (`write_form_date` open-link route, the shared label
  writer); click-geometry shares the fix from `native-write-locate-short-reference-label`.
- Depends on `native-write-locate-short-reference-label` (the click lands on the calendar button —
  the input-column click-geometry fix is the shared root cause).
- Offline test for the date-input path; live demo10413 confirmation that «Дата договора» reads back
  committed on the real create form.
- Live 1C runtime for the demo10413 leg only; otherwise offline.
