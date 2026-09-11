# Manager Fixture V2 Safe-Action Report

- Generated at: `2026-06-07T17:33:09Z`
- Capture id: `recovery-sequence`
- Row count: `7`
- Status counts: `{"blocked": 1, "rejected": 1, "success": 5}`
- Raw output policy: raw TCP streams, full event logs, platform logs and generated replay output stay under ignored runtime/protocol-research paths

## Rows

| case | validation | action status | replay | action frames | background frames | recovery frames | result markers | non-accepted reasons |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| safe-activate-existing-window | accepted_for_capture | success | pending |  | [] |  | ["PF_FORM_MAIN", "PF_STATE_INITIAL"] | ["missing_action_frame_range", "replay_or_probe_unavailable"] |
| safe-focus-existing-edit-string | accepted_for_capture | success | pending |  | [] |  | ["PF_EDIT_STRING", "PF_EDIT_STRING_VALUE"] | ["missing_action_frame_range", "replay_or_probe_unavailable"] |
| safe-switch-fixture-page-b | accepted_for_capture | success | pending |  | [] |  | ["PF_PAGES_MAIN", "PF_PAGE_B", "PF_SELECTED_PAGE"] | ["missing_action_frame_range", "replay_or_probe_unavailable"] |
| safe-select-local-row-002 | accepted_for_capture | success | pending |  | [] |  | ["PF_TABLE_ITEMS", "PF_ROW_002", "PF_SELECTED_ROW_MARKER"] | ["missing_action_frame_range", "replay_or_probe_unavailable"] |
| safe-expand-commandbar-main | accepted_for_capture | success | pending |  | [] |  | ["PF_COMMAND_BAR_MAIN", "PF_COMMAND_POPUP"] | ["missing_action_frame_range", "replay_or_probe_unavailable"] |
| blocked-expand-popup-child | blocked | blocked | blocked |  | [] |  | [] | ["missing_action_frame_range", "missing_action_result_markers", "missing_recovery_frame_range_or_known_state", "missing_recovery_result", "non_executable_status:blocked"] |
| rejected-click-inert-button | rejected | rejected | rejected |  | [] |  | [] | ["missing_action_frame_range", "missing_action_result_markers", "missing_recovery_frame_range_or_known_state", "missing_recovery_result", "unsupported_action_family:business_command_click"] |

## Notes

- V2 action rows stay non-accepted until replay/probe or typed contract proof is retained.
- Phase events are side-channel evidence and do not inject markers into TCP traffic.
- Raw captures and generated replay payloads remain under ignored runtime paths.
