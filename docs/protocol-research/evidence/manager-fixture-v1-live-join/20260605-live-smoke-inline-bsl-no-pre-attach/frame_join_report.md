# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-05T08:09:58Z`
- Run id: `20260605-live-smoke-inline-bsl-no-pre-attach`
- Source runtime directory: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260605-live-smoke-inline-bsl-no-pre-attach`
- Join status counts: `{"unresolved": 3}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-active-window | active_window | active_window | ok | True | unresolved |  |  | no_chunks_in_case_window | not_run | False |
| tm-v1-active-form | active_form | active_form | failed | True | unresolved |  |  | no_chunks_in_case_window | not_run | False |
| tm-v1-field-version | element_details | element_details | ok | True | unresolved |  |  | no_chunks_in_case_window | not_run | False |

## Notes

- `joined` requires reviewed frame or chunk ranges. This retained run has no joined cases.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- No normalized hashes or replay/direct-probe confirmations are present in this report.
