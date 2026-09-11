# Client Fixture V1 Target Map

Snapshot date: 2026-06-04.

## Scope

Change: `publish-client-fixture-v1-target-map`.

This evidence publishes the semantic/source target map for the V1 client
fixture processor. It prepares read-only corpus capture inputs, but it does
not claim live form coverage, frame ranges, normalized hashes, replay results
or accepted protocol mappings.

## Files

- `target_map.json` - machine-readable target rows for V1 `PF_*` elements.
- `target_map_summary.md` - this reviewed summary.
- Source evidence:
  `docs/protocol-research/evidence/fixture-sources/20260604-client-fixture-v1-shell/source_summary.md`.
- Control evidence:
  `docs/protocol-research/evidence/fixture-sources/20260604-client-fixture-v1-controls/control_surface_summary.md`.

## Coverage Summary

| Family | Planned case ids | Marker examples | Availability |
| --- | --- | --- | --- |
| Form shell/state | `fixture-form-shell-readonly`, `fixture-state-fields-readonly` | `PF_FORM_MAIN`, `PF_FIXTURE_VERSION`, `PF_LAST_ACTION` | `partial` |
| Edit fields | `fixture-editfield-readonly`, `typed-input-field-readonly` | `PF_EDIT_STRING`, `PF_EDIT_NUMBER`, `PF_EDIT_DATE`, `PF_EDIT_READONLY`, `PF_EDIT_DISABLED` | `partial` |
| Checkboxes | `fixture-checkbox-readonly` | `PF_CHECKBOX_TRUE`, `PF_CHECKBOX_FALSE`, `PF_CHECKBOX_READONLY`, `PF_CHECKBOX_DISABLED` | `partial` |
| Choice/radio | `fixture-choice-readonly` | `PF_CHOICE_MODE`, `PF_CHOICE_A`, `PF_CHOICE_B`, `PF_CHOICE_C` | `partial` |
| Buttons | `fixture-button-readonly` | `PF_BUTTON_INERT`, `PF_BUTTON_DISABLED`, `PF_BUTTON_DEFAULT` | `partial` |
| Command bar | `fixture-commandbar-readonly` | `PF_COMMAND_BAR_MAIN`, `PF_COMMAND_ENABLED`, `PF_COMMAND_DISABLED`, `PF_COMMAND_POPUP`, `PF_RESET_STATE` | `partial` |
| Table | `fixture-table-readonly` | `PF_TABLE_ITEMS`, `PF_TABLE_MARKER`, `PF_ROW_001`, `PF_ROW_002`, `PF_ROW_003` | `partial` |
| Label/group/pages | `fixture-label-readonly`, `fixture-page-readonly`, `fixture-group-readonly` | `PF_LABEL_STATUS`, `PF_GROUP_MAIN`, `PF_GROUP_DISABLED`, `PF_PAGES_MAIN`, `PF_PAGE_A`, `PF_PAGE_B` | `partial` |

All rows are `partial` because the current run authored and inspected source
only. The target map is sufficient as a corpus-planning input, not as native
TestClient protocol proof.

## Read-Only Boundary

V1 target rows exclude these acceptance claims:

- text input acceptance;
- button click acceptance;
- command execution acceptance;
- checkbox toggle acceptance;
- page switching acceptance;
- table edit or row-selection acceptance;
- business-data writes;
- TCP parsing or protocol decoding inside 1C.

## Provider Gaps

```yaml
provider_gaps:
  - provider_id: edt-mcp
    owner_path: /opt/edt-lab
    status: timeout
    missing_evidence_type: runtime_apply_log_and_live_form_tree
    impact: fixture source was not applied to the client infobase in this change
  - provider_id: vanessa
    owner_path: /opt/vanessa-mcp-stack
    status: deferred
    missing_evidence_type: read_only_form_analysis
    impact: live marker coverage evidence remains a follow-up
```

## Verification Notes

- JSON syntax was validated locally.
- The JSON row count and marker count were checked against source grep for
  V1 `PF_*` targets.
- `target_map.json` explicitly sets
  `accepted_protocol_mapping: false`.
- Historical fixture corpus rows remain non-accepted until later capture and
  replay/probe evidence supplies frame ranges, normalized hashes, dynamic
  fields and status.
