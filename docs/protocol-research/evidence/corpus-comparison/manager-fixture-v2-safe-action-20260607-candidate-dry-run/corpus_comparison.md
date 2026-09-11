# Protocol Corpus Repeatability Report

- Generated at: `2026-06-07T17:33:36Z`
- Input count: `1`
- Case count: `7`
- Classification counts: `{"blocked": 1, "pending": 5, "rejected": 1}`
- Stable case ids: `[]`
- Accepted case ids: `[]`
- Gap case ids: `["blocked-expand-popup-child", "rejected-click-inert-button", "safe-activate-existing-window", "safe-expand-commandbar-main", "safe-focus-existing-edit-string", "safe-select-local-row-002", "safe-switch-fixture-page-b"]`
- Normalizer investigation candidates: `[]`

## Inputs

| index | capture ids | cases | path |
| --- | --- | --- | --- |
| 0 | ["recovery-sequence"] | 7 | docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-candidate-dry-run/corpus_cases.jsonl |

## Cases

| case | classification | precise reasons | provider owners | safety | captures | row replay | effective replay | action status | probe evidence | request hash evidence | unresolved | before hashes | after hashes | request bytes | response bytes | action frames | background frames | action markers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| blocked-expand-popup-child | blocked | ["missing_action_frame_range", "missing_action_result_markers", "missing_request_frames", "missing_safe_action_hash", "replay_or_probe_unavailable"] | ["/opt/vanessa-mcp-stack", "project:qa-mcp"] | ["safe_ui_action"] | recovery-sequence | ["blocked"] | ["blocked"] | ["blocked"] | [] | [] | [] | [null] | [null] | [0] | [0] | [null] | [[]] | [[]] |
| rejected-click-inert-button | rejected | ["missing_action_frame_range", "missing_action_result_markers", "missing_request_frames", "missing_safe_action_hash", "replay_or_probe_unavailable"] | ["/opt/vanessa-mcp-stack", "project:qa-mcp"] | ["safe_ui_action"] | recovery-sequence | ["rejected"] | ["rejected"] | ["rejected"] | [] | [] | [] | [null] | [null] | [0] | [0] | [null] | [[]] | [[]] |
| safe-activate-existing-window | pending | ["missing_action_frame_range", "missing_request_frames", "missing_safe_action_hash", "pending_action_result", "replay_or_probe_unavailable"] | ["/opt/vanessa-mcp-stack", "project:qa-mcp"] | ["safe_ui_action"] | recovery-sequence | ["pending"] | ["pending"] | ["pending"] | [] | [] | [] | [null] | [null] | [0] | [0] | [null] | [[]] | [["PF_FORM_MAIN", "PF_STATE_INITIAL"]] |
| safe-expand-commandbar-main | pending | ["missing_action_frame_range", "missing_request_frames", "missing_safe_action_hash", "pending_action_result", "replay_or_probe_unavailable"] | ["/opt/vanessa-mcp-stack", "project:qa-mcp"] | ["safe_ui_action"] | recovery-sequence | ["pending"] | ["pending"] | ["pending"] | [] | [] | [] | [null] | [null] | [0] | [0] | [null] | [[]] | [["PF_COMMAND_BAR_MAIN", "PF_COMMAND_POPUP"]] |
| safe-focus-existing-edit-string | pending | ["missing_action_frame_range", "missing_request_frames", "missing_safe_action_hash", "pending_action_result", "replay_or_probe_unavailable"] | ["/opt/vanessa-mcp-stack", "project:qa-mcp"] | ["safe_ui_action"] | recovery-sequence | ["pending"] | ["pending"] | ["pending"] | [] | [] | [] | [null] | [null] | [0] | [0] | [null] | [[]] | [["PF_EDIT_STRING", "PF_EDIT_STRING_VALUE"]] |
| safe-select-local-row-002 | pending | ["missing_action_frame_range", "missing_request_frames", "missing_safe_action_hash", "pending_action_result", "replay_or_probe_unavailable"] | ["/opt/vanessa-mcp-stack", "project:qa-mcp"] | ["safe_ui_action"] | recovery-sequence | ["pending"] | ["pending"] | ["pending"] | [] | [] | [] | [null] | [null] | [0] | [0] | [null] | [[]] | [["PF_TABLE_ITEMS", "PF_ROW_002", "PF_SELECTED_ROW_MARKER"]] |
| safe-switch-fixture-page-b | pending | ["missing_action_frame_range", "missing_request_frames", "missing_safe_action_hash", "pending_action_result", "replay_or_probe_unavailable"] | ["/opt/vanessa-mcp-stack", "project:qa-mcp"] | ["safe_ui_action"] | recovery-sequence | ["pending"] | ["pending"] | ["pending"] | [] | [] | [] | [null] | [null] | [0] | [0] | [null] | [[]] | [["PF_PAGES_MAIN", "PF_PAGE_B", "PF_SELECTED_PAGE"]] |

## Notes

- The report compares reviewed corpus rows only; raw traffic remains under ignored runtime paths.
- `stable` requires the same non-null normalized hash in every input and accepted replay/probe status.
- `effective replay` includes compact direct-probe evidence supplied to the comparison.
- Safe action classifications use `accepted`, `pending`, `unsupported`, `partial`, `timeout`, `rejected` or `blocked`.
- `precise reasons` classify evidence blockers with stable reason values for follow-up planning.
- `incomplete_hash` marks repeated matrix rows whose reviewed evidence exists but one or more inputs lack captured request frames.
- `unsupported_gap` rows are fixture coverage gaps, not protocol mappings.
