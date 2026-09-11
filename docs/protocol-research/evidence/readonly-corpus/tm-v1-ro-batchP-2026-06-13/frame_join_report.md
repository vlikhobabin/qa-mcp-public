# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-13T14:55:20Z`
- Run id: `tm-v1-ro-batchP`
- Source runtime directory: `runtime\protocol-research\captures\tm-v1-ro-batchP`
- Join status counts: `{"joined": 2}`
- Accepted case ids: `["bp-form-choicelist"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bp-form-choicelist | form_state | form_state | ok | True | joined |  | {"from": 16, "to": 750, "count": 735} | {"from": 17, "to": 750, "count": 734} |  | accepted_side_channel | True |
| bp-field-getobject | element_state | element_state | ok | True | joined |  | {"from": 756, "to": 765, "count": 10} | {"from": 757, "to": 766, "count": 10} |  | pending | False |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.
- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.
