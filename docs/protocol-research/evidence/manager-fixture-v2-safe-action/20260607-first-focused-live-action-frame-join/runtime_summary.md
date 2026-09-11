# Manager Fixture V2 Safe-Action Report

- Generated at: `2026-06-07T19:33:22Z`
- Capture id: `20260607-first-focused-v2-safe-action-live-runner-2`
- Row count: `2`
- Status counts: `{"success": 2}`
- Raw output policy: raw TCP streams, full event logs, platform logs and generated replay output stay under ignored runtime/protocol-research paths

## Rows

| case | validation | action status | replay | action frames | background frames | recovery frames | result markers | non-accepted reasons |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| safe-switch-fixture-page-b | accepted_for_capture | success | pending | {"manager_to_client": {"from": 59, "to": 61, "count": 3}, "client_to_manager": {"from": 60, "to": 62, "count": 3}} | [{"manager_to_client": {"from": 55, "to": 62, "count": 5}, "client_to_manager": {"from": 56, "to": 63, "count": 5}}] | {"manager_to_client": {"from": 63, "to": 65, "count": 3}, "client_to_manager": {"from": 64, "to": 66, "count": 3}} | ["PF_PAGES_MAIN", "PF_PAGE_B", "PF_SELECTED_PAGE"] | ["replay_or_probe_unavailable"] |
| safe-focus-existing-edit-string | accepted_for_capture | success | pending | {"manager_to_client": {"from": 70, "to": 71, "count": 2}, "client_to_manager": {"from": 71, "to": 72, "count": 2}} | [{"manager_to_client": {"from": 66, "to": 72, "count": 5}, "client_to_manager": {"from": 67, "to": 73, "count": 5}}] | {"manager_to_client": {"from": 73, "to": 74, "count": 2}, "client_to_manager": {"from": 74, "to": 75, "count": 2}} | ["PF_EDIT_STRING", "PF_EDIT_STRING_VALUE"] | ["replay_or_probe_unavailable"] |

## Notes

- V2 action rows stay non-accepted until replay/probe or typed contract proof is retained.
- Phase events are side-channel evidence and do not inject markers into TCP traffic.
- Raw captures and generated replay payloads remain under ignored runtime paths.
