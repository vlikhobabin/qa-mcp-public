# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-13T13:58:16Z`
- Run id: `tm-v1-ro-batchJ`
- Source runtime directory: `runtime\protocol-research\captures\tm-v1-ro-batchJ`
- Join status counts: `{"joined": 4}`
- Accepted case ids: `["bj-form-parent", "bj-form-getobject", "bj-form-findobjects", "bj-form-currentitem"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| bj-form-parent | form_state | form_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 16, "to": 24, "count": 9} | {"from": 17, "to": 25, "count": 9} |  | accepted_side_channel | True |
| bj-form-getobject | form_state | form_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 25, "to": 33, "count": 9} | {"from": 26, "to": 34, "count": 9} |  | accepted_side_channel | True |
| bj-form-findobjects | form_state | form_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 34, "to": 42, "count": 9} | {"from": 35, "to": 43, "count": 9} |  | accepted_side_channel | True |
| bj-form-currentitem | form_state | form_state | ok | True | joined | zero_width_expanded_to_1s | {"from": 43, "to": 51, "count": 9} | {"from": 44, "to": 52, "count": 9} |  | accepted_side_channel | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.
- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.
