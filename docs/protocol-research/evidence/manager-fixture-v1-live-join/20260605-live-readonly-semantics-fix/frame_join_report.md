# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-05T12:08:59Z`
- Run id: `20260605-live-readonly-semantics-fix`
- Source runtime directory: `runtime\protocol-research\captures\20260605-live-readonly-semantics-fix`
- Join status counts: `{"joined": 11}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-active-window | active_window | active_window | ok | True | joined | zero_width_expanded_to_1s | {"from": 6, "to": 6, "count": 1} | {"from": 7, "to": 7, "count": 1} |  | pending | False |
| tm-v1-active-form | active_form | active_form | ok | True | joined |  | {"from": 7, "to": 153, "count": 147} | {"from": 8, "to": 154, "count": 147} |  | pending | False |
| tm-v1-form-summary | form_summary | form_summary | failed | True | joined |  | {"from": 154, "to": 300, "count": 147} | {"from": 155, "to": 301, "count": 147} |  | pending | False |
| tm-v1-field-version | element_details | element_details | failed | True | joined |  | {"from": 301, "to": 447, "count": 147} | {"from": 302, "to": 448, "count": 147} |  | pending | False |
| tm-v1-field-string | element_details | element_details | failed | True | joined |  | {"from": 448, "to": 594, "count": 147} | {"from": 449, "to": 595, "count": 147} |  | pending | False |
| tm-v1-checkbox-true | element_state | element_state | ok | True | joined |  | {"from": 595, "to": 741, "count": 147} | {"from": 596, "to": 742, "count": 147} |  | pending | False |
| tm-v1-button-inert | element_state | element_state | ok | True | joined |  | {"from": 742, "to": 884, "count": 143} | {"from": 743, "to": 885, "count": 143} |  | pending | False |
| tm-v1-table-items | table_summary | table_summary | ok | True | joined |  | {"from": 885, "to": 1031, "count": 147} | {"from": 886, "to": 1032, "count": 147} |  | pending | False |
| tm-v1-commandbar-main | commandbar_summary | commandbar_summary | ok | True | joined |  | {"from": 1032, "to": 1178, "count": 147} | {"from": 1033, "to": 1179, "count": 147} |  | pending | False |
| tm-v1-group-main | group_summary | group_summary | ok | True | joined |  | {"from": 1179, "to": 1325, "count": 147} | {"from": 1180, "to": 1326, "count": 147} |  | pending | False |
| tm-v1-pages-main | pages_summary | pages_summary | ok | True | joined |  | {"from": 1326, "to": 1472, "count": 147} | {"from": 1327, "to": 1473, "count": 147} |  | pending | False |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- Joined rows are still not accepted protocol mappings until normalized hashes and replay or direct-probe confirmations are retained.
