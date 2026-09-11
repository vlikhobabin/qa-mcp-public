# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-05T12:25:56Z`
- Run id: `20260605-live-readonly-findobject-selected`
- Source runtime directory: `runtime\protocol-research\captures\20260605-live-readonly-findobject-selected`
- Join status counts: `{"joined": 2}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-form-summary | form_summary | form_summary | failed | True | joined |  | {"from": 6, "to": 161, "count": 156} | {"from": 7, "to": 162, "count": 156} |  | pending | False |
| tm-v1-field-version | element_details | element_details | failed | True | joined |  | {"from": 162, "to": 317, "count": 156} | {"from": 163, "to": 318, "count": 156} |  | pending | False |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- Joined rows are still not accepted protocol mappings until normalized hashes and replay or direct-probe confirmations are retained.
