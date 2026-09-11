# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-06T18:23:06Z`
- Run id: `20260606-focused-pending-after-epf-restore-ci-bootstrap`
- Source runtime directory: `runtime\protocol-research\captures\20260606-focused-pending-after-epf-restore-ci-bootstrap`
- Join status counts: `{"joined": 9}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-diag-command-interface-dump | diagnostic_command_interface_dump | diagnostic_command_interface_dump | ok | True | joined | zero_width_expanded_to_1s | {"from": 16, "to": 18, "count": 3} | {"from": 17, "to": 19, "count": 3} |  | pending | False |
| tm-v1-diag-window-children | diagnostic_window_children | diagnostic_window_children | ok | True | joined | zero_width_expanded_to_1s | {"from": 19, "to": 20, "count": 2} | {"from": 20, "to": 21, "count": 2} |  | pending | False |
| tm-v1-diag-window-find-form-marker | diagnostic_window_find_form_marker | diagnostic_window_find_form_marker | ok | True | joined | zero_width_expanded_to_1s | {"from": 21, "to": 23, "count": 3} | {"from": 22, "to": 24, "count": 3} |  | pending | False |
| tm-v1-diag-window-get-form-path | diagnostic_window_get_form_path | diagnostic_window_get_form_path | ok | True | joined |  | {"from": 24, "to": 501, "count": 478} | {"from": 25, "to": 501, "count": 477} |  | pending | False |
| tm-v1-form-summary | form_summary | form_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 505, "to": 507, "count": 3} | {"from": 506, "to": 508, "count": 3} |  | pending | False |
| tm-v1-checkbox-true | element_state | element_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 508, "to": 512, "count": 5} | {"from": 509, "to": 513, "count": 5} |  | pending | False |
| tm-v1-button-inert | element_state | element_state | ok | True | joined |  | {"from": 513, "to": 1535, "count": 1023} | {"from": 514, "to": 1535, "count": 1022} |  | pending | False |
| tm-v1-table-items | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 1540, "to": 1545, "count": 6} | {"from": 1541, "to": 1546, "count": 6} |  | pending | False |
| tm-v1-group-main | group_summary | group_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 1546, "to": 1551, "count": 6} | {"from": 1547, "to": 1552, "count": 6} |  | pending | False |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- Joined rows without accepted replay/probe evidence remain non-accepted protocol mappings.
