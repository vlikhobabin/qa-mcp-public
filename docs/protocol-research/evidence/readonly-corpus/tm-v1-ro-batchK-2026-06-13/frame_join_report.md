# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-13T14:01:32Z`
- Run id: `tm-v1-ro-batchK`
- Source runtime directory: `runtime\protocol-research\captures\tm-v1-ro-batchK`
- Join status counts: `{"joined": 8}`
- Accepted case ids: `["bk-field-findobjects", "bk-field-findobject", "bk-group-findobjects", "bk-group-findobject", "bk-table-findobjects", "bk-table-findobject", "bk-group-getobject", "bk-table-getobject"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bk-field-findobjects | element_state | element_state | ok | True | joined |  | {"from": 16, "to": 25, "count": 10} | {"from": 17, "to": 26, "count": 10} |  | accepted_side_channel | True |
| bk-field-findobject | element_state | element_state | ok | True | joined |  | {"from": 27, "to": 36, "count": 10} | {"from": 28, "to": 37, "count": 10} |  | accepted_side_channel | True |
| bk-group-findobjects | group_summary | group_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 38, "to": 52, "count": 15} | {"from": 39, "to": 53, "count": 15} |  | accepted_side_channel | True |
| bk-group-findobject | group_summary | group_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 53, "to": 67, "count": 15} | {"from": 54, "to": 68, "count": 15} |  | accepted_side_channel | True |
| bk-table-findobjects | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 68, "to": 84, "count": 17} | {"from": 69, "to": 85, "count": 17} |  | accepted_side_channel | True |
| bk-table-findobject | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 85, "to": 101, "count": 17} | {"from": 86, "to": 102, "count": 17} |  | accepted_side_channel | True |
| bk-group-getobject | group_summary | group_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 102, "to": 116, "count": 15} | {"from": 103, "to": 117, "count": 15} |  | accepted_side_channel | True |
| bk-table-getobject | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 117, "to": 133, "count": 17} | {"from": 118, "to": 134, "count": 17} |  | accepted_side_channel | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.
- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.
