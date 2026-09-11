# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-06T16:35:41Z`
- Run id: `20260606-live-fixture-ci-bootstrap-full-readonly-cleanup`
- Source runtime directory: `runtime\protocol-research\captures\20260606-live-fixture-ci-bootstrap-full-readonly-cleanup`
- Join status counts: `{"joined": 17}`
- Accepted case ids: `["tm-v1-active-window", "tm-v1-active-form", "tm-v1-diag-window-find-field-marker", "tm-v1-diag-form-find-field-marker", "tm-v1-field-version", "tm-v1-field-string", "tm-v1-commandbar-main", "tm-v1-pages-main"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-active-window | active_window | active_window | ok | True | joined | zero_width_expanded_to_1s | {"from": 16, "to": 16, "count": 1} | {"from": 17, "to": 17, "count": 1} |  | accepted_probe | True |
| tm-v1-active-form | active_form | active_form | ok | True | joined | zero_width_expanded_to_1s | {"from": 17, "to": 17, "count": 1} | {"from": 18, "to": 18, "count": 1} |  | accepted_probe | True |
| tm-v1-diag-command-interface-dump | diagnostic_command_interface_dump | diagnostic_command_interface_dump | ok | True | joined | zero_width_expanded_to_1s | {"from": 18, "to": 20, "count": 3} | {"from": 19, "to": 21, "count": 3} |  | pending | False |
| tm-v1-diag-window-children | diagnostic_window_children | diagnostic_window_children | ok | True | joined | zero_width_expanded_to_1s | {"from": 21, "to": 22, "count": 2} | {"from": 22, "to": 23, "count": 2} |  | pending | False |
| tm-v1-diag-window-find-form-marker | diagnostic_window_find_form_marker | diagnostic_window_find_form_marker | ok | True | joined | zero_width_expanded_to_1s | {"from": 23, "to": 25, "count": 3} | {"from": 24, "to": 26, "count": 3} |  | pending | False |
| tm-v1-diag-window-get-form-path | diagnostic_window_get_form_path | diagnostic_window_get_form_path | ok | True | joined |  | {"from": 26, "to": 106, "count": 81} | {"from": 27, "to": 106, "count": 80} |  | pending | False |
| tm-v1-diag-window-find-field-marker | diagnostic_window_find_field_marker | diagnostic_window_find_field_marker | ok | True | joined | zero_width_expanded_to_1s | {"from": 110, "to": 112, "count": 3} | {"from": 111, "to": 113, "count": 3} |  | accepted_probe | True |
| tm-v1-diag-form-find-field-marker | diagnostic_form_find_field_marker | diagnostic_form_find_field_marker | ok | True | joined | zero_width_expanded_to_1s | {"from": 113, "to": 116, "count": 4} | {"from": 114, "to": 117, "count": 4} |  | accepted_probe | True |
| tm-v1-form-summary | form_summary | form_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 117, "to": 119, "count": 3} | {"from": 118, "to": 120, "count": 3} |  | pending | False |
| tm-v1-field-version | element_details | element_details | ok | True | joined | zero_width_expanded_to_1s | {"from": 120, "to": 122, "count": 3} | {"from": 121, "to": 123, "count": 3} |  | accepted_probe | True |
| tm-v1-field-string | element_details | element_details | ok | True | joined | zero_width_expanded_to_1s | {"from": 123, "to": 125, "count": 3} | {"from": 124, "to": 126, "count": 3} |  | accepted_probe | True |
| tm-v1-checkbox-true | element_state | element_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 126, "to": 130, "count": 5} | {"from": 127, "to": 131, "count": 5} |  | pending | False |
| tm-v1-button-inert | element_state | element_state | ok | True | joined |  | {"from": 131, "to": 390, "count": 260} | {"from": 132, "to": 390, "count": 259} |  | pending | False |
| tm-v1-table-items | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 396, "to": 401, "count": 6} | {"from": 397, "to": 402, "count": 6} |  | pending | False |
| tm-v1-commandbar-main | commandbar_summary | commandbar_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 402, "to": 407, "count": 6} | {"from": 403, "to": 408, "count": 6} |  | accepted_probe | True |
| tm-v1-group-main | group_summary | group_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 408, "to": 413, "count": 6} | {"from": 409, "to": 414, "count": 6} |  | pending | False |
| tm-v1-pages-main | pages_summary | pages_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 414, "to": 419, "count": 6} | {"from": 415, "to": 420, "count": 6} |  | accepted_probe | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- Joined rows without accepted replay/probe evidence remain non-accepted protocol mappings.
