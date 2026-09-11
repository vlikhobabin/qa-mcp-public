# Manager Fixture V1 Read-Only Command Catalog

Snapshot date: 2026-06-04.

## Scope

Change: `define-manager-fixture-v1-readonly-command-manifest`.

This evidence defines the manager-side read-only command manifest and output
contract. It does not claim a live manager run, frame range, normalized hash,
replay result or accepted protocol mapping.

## Contract Files

- `manager_harness_manifest.sample.json` - sample input manifest.
- `case_events.sample.jsonl` - sample before/after command events.
- `manager_harness_result.sample.json` - sample compact run summary.
- Manager source:
  `C:\1C_BASES\EDT\vanessa_qa\vanessa_manager\src\DataProcessors\ProtocolFixtureTestManager\`.

## Catalog Coverage

| Family | Command kinds | Marker examples | Status |
| --- | --- | --- | --- |
| Application/window | `active_window` | `PF_FORM_MAIN` | source-authored |
| Active form | `active_form`, `form_summary` | `PF_FORM_MAIN`, `PF_FIXTURE_VERSION` | source-authored |
| Fields | `element_details`, `element_state` | `PF_FIXTURE_VERSION`, `PF_EDIT_STRING`, `PF_CHECKBOX_TRUE` | source-authored |
| Buttons/commands | `element_state`, `commandbar_summary` | `PF_BUTTON_INERT`, `PF_COMMAND_BAR_MAIN`, `PF_COMMAND_ENABLED` | source-authored |
| Table | `table_summary` | `PF_TABLE_ITEMS`, `PF_ROW_001` | source-authored |
| Groups/pages | `group_summary`, `pages_summary` | `PF_GROUP_MAIN`, `PF_PAGES_MAIN`, `PF_PAGE_A` | source-authored |

## Read-Only Rejections

The V1 accepted catalog rejects command kinds for text input, clicks, page
switching, row selection, business commands and object writes. Buttons,
checkboxes, commands, rows and pages may appear as read-only targets, but
their action semantics are not accepted by this contract.

## Verification Notes

- JSON samples were parsed with a Windows-native parser.
- JSONL events were parsed line-by-line.
- The manager source contains manifest validation, read-only catalog seeding,
  event/result writer functions and command-kind rejection logic.
- Runtime execution remains deferred until the manager shell can be deployed
  without a broad full configuration reload and the manager runtime platform
  mismatch is resolved.
