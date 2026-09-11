## Why

The owner field's on-screen label is resolved from a hard-coded vanessa-specific alias
`("e1cib/data/Справочник.ДоговорыКонтрагентов", "reference", "Владелец") → "Контрагент"`
(`_OPEN_LINK_LABEL_ALIASES`, `src/qa_mcp/mcp_server.py:251`), applied in the scenario route by
`_open_link_visible_label` (`:276`, used at `:607`). On demo10413 the visible owner label is
«Владелец», so the scenario route targets a non-existent «Контрагент» label.

Live + static evidence (2026-06-30): the direct tool `write_form_fields_by_label` uses **verbatim**
labels (`:1745`) and does NOT apply the alias — which is exactly why the predecessor proof appeared
to "work" only on the retired vanessa form (whose owner label really is «Контрагент»), and why on
demo10413 the owner field cannot be addressed by its real label through the scenario route. The alias
is a fixture-specific constant that bakes one config's label into the engine.

## What Changes

- Remove or parametrize the `Владелец → Контрагент` alias (`_OPEN_LINK_LABEL_ALIASES`,
  `mcp_server.py:251`).
- Derive the on-screen owner label from the live form (the `read_form_descriptor` descriptor / the
  requested field name) so both «Владелец» (demo10413) and «Контрагент» (vanessa) forms resolve
  correctly with no fixture-specific owner-label constant.

## Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: add requirements that the open-link reference/owner label is resolved from
  the live form, not a hard-coded fixture alias, and that no fixture-specific owner-label constant
  remains.

## Impact

- Python manager: `src/qa_mcp/mcp_server.py` (`_OPEN_LINK_LABEL_ALIASES`, `_open_link_visible_label`,
  the scenario input-step route at `:607`).
- Depends on `native-write-locate-short-reference-label`: removing the alias makes the scenario route
  target the real «Владелец» label, which only succeeds once short/reference-label localization works.
- Offline test asserting label resolution for both the demo10413 and vanessa owner forms; live
  demo10413 confirmation that the open-link reference write targets «Владелец» by its real label.
- Live 1C runtime for the demo10413 leg only; otherwise offline.
