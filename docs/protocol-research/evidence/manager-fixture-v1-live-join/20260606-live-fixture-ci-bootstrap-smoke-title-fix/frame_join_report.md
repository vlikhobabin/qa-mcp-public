# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-06T09:14:40Z`
- Run id: `20260606-live-fixture-ci-bootstrap-smoke-title-fix`
- Source runtime directory: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260606-live-fixture-ci-bootstrap-smoke-title-fix`
- Join status counts: `{"joined": 3}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-active-form | active_form | active_form | ok | True | joined | zero_width_expanded_to_1s | {"from": 16, "to": 16, "count": 1} | {"from": 17, "to": 17, "count": 1} |  | pending | False |
| tm-v1-form-summary | form_summary | form_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 17, "to": 19, "count": 3} | {"from": 18, "to": 20, "count": 3} |  | pending | False |
| tm-v1-field-version | element_details | element_details | ok | True | joined | zero_width_expanded_to_1s | {"from": 20, "to": 22, "count": 3} | {"from": 21, "to": 23, "count": 3} |  | pending | False |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- Joined rows are still not accepted protocol mappings until normalized hashes and replay or direct-probe confirmations are retained.
