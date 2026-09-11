# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-13T13:44:09Z`
- Run id: `tm-v1-ro-batchF`
- Source runtime directory: `runtime\protocol-research\captures\tm-v1-ro-batchF`
- Join status counts: `{"joined": 6}`
- Accepted case ids: `["bf-form-titletext", "bf-form-formname", "bf-form-enable", "bf-field-tooltip", "bf-group-tooltip", "bf-table-tooltip"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bf-form-titletext | form_state | form_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 16, "to": 20, "count": 5} | {"from": 17, "to": 21, "count": 5} |  | accepted_side_channel | True |
| bf-form-formname | form_state | form_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 21, "to": 25, "count": 5} | {"from": 22, "to": 26, "count": 5} |  | accepted_side_channel | True |
| bf-form-enable | form_state | form_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 26, "to": 30, "count": 5} | {"from": 27, "to": 31, "count": 5} |  | accepted_side_channel | True |
| bf-field-tooltip | element_state | element_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 31, "to": 38, "count": 8} | {"from": 32, "to": 39, "count": 8} |  | accepted_side_channel | True |
| bf-group-tooltip | group_summary | group_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 39, "to": 47, "count": 9} | {"from": 40, "to": 48, "count": 9} |  | accepted_side_channel | True |
| bf-table-tooltip | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 48, "to": 58, "count": 11} | {"from": 49, "to": 59, "count": 11} |  | accepted_side_channel | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.
- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.
