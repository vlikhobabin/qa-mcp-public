# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-06T19:16:30Z`
- Run id: `20260606-side-channel-count-contracts-focused-proof`
- Source runtime directory: `runtime\protocol-research\captures\20260606-side-channel-count-contracts-focused-proof`
- Join status counts: `{"joined": 2}`
- Accepted case ids: `["tm-v1-diag-command-interface-dump", "tm-v1-diag-window-children"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-diag-command-interface-dump | diagnostic_command_interface_dump | diagnostic_command_interface_dump | ok | True | joined | zero_width_expanded_to_1s | {"from": 16, "to": 18, "count": 3} | {"from": 17, "to": 19, "count": 3} |  | accepted_side_channel | True |
| tm-v1-diag-window-children | diagnostic_window_children | diagnostic_window_children | ok | True | joined | zero_width_expanded_to_1s | {"from": 19, "to": 20, "count": 2} | {"from": 20, "to": 21, "count": 2} |  | accepted_side_channel | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- Joined rows without accepted replay/probe evidence remain non-accepted protocol mappings.
