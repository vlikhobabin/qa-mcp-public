# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-06T07:11:57Z`
- Run id: `20260606-live-diag-addressing-smoke`
- Source runtime directory: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260606-live-diag-addressing-smoke`
- Join status counts: `{"joined": 5}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-diag-window-children | diagnostic_window_children | diagnostic_window_children | ok | True | joined | zero_width_expanded_to_1s | {"from": 6, "to": 7, "count": 2} | {"from": 7, "to": 8, "count": 2} |  | pending | False |
| tm-v1-diag-window-find-form-marker | diagnostic_window_find_form_marker | diagnostic_window_find_form_marker | failed | True | joined |  | {"from": 8, "to": 349, "count": 342} | {"from": 9, "to": 349, "count": 341} |  | pending | False |
| tm-v1-diag-window-get-form-path | diagnostic_window_get_form_path | diagnostic_window_get_form_path | failed | True | joined |  | {"from": 351, "to": 682, "count": 332} | {"from": 352, "to": 682, "count": 331} |  | pending | False |
| tm-v1-diag-window-find-field-marker | diagnostic_window_find_field_marker | diagnostic_window_find_field_marker | failed | True | joined |  | {"from": 684, "to": 1032, "count": 349} | {"from": 685, "to": 1033, "count": 349} |  | pending | False |
| tm-v1-diag-form-find-field-marker | diagnostic_form_find_field_marker | diagnostic_form_find_field_marker | failed | True | joined |  | {"from": 1034, "to": 1373, "count": 340} | {"from": 1035, "to": 1373, "count": 339} |  | pending | False |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- Joined rows are still not accepted protocol mappings until normalized hashes and replay or direct-probe confirmations are retained.
