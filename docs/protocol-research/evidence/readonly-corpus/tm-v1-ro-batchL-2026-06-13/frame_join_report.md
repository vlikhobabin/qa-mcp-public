# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-13T14:04:12Z`
- Run id: `tm-v1-ro-batchL`
- Source runtime directory: `runtime\protocol-research\captures\tm-v1-ro-batchL`
- Join status counts: `{"joined": 4}`
- Accepted case ids: `["bl-app-findobject", "bl-app-findobjects", "bl-app-getobject", "bl-window-findobjects"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bl-app-findobject | app_state | app_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 16, "to": 21, "count": 6} | {"from": 17, "to": 22, "count": 6} |  | accepted_side_channel | True |
| bl-app-findobjects | app_state | app_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 22, "to": 27, "count": 6} | {"from": 23, "to": 28, "count": 6} |  | accepted_side_channel | True |
| bl-app-getobject | app_state | app_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 28, "to": 33, "count": 6} | {"from": 29, "to": 34, "count": 6} |  | accepted_side_channel | True |
| bl-window-findobjects | window_state | window_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 34, "to": 35, "count": 2} | {"from": 35, "to": 36, "count": 2} |  | accepted_side_channel | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.
- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.
