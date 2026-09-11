# First Focused V2 Safe-Action Subset

Run id: `20260607-first-focused-subset`

This evidence selects input rows for the first focused manager fixture V2
safe-action proof. It does not accept any protocol mapping and does not claim
live execution.

## Selected Rows

| order | action id | target id | target marker | family | recovery expectation |
| --- | --- | --- | --- | --- | --- |
| 1 | `safe-switch-fixture-page-b` | `tm-v2-pages-main` | `PF_PAGES_MAIN` | `switch_fixture_page` | `select_page_a` returns `PF_PAGE_A` |
| 2 | `safe-focus-existing-edit-string` | `tm-v2-edit-string` | `PF_EDIT_STRING` | `focus_existing_element` | `focus_form_shell` returns `PF_FORM_MAIN` |

Both rows carry `mutates_business_data=false`, an allowlisted action family,
target marker, pre-state, post-state, recovery expectation and expected action
result markers.

## Deferred Or Excluded Rows

| action id | decision | owner | reason | residual risk |
| --- | --- | --- | --- | --- |
| `safe-activate-existing-window` | deferred | `project:qa-mcp` | Not needed for the first focused action proof unless capture bootstrap requires explicit activation. | Useful setup traffic, but not proof of the preferred fixture action families. |
| `safe-select-local-row-002` | deferred | `project:qa-mcp` | Safe-cataloged but broader than the first page/focus proof. | Selection state needs reset proof before first action-frame isolation. |
| `safe-expand-commandbar-main` | deferred | `project:qa-mcp` | Menu expansion is harder to distinguish from command invocation. | Popup identity drift could approach command-like behavior. |
| `blocked-expand-popup-child` | excluded | `project:qa-mcp` | Catalog marks the popup child target blocked because identity is not reviewed enough. | A child popup target could invoke a command if marker identity drifts. |
| `rejected-click-inert-button` | excluded | `project:qa-mcp` | Button clicks and business command clicks are outside V2 safe-action scope. | Button behavior belongs to a later mutation/recovery card. |

## Evidence Inputs

- Focused manifest:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-subset/focused_safe_action_manifest.json`
- Source catalog:
  `tools/protocol-research/manager_fixture_v2_safe_action_catalog.json`
- V2 target-map publication boundary:
  `docs/protocol-research/evidence/fixture-target-maps/20260607-client-fixture-v2-safe-action-target-map/target_map_summary.md`
- Detailed marker source map used by the catalog:
  `docs/protocol-research/evidence/fixture-target-maps/20260604-client-fixture-v1-target-map/target_map.json`
- Prior candidate dry run:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-candidate-dry-run/safe_action_report.md`

## Decision

The downstream live capture change may attempt only
`safe-switch-fixture-page-b` and `safe-focus-existing-edit-string` from this
focused manifest. Any unavailable row must fail closed with typed status rather
than falling through to a broader action.
