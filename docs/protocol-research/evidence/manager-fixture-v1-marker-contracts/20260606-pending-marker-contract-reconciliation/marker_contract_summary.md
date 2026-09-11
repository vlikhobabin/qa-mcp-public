# Manager Fixture V1 Marker Contract Reconciliation

- Source cleanup run: `20260606-live-fixture-ci-bootstrap-full-readonly-cleanup`
- Catalog changes applied: `0`
- Accepted mappings from this reconciliation: `0`
- Catalog drift check: `ok`

## Decisions

| case id | previous expected | candidate | current proof | decision |
| --- | --- | --- | --- | --- |
| `tm-v1-diag-window-find-form-marker` | `PF_FIXTURE_VERSION` | `QA MCP Protocol Fixture V1` | `not_run` | `candidate_only` |
| `tm-v1-form-summary` | `PF_FIXTURE_VERSION` | `QA MCP Protocol Fixture V1` | `not_run` | `candidate_only` |
| `tm-v1-checkbox-true` | `CheckBox` | none | `transport_ok_marker_mismatch`, observed `PF_CHECKBOX_TRUE` | `mismatch_retained` |
| `tm-v1-button-inert` | `TestedFormButton` | `PF_BUTTON_INERT` | `transport_ok_marker_mismatch`, broad range `131..390` | `candidate_only_blocked_by_broad_range` |
| `tm-v1-table-items` | `PF_ROW_001` | `PF_TABLE_ITEMS` | `transport_ok_marker_mismatch`, observed `PF_TABLE_ITEMS` | `candidate_only` |
| `tm-v1-group-main` | `PF_FORM_MAIN` | `PF_GROUP_MAIN` | `transport_ok_marker_mismatch`, observed `PF_GROUP_MAIN` | `candidate_only` |

## Boundary

No expected-marker correction was applied. The existing JSON catalog and BSL
catalog remain aligned, and old/candidate markers are retained for the next
runtime-restored proof pass.

`tm-v1-button-inert` remains strictly read-only evidence. This reconciliation
does not claim click, command execution or other action semantics.
