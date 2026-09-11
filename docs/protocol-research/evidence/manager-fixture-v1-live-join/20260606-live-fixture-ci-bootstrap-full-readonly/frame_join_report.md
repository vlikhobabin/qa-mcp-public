# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-06T09:23:17Z`
- Run id: `20260606-live-fixture-ci-bootstrap-full-readonly`
- Source runtime directory: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260606-live-fixture-ci-bootstrap-full-readonly`
- Join status counts: `{"joined": 17}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-active-window | active_window | active_window | ok | True | joined | zero_width_expanded_to_1s | {"from": 16, "to": 16, "count": 1} | {"from": 17, "to": 17, "count": 1} |  | pending | False |
| tm-v1-active-form | active_form | active_form | ok | True | joined | zero_width_expanded_to_1s | {"from": 17, "to": 17, "count": 1} | {"from": 18, "to": 18, "count": 1} |  | pending | False |
| tm-v1-diag-command-interface-dump | diagnostic_command_interface_dump | diagnostic_command_interface_dump | ok | True | joined | zero_width_expanded_to_1s | {"from": 18, "to": 20, "count": 3} | {"from": 19, "to": 21, "count": 3} |  | pending | False |
| tm-v1-diag-window-children | diagnostic_window_children | diagnostic_window_children | ok | True | joined | zero_width_expanded_to_1s | {"from": 21, "to": 22, "count": 2} | {"from": 22, "to": 23, "count": 2} |  | pending | False |
| tm-v1-diag-window-find-form-marker | diagnostic_window_find_form_marker | diagnostic_window_find_form_marker | failed | True | joined |  | {"from": 23, "to": 252, "count": 230} | {"from": 24, "to": 252, "count": 229} |  | pending | False |
| tm-v1-diag-window-get-form-path | diagnostic_window_get_form_path | diagnostic_window_get_form_path | failed | True | joined |  | {"from": 253, "to": 461, "count": 209} | {"from": 254, "to": 461, "count": 208} |  | pending | False |
| tm-v1-diag-window-find-field-marker | diagnostic_window_find_field_marker | diagnostic_window_find_field_marker | ok | True | joined | zero_width_expanded_to_1s | {"from": 463, "to": 465, "count": 3} | {"from": 464, "to": 466, "count": 3} |  | pending | False |
| tm-v1-diag-form-find-field-marker | diagnostic_form_find_field_marker | diagnostic_form_find_field_marker | failed | True | joined |  | {"from": 466, "to": 698, "count": 233} | {"from": 467, "to": 698, "count": 232} |  | pending | False |
| tm-v1-form-summary | form_summary | form_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 700, "to": 702, "count": 3} | {"from": 701, "to": 703, "count": 3} |  | pending | False |
| tm-v1-field-version | element_details | element_details | ok | True | joined | zero_width_expanded_to_1s | {"from": 703, "to": 705, "count": 3} | {"from": 704, "to": 706, "count": 3} |  | pending | False |
| tm-v1-field-string | element_details | element_details | ok | True | joined | zero_width_expanded_to_1s | {"from": 706, "to": 708, "count": 3} | {"from": 707, "to": 709, "count": 3} |  | pending | False |
| tm-v1-checkbox-true | element_state | element_state | ok | True | joined |  | {"from": 709, "to": 852, "count": 144} | {"from": 710, "to": 853, "count": 144} |  | pending | False |
| tm-v1-button-inert | element_state | element_state | ok | True | joined |  | {"from": 854, "to": 997, "count": 144} | {"from": 855, "to": 998, "count": 144} |  | pending | False |
| tm-v1-table-items | table_summary | table_summary | ok | True | joined |  | {"from": 998, "to": 1144, "count": 147} | {"from": 999, "to": 1145, "count": 147} |  | pending | False |
| tm-v1-commandbar-main | commandbar_summary | commandbar_summary | ok | True | joined |  | {"from": 1145, "to": 1291, "count": 147} | {"from": 1146, "to": 1292, "count": 147} |  | pending | False |
| tm-v1-group-main | group_summary | group_summary | ok | True | joined |  | {"from": 1292, "to": 1438, "count": 147} | {"from": 1293, "to": 1439, "count": 147} |  | pending | False |
| tm-v1-pages-main | pages_summary | pages_summary | ok | True | joined |  | {"from": 1439, "to": 1584, "count": 146} | {"from": 1440, "to": 1585, "count": 146} |  | pending | False |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- Joined rows are still not accepted protocol mappings until normalized hashes and replay or direct-probe confirmations are retained.
