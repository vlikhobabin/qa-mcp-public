# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-04T19:04:00Z`
- Run id: `opsx-manager-fixture-v1-dryrun`
- Source runtime directory: `runtime\protocol-research\captures\opsx-manager-fixture-v1-dryrun`
- Join status counts: `{"blocked": 5, "unresolved": 1}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-active-window | active_window | active_window | not_run | False | blocked |  |  | no side-channel event for this command in the retained run | not_run | False |
| tm-v1-active-form | active_form | active_form | dry_run_ok | True | unresolved |  |  | dry-run produced no proxy traffic or chunk counters | not_run | False |
| tm-v1-field-version | element_details | element_details | not_run | False | blocked |  |  | no side-channel event for this command in the retained run | not_run | False |
| tm-v1-table-items | table_summary | table_summary | not_run | False | blocked |  |  | no side-channel event for this command in the retained run | not_run | False |
| tm-v1-commandbar-main | commandbar_summary | commandbar_summary | not_run | False | blocked |  |  | no side-channel event for this command in the retained run | not_run | False |
| tm-v1-pages-main | pages_summary | pages_summary | not_run | False | blocked |  |  | no side-channel event for this command in the retained run | not_run | False |

## Notes

- `joined` requires reviewed frame or chunk ranges. This retained run has no joined cases.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- No normalized hashes or replay/direct-probe confirmations are present in this report.
