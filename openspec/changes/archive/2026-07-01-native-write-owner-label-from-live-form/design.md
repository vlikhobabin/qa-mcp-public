## Context

`_OPEN_LINK_LABEL_ALIASES` (`src/qa_mcp/mcp_server.py:251`) maps
`("e1cib/data/Справочник.ДоговорыКонтрагентов", "reference", "Владелец") → "Контрагент"`.
`_open_link_visible_label` (`:276`) returns `aliases.get((normalized, field_mode, field), field)`,
and the scenario input-step route calls it at `:607` to pick the label to locate. The direct tool
`write_form_fields_by_label` does NOT pass through the alias — it locates `f"{label}:"` verbatim
(`:1745`).

Live evidence (2026-06-30): on demo10413 the owner label is «Владелец»; the alias would rewrite it to
«Контрагент», which is absent there. The predecessor proof ran on the retired vanessa form whose
owner label is «Контрагент», so the alias matched there — masking the demo10413 gap.

## Goals / Non-Goals

**Goals:**
- Resolve the owner/reference label from the live form so «Владелец» (demo10413) and «Контрагент»
  (vanessa) both work.
- Remove the fixture-specific owner-label constant.

**Non-Goals:**
- Short/reference-label localization mechanics (that is `native-write-locate-short-reference-label`,
  on which this depends).
- Date commit behaviour (`native-write-open-link-date-commit`).

## Decisions

- Resolve the label from `read_form_descriptor` (or the requested field name) at write time rather
  than a static map. If a per-config mapping is ever genuinely needed, drive it from form evidence,
  not a hard-coded constant.
- Keep the scenario route (`_open_link_visible_label`) as the single resolution point so both the
  scenario and the direct tool converge on the live-form label.

## Risks / Trade-offs

- Removing the alias surfaces the dependency on `native-write-locate-short-reference-label`: until
  short-label localization works, the scenario route targeting «Владелец» will still fail to locate.
  Sequence this change after Change 1.
- Safety: offline label-resolution tests need no live runtime; the live confirmation opens the
  demo10413 create form read-only (no save) and leaves no records.
