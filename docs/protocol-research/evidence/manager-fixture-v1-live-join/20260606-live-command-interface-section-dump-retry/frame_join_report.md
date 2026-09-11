# Manager Fixture V1 Frame Join Report

- Generated at: `2026-06-06T09:14:40Z`
- Run id: `20260606-live-command-interface-section-dump-retry`
- Source runtime directory: `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp\runtime\protocol-research\captures\20260606-live-command-interface-section-dump-retry`
- Join status counts: `{"joined": 1}`
- Accepted case ids: `[]`

## Cases

| case | command | kind | result | event | join | time adjustment | manager chunks | client chunks | unresolved reason | replay | accepted |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| tm-v1-diag-command-interface-section-dump | diagnostic_command_interface_section_dump | diagnostic_command_interface_section_dump | ok | True | joined | zero_width_expanded_to_1s | {"from": 6, "to": 16, "count": 11} | {"from": 7, "to": 17, "count": 11} |  | pending | False |

## Notes

- `joined` means side-channel command windows were matched to proxy chunk ranges.
- `blocked` means the retained run did not emit a side-channel event for that catalog command.
- `unresolved` means a side-channel event exists but frame/chunk evidence is unavailable or unreviewed.
- Joined rows are still not accepted protocol mappings until normalized hashes and replay or direct-probe confirmations are retained.
