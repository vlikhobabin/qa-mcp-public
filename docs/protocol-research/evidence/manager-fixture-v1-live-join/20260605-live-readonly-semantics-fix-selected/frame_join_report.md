# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-05T12:15:16Z`
- Run id: `20260605-live-readonly-semantics-fix-selected`
- Source runtime directory: `runtime\protocol-research\captures\20260605-live-readonly-semantics-fix-selected`
- Join status counts: `{"joined": 2}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-form-summary | form_summary | form_summary | failed | True | joined |  | {"from": 6, "to": 152, "count": 147} | {"from": 7, "to": 153, "count": 147} |  | pending | False |
| tm-v1-field-version | element_details | element_details | failed | True | joined |  | {"from": 153, "to": 299, "count": 147} | {"from": 154, "to": 300, "count": 147} |  | pending | False |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- Joined rows are still not accepted protocol mappings until normalized hashes and replay or direct-probe confirmations are retained.
