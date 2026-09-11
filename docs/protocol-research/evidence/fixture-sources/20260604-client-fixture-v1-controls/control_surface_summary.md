# Client Fixture V1 Control Surface Summary

Snapshot date: 2026-06-04.

## Scope

Change: `add-client-fixture-v1-readonly-controls`.

This evidence records source-level readiness for the V1 client fixture control
surface. It does not claim a live DB update, TestClient form-open result,
frame range, normalized hash or accepted protocol mapping.

## Source Boundary

- EDT workspace: `C:\1C_BASES\EDT\vanessa_qa`.
- EDT project: `vanessa_client`.
- Target context: `client`.
- Source object:
  `src/DataProcessors/<client-fixture-processor>/Forms/<main-form>/`.
- Runtime binding status: provider gap retained from the current OPSX run;
  no retrieve, DB update, hot deploy or runtime apply was performed.

## Implemented Control Markers

| Family | Markers | Source status | V1 protocol status |
| --- | --- | --- | --- |
| Shell/state | `PF_FORM_MAIN`, `PF_GROUP_MAIN`, `PF_FIXTURE_VERSION`, `PF_LAST_ACTION`, `PF_ACTION_COUNTER`, `PF_SELECTED_ROW_MARKER` | source-authored | read-only target only |
| Edit fields | `PF_EDIT_STRING`, `PF_EDIT_NUMBER`, `PF_EDIT_DATE`, `PF_EDIT_READONLY`, `PF_EDIT_DISABLED` | source-authored | input acceptance out of scope |
| Checkboxes | `PF_CHECKBOX_TRUE`, `PF_CHECKBOX_FALSE`, `PF_CHECKBOX_READONLY`, `PF_CHECKBOX_DISABLED` | source-authored | toggle acceptance out of scope |
| Choice/radio | `PF_CHOICE_MODE`, `PF_CHOICE_A`, `PF_CHOICE_B`, `PF_CHOICE_C` | source-authored | page/input action acceptance out of scope |
| Buttons | `PF_BUTTON_INERT`, `PF_BUTTON_DISABLED`, `PF_BUTTON_DEFAULT` | source-authored | click acceptance out of scope |
| Command bar | `PF_COMMAND_BAR_MAIN`, `PF_COMMAND_ENABLED`, `PF_COMMAND_DISABLED`, `PF_COMMAND_POPUP`, `PF_COMMAND_POPUP_CHILD`, `PF_RESET_STATE` | source-authored | command acceptance out of scope |
| Table | `PF_TABLE_ITEMS`, `PF_TABLE_MARKER`, `PF_TABLE_TEXT`, `PF_TABLE_NUMBER`, `PF_TABLE_FLAG` | source-authored | table edit acceptance out of scope |
| Table rows | `PF_ROW_001`, `PF_ROW_002`, `PF_ROW_003` | initialized in form module | read-only target only |
| Label/group/pages | `PF_LABEL_STATUS`, `PF_GROUP_DISABLED`, `PF_PAGES_MAIN`, `PF_PAGE_A`, `PF_PAGE_A_LABEL`, `PF_PAGE_A_FIELD`, `PF_PAGE_B`, `PF_PAGE_B_FIELD` | source-authored | navigation action acceptance out of scope |

## Deterministic State

- Version value: `protocol-fixture.v1`.
- Initial state marker: `PF_STATE_INITIAL`.
- Initial selected row marker: `PF_ROW_NONE`.
- Choice value: `PF_CHOICE_B`.
- Label value: `PF_LABEL_STATUS_READY`.
- Table rows:
  `PF_ROW_001`, `PF_ROW_002`, `PF_ROW_003`.

## Verification Notes

- XML parse passed for the fixture form, fixture processor metadata,
  configuration metadata and subsystem metadata.
- Item ids in the fixture form are unique within form item nodes; repeated ids
  in attributes, columns and commands are scoped to their own EDT collections.
- Marker grep confirmed the expected V1 edit, checkbox, choice, button,
  command bar, table, row, label, group and page markers in source.
- BSL marker grep confirmed deterministic value setup and table row setup in
  the form module.
- Read-only TestClient/Vanessa form analysis is deferred because the fixture
  source was not applied to the client infobase in this change.

## Provider Gap

```yaml
provider_gap:
  provider_id: edt-mcp
  owner_path: /opt/edt-lab
  matrix_row: delivery_or_runtime_apply
  missing_capability: validate_project_infobase_binding did not return in the current OPSX run
  missing_evidence_type: runtime_apply_log_and_live_form_tree
  impact: live marker coverage evidence is deferred
  current_workaround: source-level EDT authoring with compact marker evidence only
  source_card: openspec/board/2.todo/01-2026-06-04-client-fixture-v1-control-surface.md
  sanitized_evidence: docs/protocol-research/evidence/fixture-sources/20260604-client-fixture-v1-controls/control_surface_summary.md
  sensitivity: no credentials or raw runtime payloads copied
```
