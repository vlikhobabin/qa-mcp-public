## ADDED Requirements

### Requirement: Open-link owner/reference label is resolved from the live form

The open-link write route SHALL resolve a reference/owner field's on-screen label from the live form
(its `read_form_descriptor` descriptor and/or the requested field name), not from a hard-coded
fixture alias. No config-specific owner-label constant (such as «Владелец»→«Контрагент») SHALL remain
baked into the engine.

#### Scenario: demo10413 owner field targeted by its real label

- **WHEN** the open-link route writes the owner field on the demo10413
  `Catalog.ДоговорыКонтрагентов` create form
- **THEN** it targets the «Владелец» label that the live form actually shows
- **AND** it does not look for a «Контрагент» label that is absent on that form

#### Scenario: label is the requested field name, not a baked-in alias

- **WHEN** the open-link route resolves the on-screen label for a reference/owner field
- **THEN** it uses the requested field name (which is the live on-screen label on a create form)
- **AND** the retired vanessa-only «Владелец»→«Контрагент» alias no longer overrides it

#### Scenario: no fixture owner-label constant remains

- **WHEN** the source is inspected after the change
- **THEN** the `Владелец → Контрагент` alias entry no longer hard-codes a single config's label
- **AND** an offline test asserts owner-label resolution for both the demo10413 and vanessa forms
