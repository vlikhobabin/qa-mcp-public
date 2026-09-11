# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-05T08:23:10Z`
- Run id: `20260605-live-smoke-inline-bsl-utc`
- Source runtime directory: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260605-live-smoke-inline-bsl-utc`
- Join status counts: `{"joined": 3}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-active-window | active_window | active_window | ok | True | joined | {"from": 1, "to": 10, "count": 10} | {"from": 1, "to": 11, "count": 11} |  | pending | False |
| tm-v1-active-form | active_form | active_form | failed | True | joined | {"from": 1, "to": 147, "count": 147} | {"from": 1, "to": 148, "count": 148} |  | pending | False |
| tm-v1-field-version | element_details | element_details | ok | True | joined | {"from": 148, "to": 294, "count": 147} | {"from": 149, "to": 295, "count": 147} |  | pending | False |

## Notes

- `joined` requires reviewed frame or chunk ranges. This retained run has no joined cases.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- No normalized hashes or replay/direct-probe confirmations are present in this report.
