# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-05T11:06:18Z`
- Run id: `20260605-live-full-readonly-repeat-second-boundary-guard`
- Source runtime directory: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260605-live-full-readonly-repeat-second-boundary-guard`
- Join status counts: `{"joined": 11}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-active-window | active_window | active_window | ok | True | joined | zero_width_expanded_to_1s | {"from": 6, "to": 6, "count": 1} | {"from": 7, "to": 7, "count": 1} |  | pending | False |
| tm-v1-active-form | active_form | active_form | ok | True | joined |  | {"from": 7, "to": 150, "count": 144} | {"from": 8, "to": 151, "count": 144} |  | pending | False |
| tm-v1-form-summary | form_summary | form_summary | ok | True | joined |  | {"from": 151, "to": 294, "count": 144} | {"from": 152, "to": 295, "count": 144} |  | pending | False |
| tm-v1-field-version | element_details | element_details | ok | True | joined |  | {"from": 295, "to": 438, "count": 144} | {"from": 296, "to": 439, "count": 144} |  | pending | False |
| tm-v1-field-string | element_details | element_details | ok | True | joined |  | {"from": 439, "to": 582, "count": 144} | {"from": 440, "to": 583, "count": 144} |  | pending | False |
| tm-v1-checkbox-true | element_state | element_state | ok | True | joined |  | {"from": 583, "to": 727, "count": 145} | {"from": 584, "to": 728, "count": 145} |  | pending | False |
| tm-v1-button-inert | element_state | element_state | ok | True | joined |  | {"from": 728, "to": 871, "count": 144} | {"from": 729, "to": 872, "count": 144} |  | pending | False |
| tm-v1-table-items | table_summary | table_summary | ok | True | joined |  | {"from": 872, "to": 1016, "count": 145} | {"from": 873, "to": 1017, "count": 145} |  | pending | False |
| tm-v1-commandbar-main | commandbar_summary | commandbar_summary | ok | True | joined |  | {"from": 1017, "to": 1162, "count": 146} | {"from": 1018, "to": 1163, "count": 146} |  | pending | False |
| tm-v1-group-main | group_summary | group_summary | ok | True | joined |  | {"from": 1163, "to": 1309, "count": 147} | {"from": 1164, "to": 1310, "count": 147} |  | pending | False |
| tm-v1-pages-main | pages_summary | pages_summary | ok | True | joined |  | {"from": 1310, "to": 1456, "count": 147} | {"from": 1311, "to": 1457, "count": 147} |  | pending | False |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- Joined rows are still not accepted protocol mappings until normalized hashes and replay or direct-probe confirmations are retained.
