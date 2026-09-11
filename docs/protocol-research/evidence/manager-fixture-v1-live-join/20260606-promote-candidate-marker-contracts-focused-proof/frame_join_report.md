# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-06T18:48:38Z`
- Run id: `20260606-promote-candidate-marker-contracts-focused-proof`
- Source runtime directory: `runtime\protocol-research\captures\20260606-promote-candidate-marker-contracts-focused-proof`
- Join status counts: `{"joined": 10}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-active-window | active_window | active_window | ok | True | joined | zero_width_expanded_to_1s | {"from": 16, "to": 16, "count": 1} | {"from": 17, "to": 17, "count": 1} |  | pending | False |
| tm-v1-diag-command-interface-dump | diagnostic_command_interface_dump | diagnostic_command_interface_dump | ok | True | joined | zero_width_expanded_to_1s | {"from": 17, "to": 19, "count": 3} | {"from": 18, "to": 20, "count": 3} |  | pending | False |
| tm-v1-diag-window-children | diagnostic_window_children | diagnostic_window_children | ok | True | joined | zero_width_expanded_to_1s | {"from": 20, "to": 21, "count": 2} | {"from": 21, "to": 22, "count": 2} |  | pending | False |
| tm-v1-diag-window-find-form-marker | diagnostic_window_find_form_marker | diagnostic_window_find_form_marker | ok | True | joined | zero_width_expanded_to_1s | {"from": 22, "to": 24, "count": 3} | {"from": 23, "to": 25, "count": 3} |  | pending | False |
| tm-v1-diag-window-get-form-path | diagnostic_window_get_form_path | diagnostic_window_get_form_path | ok | True | joined |  | {"from": 25, "to": 361, "count": 337} | {"from": 26, "to": 361, "count": 336} |  | pending | False |
| tm-v1-form-summary | form_summary | form_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 365, "to": 367, "count": 3} | {"from": 366, "to": 368, "count": 3} |  | pending | False |
| tm-v1-checkbox-true | element_state | element_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 368, "to": 372, "count": 5} | {"from": 369, "to": 373, "count": 5} |  | pending | False |
| tm-v1-button-inert | element_state | element_state | ok | True | joined |  | {"from": 373, "to": 1020, "count": 648} | {"from": 374, "to": 1020, "count": 647} |  | pending | False |
| tm-v1-table-items | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 1025, "to": 1030, "count": 6} | {"from": 1026, "to": 1031, "count": 6} |  | pending | False |
| tm-v1-group-main | group_summary | group_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 1031, "to": 1036, "count": 6} | {"from": 1032, "to": 1037, "count": 6} |  | pending | False |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- Joined rows without accepted replay/probe evidence remain non-accepted protocol mappings.
