## 1. Remove the fixture alias

- [x] 1.1 Remove or parametrize `_OPEN_LINK_LABEL_ALIASES` (`src/qa_mcp/mcp_server.py:251`) so no
  single config's owner label (`Владелец → Контрагент`) is hard-coded.

## 2. Resolve label from the live form

- [x] 2.1 In `_open_link_visible_label` (`:276`, used at `:607`) resolve the owner/reference label
  from the live form descriptor (`read_form_descriptor`) / the requested field name.
- [x] 2.2 Ensure both the scenario route and the direct `write_form_fields_by_label` converge on the
  live-form label.

## 3. Offline tests

- [x] 3.1 Test that owner-label resolution returns «Владелец» for a demo10413-shaped descriptor and
  «Контрагент» for a vanessa-shaped descriptor, with no fixture constant.

## 4. Live verification (demo10413)

- [x] 4.1 With the catalog re-applied, confirm the open-link reference write targets the owner field
  by its real «Владелец» label on the demo10413 create form (depends on Change 1 localization).
- [x] 4.2 Retain the run bundle and record evidence path.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner |
| --- | --- | --- | --- | --- | --- | --- |
| open-link reference resolution | `_OPEN_LINK_LABEL_ALIASES`, `_open_link_visible_label` | offline + live | offline test: «Владелец» vs «Контрагент» resolved from descriptor; live «Владелец» targeted | `.artifacts/openspec/native-write-owner-label-from-live-form/<run-id>/` | planned | qa-mcp |
| source hygiene | no fixture owner-label constant | source inspection + test | alias entry no longer hard-codes a single config's label | (source/test) | planned | qa-mcp |
