# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-13T13:47:13Z`
- Run id: `tm-v1-ro-batchG`
- Source runtime directory: `runtime\protocol-research\captures\tm-v1-ro-batchG`
- Join status counts: `{"joined": 4}`
- Accepted case ids: `["bg-window-caption", "bg-window-url", "bg-window-homepage", "bg-window-ismain"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bg-window-caption | window_state | window_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 16, "to": 16, "count": 1} | {"from": 17, "to": 17, "count": 1} |  | accepted_side_channel | True |
| bg-window-url | window_state | window_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 17, "to": 17, "count": 1} | {"from": 18, "to": 18, "count": 1} |  | accepted_side_channel | True |
| bg-window-homepage | window_state | window_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 18, "to": 18, "count": 1} | {"from": 19, "to": 19, "count": 1} |  | accepted_side_channel | True |
| bg-window-ismain | window_state | window_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 19, "to": 19, "count": 1} | {"from": 20, "to": 20, "count": 1} |  | accepted_side_channel | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.
- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.
