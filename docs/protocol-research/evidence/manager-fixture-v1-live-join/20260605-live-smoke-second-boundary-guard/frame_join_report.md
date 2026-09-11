# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-05T08:51:11Z`
- Run id: `20260605-live-smoke-second-boundary-guard`
- Source runtime directory: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260605-live-smoke-second-boundary-guard`
- Join status counts: `{"joined": 3}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-active-window | active_window | active_window | ok | True | joined | zero_width_expanded_to_1s | {"from": 4, "to": 6, "count": 3} | {"from": 4, "to": 7, "count": 4} |  | pending | False |
| tm-v1-active-form | active_form | active_form | ok | True | joined |  | {"from": 7, "to": 145, "count": 139} | {"from": 8, "to": 146, "count": 139} |  | pending | False |
| tm-v1-field-version | element_details | element_details | ok | True | joined |  | {"from": 146, "to": 287, "count": 142} | {"from": 147, "to": 288, "count": 142} |  | pending | False |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- Joined rows are still not accepted protocol mappings until normalized hashes and replay or direct-probe confirmations are retained.
