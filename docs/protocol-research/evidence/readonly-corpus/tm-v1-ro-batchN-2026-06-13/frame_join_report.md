# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-13T14:09:59Z`
- Run id: `tm-v1-ro-batchN`
- Source runtime directory: `runtime\protocol-research\captures\tm-v1-ro-batchN`
- Join status counts: `{"joined": 3}`
- Accepted case ids: `["bn-form-defaultbutton", "bn-form-waitclosing", "bn-table-celltext"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bn-form-defaultbutton | form_state | form_state | ok | True | joined |  | {"from": 16, "to": 1386, "count": 1371} | {"from": 17, "to": 1386, "count": 1370} |  | accepted_side_channel | True |
| bn-form-waitclosing | form_state | form_state | ok | True | joined |  | {"from": 1388, "to": 2671, "count": 1284} | {"from": 1389, "to": 2672, "count": 1284} |  | accepted_side_channel | True |
| bn-table-celltext | table_summary | table_summary | ok | True | joined | zero_width_expanded_to_1s | {"from": 2674, "to": 2693, "count": 20} | {"from": 2675, "to": 2694, "count": 20} |  | accepted_side_channel | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.
- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.
