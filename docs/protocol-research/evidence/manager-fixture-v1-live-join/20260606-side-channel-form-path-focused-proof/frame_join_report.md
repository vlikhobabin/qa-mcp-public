# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-06T19:29:44Z`
- Run id: `20260606-side-channel-form-path-focused-proof`
- Source runtime directory: `runtime\protocol-research\captures\20260606-side-channel-form-path-focused-proof`
- Join status counts: `{"joined": 1}`
- Accepted case ids: `["tm-v1-diag-window-get-form-path"]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-diag-window-get-form-path | diagnostic_window_get_form_path | diagnostic_window_get_form_path | ok | True | joined |  | {"from": 16, "to": 326, "count": 311} | {"from": 17, "to": 326, "count": 310} |  | accepted_side_channel | True |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- `accepted_probe` means retained replay/probe evidence matched the joined manager frame range and normalized hash.
- `accepted_side_channel` means the manager harness result preview matched a typed side-channel contract while frame range and normalized hash evidence were retained.
- Joined rows without accepted replay/probe or side-channel evidence remain non-accepted protocol mappings.
