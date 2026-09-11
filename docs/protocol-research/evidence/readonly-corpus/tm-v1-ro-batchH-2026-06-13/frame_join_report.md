# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-13T13:50:23Z`
- Run id: `tm-v1-ro-batchH`
- Source runtime directory: `runtime\protocol-research\captures\tm-v1-ro-batchH`
- Join status counts: `{"joined": 4}`
- Accepted case ids: `["bh-app-maxexec", "bh-app-perf", "bh-app-errorinfo", "bh-app-children"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bh-app-maxexec | app_state | app_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 16, "to": 18, "count": 3} | {"from": 17, "to": 19, "count": 3} |  | accepted_side_channel | True |
| bh-app-perf | app_state | app_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 19, "to": 21, "count": 3} | {"from": 20, "to": 22, "count": 3} |  | accepted_side_channel | True |
| bh-app-errorinfo | app_state | app_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 22, "to": 24, "count": 3} | {"from": 23, "to": 25, "count": 3} |  | accepted_side_channel | True |
| bh-app-children | app_state | app_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 25, "to": 27, "count": 3} | {"from": 26, "to": 28, "count": 3} |  | accepted_side_channel | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.
- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.
