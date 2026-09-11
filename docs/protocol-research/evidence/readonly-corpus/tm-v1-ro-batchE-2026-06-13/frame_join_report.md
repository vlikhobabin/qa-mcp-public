# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-13T13:40:37Z`
- Run id: `tm-v1-ro-batchE`
- Source runtime directory: `runtime\protocol-research\captures\tm-v1-ro-batchE`
- Join status counts: `{"joined": 2}`
- Accepted case ids: `["be-form-readonly", "be-form-modified"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| be-form-readonly | form_state | form_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 16, "to": 19, "count": 4} | {"from": 17, "to": 20, "count": 4} |  | accepted_side_channel | True |
| be-form-modified | form_state | form_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 20, "to": 23, "count": 4} | {"from": 21, "to": 24, "count": 4} |  | accepted_side_channel | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.
- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.
