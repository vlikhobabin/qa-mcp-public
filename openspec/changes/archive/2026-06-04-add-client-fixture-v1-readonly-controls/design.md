## Context

The V1 processor shell gives the lab a dedicated form target. This change
turns that shell into a useful read-only fixture surface by adding the main
control families from the roadmap. The goal is to make later corpus captures
rich enough to classify element families without changing the form every time.

## Goals / Non-Goals

Goals:

- Expose stable `PF_*` markers for common managed form control families.
- Include state variants that are important for read-only property probes:
  enabled, disabled, read-only and visible/invisible where practical.
- Keep all values deterministic and local to form attributes.
- Make the form useful for `form-summary` and `form-element-details` style
  probes.

Non-goals:

- Do not accept or validate action protocol semantics.
- Do not execute business commands, text input, checkbox toggles or page
  switching as part of acceptance.
- Do not use real business tables, dynamic lists or external data sources.
- Do not create accepted protocol dictionary descriptors.

## Decisions

- Add a wide surface in V1 rather than one control family per later version.
  This front-loads fixture authoring cost and keeps future protocol runs from
  being blocked by missing basic controls.
- Prefer local attributes and value tables over dynamic lists. Local data is
  deterministic, resettable and does not depend on demo infobase content.
- Keep disabled and read-only variants visible when possible. Hidden controls
  can be represented by metadata/path map entries, but live UI evidence for
  invisible controls may be provider-dependent.
- Use unique markers in element names, captions and values. Response marker
  review should not rely on repeated Russian captions or current business data.

## Control Families

Planned V1 surface:

- `PF_EDIT_STRING`, `PF_EDIT_NUMBER`, `PF_EDIT_DATE`,
  `PF_EDIT_READONLY`, `PF_EDIT_DISABLED`.
- `PF_CHECKBOX_TRUE`, `PF_CHECKBOX_FALSE`, `PF_CHECKBOX_READONLY`,
  `PF_CHECKBOX_DISABLED`.
- `PF_CHOICE_MODE` or equivalent radio/choice control with stable values.
- `PF_BUTTON_INERT`, `PF_BUTTON_DISABLED`, `PF_BUTTON_DEFAULT`.
- `PF_COMMAND_BAR_MAIN`, `PF_COMMAND_ENABLED`, `PF_COMMAND_DISABLED`,
  `PF_COMMAND_POPUP`.
- `PF_TABLE_ITEMS` with rows `PF_ROW_001`, `PF_ROW_002`, `PF_ROW_003` and
  typed columns.
- `PF_LABEL_STATUS`, `PF_GROUP_MAIN`, `PF_GROUP_DISABLED`,
  `PF_PAGES_MAIN`, `PF_PAGE_A`, `PF_PAGE_B`.

## Capture And Replay Strategy

This change prepares target surface only. A read-only form analysis or direct
probe may be used to prove markers are visible, but any accepted protocol
mapping still requires later corpus rows with frame ranges, normalized hashes,
dynamic fields and replay/probe status.

## Risks / Trade-offs

- A very wide form can make response parsing noisy. Mitigation: unique markers
  and an explicit target map in the next change.
- Some form element variants may be represented differently by TestClient than
  EDT metadata. Mitigation: record provider gaps and keep rows pending instead
  of inferring coverage.
- Disabled/read-only controls may be confused with action readiness. Mitigation:
  keep V1 acceptance strictly read-only.
