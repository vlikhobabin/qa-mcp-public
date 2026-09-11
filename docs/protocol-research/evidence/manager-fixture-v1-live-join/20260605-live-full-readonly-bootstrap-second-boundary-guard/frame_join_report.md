# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-05T11:06:18Z`
- Run id: `20260605-live-full-readonly-bootstrap-second-boundary-guard`
- Source runtime directory: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260605-live-full-readonly-bootstrap-second-boundary-guard`
- Join status counts: `{"joined": 11}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-active-window | active_window | active_window | ok | True | joined | zero_width_expanded_to_1s | {"from": 6, "to": 6, "count": 1} | {"from": 7, "to": 7, "count": 1} |  | pending | False |
| tm-v1-active-form | active_form | active_form | ok | True | joined |  | {"from": 7, "to": 147, "count": 141} | {"from": 8, "to": 148, "count": 141} |  | pending | False |
| tm-v1-form-summary | form_summary | form_summary | ok | True | joined |  | {"from": 148, "to": 288, "count": 141} | {"from": 149, "to": 289, "count": 141} |  | pending | False |
| tm-v1-field-version | element_details | element_details | ok | True | joined |  | {"from": 289, "to": 414, "count": 126} | {"from": 290, "to": 415, "count": 126} |  | pending | False |
| tm-v1-field-string | element_details | element_details | ok | True | joined |  | {"from": 415, "to": 555, "count": 141} | {"from": 416, "to": 556, "count": 141} |  | pending | False |
| tm-v1-checkbox-true | element_state | element_state | ok | True | joined |  | {"from": 556, "to": 696, "count": 141} | {"from": 557, "to": 697, "count": 141} |  | pending | False |
| tm-v1-button-inert | element_state | element_state | ok | True | joined |  | {"from": 697, "to": 837, "count": 141} | {"from": 698, "to": 838, "count": 141} |  | pending | False |
| tm-v1-table-items | table_summary | table_summary | ok | True | joined |  | {"from": 838, "to": 978, "count": 141} | {"from": 839, "to": 979, "count": 141} |  | pending | False |
| tm-v1-commandbar-main | commandbar_summary | commandbar_summary | ok | True | joined |  | {"from": 979, "to": 1119, "count": 141} | {"from": 980, "to": 1120, "count": 141} |  | pending | False |
| tm-v1-group-main | group_summary | group_summary | ok | True | joined |  | {"from": 1120, "to": 1261, "count": 142} | {"from": 1121, "to": 1262, "count": 142} |  | pending | False |
| tm-v1-pages-main | pages_summary | pages_summary | ok | True | joined |  | {"from": 1262, "to": 1402, "count": 141} | {"from": 1263, "to": 1403, "count": 141} |  | pending | False |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- Joined rows are still not accepted protocol mappings until normalized hashes and replay or direct-probe confirmations are retained.
