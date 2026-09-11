## ADDED Requirements

### Requirement: Short and single-word form labels are reliably localized

`locate_text`-backed label targeting SHALL locate short, single-word and reference field labels
(for example «Владелец», «Код», «Основной») on a live managed-form create surface, not only longer
multi-word labels. When the default subimage-search needle does not pass the confidence threshold,
the localizer SHALL apply a documented fallback (for example scale/threshold tuning per label length,
multiple point sizes, or an OCR fallback) before reporting the label as not located.

#### Scenario: Short owner label is located on the live create form

- **WHEN** `write_form_fields_by_label` targets the «Владелец» label on the demo10413
  `Catalog.ДоговорыКонтрагентов` create form
- **THEN** the label is located and reported `targeted: true`
- **AND** the longer labels «Номер договора» and «Дата договора» on the same form also locate
- **AND** retained evidence references the live screenshot for the run

#### Scenario: Offline short-label needle the prior default would miss

- **WHEN** an offline localization test renders a short single-word needle that the previous
  `max_score=0.2` single-pointsize search would reject
- **THEN** the hardened localizer locates it via its documented fallback
- **AND** the test records the chosen knob (scale, point size or OCR path)

### Requirement: Located reference/short-label writes reach their input field

When a reference/owner or short label is located on a live create form, the write SHALL reach that
field's input so the typed value lands in the intended field. (Known residual, tracked in design: a
very short label whose input column is right-aligned to a much longer sibling — e.g. «Код» beside
«Наименование разменной валюты» — can still under-reach the column with the default offset.)

#### Scenario: Owner reference value reaches its field on the live create form

- **WHEN** the owner label «Владелец» is written on the demo10413 `Catalog.ДоговорыКонтрагентов`
  create form
- **THEN** the reference value «Корнет ЗАО» lands in the «Владелец» field and is reported
  `selected: true`

### Requirement: Form-write results label their verification honestly

A field write SHALL report its verification level rather than implying a read-back it did not perform.
Reference fields SHALL report an explicit `selected` check (the requested value located on screen after
input); every open-link field write SHALL be marked `verification: screen_targeted` (label located +
value typed). Authoritative per-record commit verification is a post-save data/UI read-back, as
exercised by the demo10413 owner-create proof (`native-write-demo10413-real-proof`).

#### Scenario: Reference input reports an explicit selected check

- **WHEN** a reference field value is typed by the open-link writer
- **THEN** the result reports `selected: true` only when the value is located on screen after input
- **AND** reports `selected: false` with a reason otherwise

#### Scenario: The write result is not claimed as read-back verified

- **WHEN** an open-link field is written
- **THEN** the result is marked `verification: screen_targeted`, not a read-back-verified commit
- **AND** the authoritative commit check is the post-save read-back (the proof reads the saved record)
