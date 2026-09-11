# Protocol Corpus Repeatability Report

- Generated at: `2026-06-03T10:56:18Z`
- Input count: `1`
- Case count: `1`
- Classification counts: `{"pending": 1}`
- Stable case ids: `[]`
- Accepted case ids: `[]`
- Gap case ids: `["safe-activate-existing-window"]`
- Normalizer investigation candidates: `[]`

## Inputs

| index | capture ids | cases | path |
| --- | --- | --- | --- |
| 0 | ["20260603-134132"] | 1 | docs/protocol-research/evidence/corpus/20260603-134132-safe-action/corpus_cases.jsonl |

## Cases

| case | classification | precise reasons | provider owners | safety | captures | row replay | effective replay | action status | probe evidence | request hash evidence | unresolved | before hashes | after hashes | request bytes | response bytes | action frames | background frames | action markers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| safe-activate-existing-window | pending | ["missing_action_frame_range", "missing_request_frames", "missing_safe_action_hash", "pending_action_result", "replay_or_probe_unavailable"] | ["/opt/vanessa-mcp-stack", "project:qa-mcp"] | ["safe_ui_action"] | 20260603-134132 | ["pending"] | ["pending"] | ["pending"] | [] | [] | [] | [null] | [null] | [0] | [0] | [null] | [[]] | [["status=pending", "window_title_observed"]] |

## Notes

- The report compares reviewed corpus rows only; raw traffic remains under ignored runtime paths.
- `stable` requires the same non-null normalized hash in every input and accepted replay/probe status.
- `effective replay` includes compact direct-probe evidence supplied to the comparison.
- Safe action classifications use `accepted`, `pending`, `unsupported`, `partial`, `timeout`, `rejected` or `blocked`.
- `precise reasons` classify evidence blockers with stable reason values for follow-up planning.
- `incomplete_hash` marks repeated matrix rows whose reviewed evidence exists but one or more inputs lack captured request frames.
- `unsupported_gap` rows are fixture coverage gaps, not protocol mappings.
