# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-13T14:07:14Z`
- Run id: `tm-v1-ro-batchM`
- Source runtime directory: `runtime\protocol-research\captures\tm-v1-ro-batchM`
- Join status counts: `{"joined": 5}`
- Accepted case ids: `["bm-field-titleshown", "bm-pages-currentpage", "bm-table-selrows", "bm-table-currentitem", "bm-app-waitobj"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bm-field-titleshown | element_state | element_state | ok | True | joined |  | {"from": 16, "to": 25, "count": 10} | {"from": 17, "to": 26, "count": 10} |  | accepted_side_channel | True |
| bm-pages-currentpage | pages_summary | pages_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 28, "to": 43, "count": 16} | {"from": 29, "to": 44, "count": 16} |  | accepted_side_channel | True |
| bm-table-selrows | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 44, "to": 62, "count": 19} | {"from": 45, "to": 63, "count": 19} |  | accepted_side_channel | True |
| bm-table-currentitem | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 63, "to": 81, "count": 19} | {"from": 64, "to": 82, "count": 19} |  | accepted_side_channel | True |
| bm-app-waitobj | app_state | app_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 82, "to": 88, "count": 7} | {"from": 83, "to": 89, "count": 7} |  | accepted_side_channel | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.
- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.
