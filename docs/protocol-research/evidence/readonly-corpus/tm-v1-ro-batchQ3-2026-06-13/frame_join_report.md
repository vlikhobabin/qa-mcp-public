# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-13T15:31:57Z`
- Run id: `tm-v1-ro-batchQ3`
- Source runtime directory: `runtime\protocol-research\captures\tm-v1-ro-batchQ3`
- Join status counts: `{"joined": 1}`
- Accepted case ids: `["bq-window-usermessages"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bq-window-usermessages | window_messages | window_messages | ok | True | joined | zero_width_expanded_to_1s | {"from": 16, "to": 21, "count": 6} | {"from": 17, "to": 22, "count": 6} |  | accepted_side_channel | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.
- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.
