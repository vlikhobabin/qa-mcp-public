## Context

`write_form_date(open_link=…)` uses the config-agnostic foreground label writer: it locates the date
label, clicks `input_offset` px right, and types the date. On the demo10413 `ДоговорыКонтрагентов`
create form this OPENS the calendar (the click lands on/near the date field's calendar button and/or
typing the dotted date triggers the dropdown) and the field is left empty (live 2026-06-30, shots
`07`, `09`).

The date field commits fine when digits are typed directly into the focused field: on the
`РегистрСведений.КурсыВалют` «Период» field, typing `15032025` + Tab read back `15.03.2025` and made
the form dirty (shots `05`, `06`). So the fix is in the drive, not the field.

## Goals / Non-Goals

**Goals:**
- Commit `DD.MM.YYYY` into a date field on an open-link create form, verified by read-back.
- Avoid the calendar-button trap.

**Non-Goals:**
- Grid date-cell writing (`set_table_date_cell` is separate).
- General label localization mechanics (covered by `native-write-locate-short-reference-label`).

## Decisions

- Prefer masked-input digit typing into the field's text input (the КурсыВалют-proven path:
  digits into the focused field, then Tab to commit), reusing the input-column click-geometry from
  `native-write-locate-short-reference-label` so the click hits the input, not the calendar button.
- If digit typing is not viable for a field, fall back to a deterministic calendar pick (navigate to
  the target Y/M, click the day) — but the default is inline typing.
- Verify by reading the field back (descriptor value read) and confirming the calendar is closed.

## Risks / Trade-offs

- Locale/format: the field expects DD.MM.YYYY; normalize/validate before typing (reuse
  `_normalize_form_date`).
- Date+time fields (e.g. «Период») show a date but hold a datetime; assert on the date prefix.
- Depends on the click-geometry fix landing first; otherwise the click keeps hitting the calendar
  button.
- Safety: the demo10413 confirmation opens the create form and reads back; the full save proof lives
  in `native-write-demo10413-real-proof` with snapshot-based rollback.
