# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-05T10:19:00Z`
- Run id: `20260605-live-full-readonly-second-boundary-guard`
- Source runtime directory: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260605-live-full-readonly-second-boundary-guard`
- Join status counts: `{"joined": 11}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-active-window | active_window | active_window | ok | True | joined | zero_width_expanded_to_1s | {"from": 1, "to": 6, "count": 6} | {"from": 1, "to": 7, "count": 7} |  | pending | False |
| tm-v1-active-form | active_form | active_form | ok | True | joined |  | {"from": 7, "to": 150, "count": 144} | {"from": 8, "to": 151, "count": 144} |  | pending | False |
| tm-v1-form-summary | form_summary | form_summary | ok | True | joined |  | {"from": 151, "to": 296, "count": 146} | {"from": 152, "to": 297, "count": 146} |  | pending | False |
| tm-v1-field-version | element_details | element_details | ok | True | joined |  | {"from": 297, "to": 441, "count": 145} | {"from": 298, "to": 442, "count": 145} |  | pending | False |
| tm-v1-field-string | element_details | element_details | ok | True | joined |  | {"from": 442, "to": 586, "count": 145} | {"from": 443, "to": 587, "count": 145} |  | pending | False |
| tm-v1-checkbox-true | element_state | element_state | ok | True | joined |  | {"from": 587, "to": 729, "count": 143} | {"from": 588, "to": 730, "count": 143} |  | pending | False |
| tm-v1-button-inert | element_state | element_state | ok | True | joined |  | {"from": 730, "to": 871, "count": 142} | {"from": 731, "to": 872, "count": 142} |  | pending | False |
| tm-v1-table-items | table_summary | table_summary | ok | True | joined |  | {"from": 872, "to": 1014, "count": 143} | {"from": 873, "to": 1015, "count": 143} |  | pending | False |
| tm-v1-commandbar-main | commandbar_summary | commandbar_summary | ok | True | joined |  | {"from": 1015, "to": 1155, "count": 141} | {"from": 1016, "to": 1156, "count": 141} |  | pending | False |
| tm-v1-group-main | group_summary | group_summary | ok | True | joined |  | {"from": 1156, "to": 1285, "count": 130} | {"from": 1157, "to": 1286, "count": 130} |  | pending | False |
| tm-v1-pages-main | pages_summary | pages_summary | ok | True | joined |  | {"from": 1286, "to": 1408, "count": 123} | {"from": 1287, "to": 1409, "count": 123} |  | pending | False |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- Joined rows are still not accepted protocol mappings until normalized hashes and replay or direct-probe confirmations are retained.
