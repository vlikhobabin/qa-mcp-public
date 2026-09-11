# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-13T09:48:42Z`
- Run id: `tm-v1-ro-batchD`
- Source runtime directory: `runtime\protocol-research\captures\tm-v1-ro-batchD`
- Join status counts: `{"joined": 4}`
- Accepted case ids: `["bd-button-check", "bd-table-mode", "bd-table-canexpand", "bd-table-expanded"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bd-button-check | element_state | element_state | ok | True | joined |  | {"from": 16, "to": 445, "count": 430} | {"from": 17, "to": 446, "count": 430} |  | accepted_side_channel | True |
| bd-table-mode | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 453, "to": 462, "count": 10} | {"from": 454, "to": 463, "count": 10} |  | accepted_side_channel | True |
| bd-table-canexpand | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 463, "to": 472, "count": 10} | {"from": 464, "to": 473, "count": 10} |  | accepted_side_channel | True |
| bd-table-expanded | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 473, "to": 482, "count": 10} | {"from": 474, "to": 483, "count": 10} |  | accepted_side_channel | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.
- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.
