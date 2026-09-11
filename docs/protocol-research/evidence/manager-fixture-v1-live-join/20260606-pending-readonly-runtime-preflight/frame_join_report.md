# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-06T16:13:39Z`
- Run id: `20260606-pending-readonly-runtime-preflight`
- Source runtime directory: `runtime\protocol-research\captures\20260606-pending-readonly-runtime-preflight`
- Join status counts: `{"unresolved": 1}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-active-window | active_window | active_window | not_run | False | unresolved |  |  |  | no_before_event | not_run | False |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- Joined rows without accepted replay/probe evidence remain non-accepted protocol mappings.
