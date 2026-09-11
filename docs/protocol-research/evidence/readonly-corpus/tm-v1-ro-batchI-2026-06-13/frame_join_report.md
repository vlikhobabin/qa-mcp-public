# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-13T13:53:34Z`
- Run id: `tm-v1-ro-batchI`
- Source runtime directory: `runtime\protocol-research\captures\tm-v1-ro-batchI`
- Join status counts: `{"joined": 9}`
- Accepted case ids: `["bi-field-parent", "bi-field-commandbar", "bi-field-contextmenu", "bi-group-parent", "bi-group-commandbar", "bi-group-contextmenu", "bi-table-parent", "bi-table-commandbar", "bi-table-contextmenu"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bi-field-parent | element_state | element_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 16, "to": 26, "count": 11} | {"from": 17, "to": 27, "count": 11} |  | accepted_side_channel | True |
| bi-field-commandbar | element_state | element_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 27, "to": 37, "count": 11} | {"from": 28, "to": 38, "count": 11} |  | accepted_side_channel | True |
| bi-field-contextmenu | element_state | element_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 38, "to": 48, "count": 11} | {"from": 39, "to": 49, "count": 11} |  | accepted_side_channel | True |
| bi-group-parent | group_summary | group_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 49, "to": 60, "count": 12} | {"from": 50, "to": 61, "count": 12} |  | accepted_side_channel | True |
| bi-group-commandbar | group_summary | group_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 61, "to": 72, "count": 12} | {"from": 62, "to": 73, "count": 12} |  | accepted_side_channel | True |
| bi-group-contextmenu | group_summary | group_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 73, "to": 84, "count": 12} | {"from": 74, "to": 85, "count": 12} |  | accepted_side_channel | True |
| bi-table-parent | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 85, "to": 98, "count": 14} | {"from": 86, "to": 99, "count": 14} |  | accepted_side_channel | True |
| bi-table-commandbar | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 99, "to": 112, "count": 14} | {"from": 100, "to": 113, "count": 14} |  | accepted_side_channel | True |
| bi-table-contextmenu | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 113, "to": 126, "count": 14} | {"from": 114, "to": 127, "count": 14} |  | accepted_side_channel | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.
- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.
