# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-13T09:33:56Z`
- Run id: `tm-v1-ro-batchC3`
- Source runtime directory: `runtime\protocol-research\captures\tm-v1-ro-batchC3`
- Join status counts: `{"joined": 4}`
- Accepted case ids: `["ro-field-readonly", "ro-group-readonly", "ro-table-readonly", "ro-group-opened"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ro-field-readonly | element_state | element_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 16, "to": 21, "count": 6} | {"from": 17, "to": 22, "count": 6} |  | accepted_side_channel | True |
| ro-group-readonly | group_summary | group_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 22, "to": 29, "count": 8} | {"from": 23, "to": 30, "count": 8} |  | accepted_side_channel | True |
| ro-table-readonly | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 30, "to": 36, "count": 7} | {"from": 31, "to": 37, "count": 7} |  | accepted_side_channel | True |
| ro-group-opened | group_summary | group_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 37, "to": 44, "count": 8} | {"from": 38, "to": 45, "count": 8} |  | accepted_side_channel | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.
- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.
