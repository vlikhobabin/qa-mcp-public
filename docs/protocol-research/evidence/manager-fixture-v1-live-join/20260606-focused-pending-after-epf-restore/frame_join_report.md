# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-06T18:21:13Z`
- Run id: `20260606-focused-pending-after-epf-restore`
- Source runtime directory: `runtime\protocol-research\captures\20260606-focused-pending-after-epf-restore`
- Join status counts: `{"joined": 9}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-diag-command-interface-dump | diagnostic_command_interface_dump | diagnostic_command_interface_dump | ok | True | joined | zero_width_expanded_to_1s | {"from": 6, "to": 12, "count": 7} | {"from": 7, "to": 13, "count": 7} |  | pending | False |
| tm-v1-diag-window-children | diagnostic_window_children | diagnostic_window_children | ok | True | joined | zero_width_expanded_to_1s | {"from": 13, "to": 14, "count": 2} | {"from": 14, "to": 15, "count": 2} |  | pending | False |
| tm-v1-diag-window-find-form-marker | diagnostic_window_find_form_marker | diagnostic_window_find_form_marker | failed | True | joined |  | {"from": 15, "to": 7158, "count": 7144} | {"from": 16, "to": 7159, "count": 7144} |  | pending | False |
| tm-v1-diag-window-get-form-path | diagnostic_window_get_form_path | diagnostic_window_get_form_path | failed | True | joined |  | {"from": 7159, "to": 14693, "count": 7535} | {"from": 7160, "to": 14693, "count": 7534} |  | pending | False |
| tm-v1-form-summary | form_summary | form_summary | failed | True | joined |  | {"from": 14694, "to": 14986, "count": 293} | {"from": 14695, "to": 14987, "count": 293} |  | pending | False |
| tm-v1-checkbox-true | element_state | element_state | failed | True | joined |  | {"from": 14987, "to": 15133, "count": 147} | {"from": 14988, "to": 15134, "count": 147} |  | pending | False |
| tm-v1-button-inert | element_state | element_state | failed | True | joined |  | {"from": 15134, "to": 15280, "count": 147} | {"from": 15135, "to": 15281, "count": 147} |  | pending | False |
| tm-v1-table-items | table_summary | table_summary | failed | True | joined |  | {"from": 15281, "to": 15406, "count": 126} | {"from": 15282, "to": 15407, "count": 126} |  | pending | False |
| tm-v1-group-main | group_summary | group_summary | failed | True | joined |  | {"from": 15407, "to": 15553, "count": 147} | {"from": 15408, "to": 15554, "count": 147} |  | pending | False |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- Joined rows without accepted replay/probe evidence remain non-accepted protocol mappings.
