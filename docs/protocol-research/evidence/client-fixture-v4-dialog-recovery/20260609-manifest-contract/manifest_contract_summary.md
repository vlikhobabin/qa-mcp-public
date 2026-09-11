# Client Fixture V4 Dialog Manifest Contract

Published at: `2026-06-09T17:36:09Z`.

This reviewed publication defines the V4 dialog, expected-error and bounded
wait manifest shape and evidence boundary. It publishes candidate rows only; it
does not accept any protocol mapping.

## Required Row Fields

Every V4 dialog row must include:

| Field | Requirement |
| --- | --- |
| `dialog_scenario_id` | Stable row id. |
| `scenario_family` | One of `warning`, `question`, `fixture_modal`, `expected_error`, `bounded_wait_complete`, `bounded_wait_cancel`, `bounded_wait_retry`. |
| `target_marker` | Reviewed fixture-local `PF_*` command or marker. |
| `dialog_family` | Expected dialog family marker such as `PF_V4_WARNING` or `PF_V4_WAIT`. |
| `dialog_lifecycle` | Expected lifecycle marker after the action. |
| `expected_text_marker` | Marker for the reviewed text surface. |
| `expected_dialog_result_marker` | Marker for the selected result or wait outcome. |
| `pre_state` | Baseline observable markers before the scenario. |
| `action` | Concrete fixture-local command route. |
| `post_state` | Expected marker state after the scenario. |
| `recovery_expectation` | Reset path and expected baseline markers. |
| `mutates_business_data` | Must be `false`. |
| `expected_action_result_markers` | Compact markers that distinguish the scenario result from background traffic. |

`expected_error` rows must also include `expected_diagnostic_marker`. Bounded
wait rows must also include `bounded_duration_ms`.

Rows may add `action_frame_range`, `background_frame_ranges`,
`recovery_frame_range`, `dynamic_fields`, `normalized_hash`,
`recovery_result`, `rerun_determinism`, `proof_routes`,
`dialog_review_status` and `accepted_protocol_mapping` as evidence becomes
available.

## Fail-Closed Rules

A row fails closed before capture or publication when:

- a required field is missing;
- `mutates_business_data` is absent or not `false`;
- `scenario_family` is outside the reviewed V4 family list;
- `target_marker` is outside the reviewed fixture-local marker set;
- an `expected_error` row lacks `expected_diagnostic_marker`;
- a bounded wait row lacks `bounded_duration_ms`;
- `recovery_expectation` does not return to the V1 baseline;
- the row attempts OS dialogs, files, network resources, printing, clipboard,
  business objects, registers, settings storage or other persisted paths.

## Status Taxonomy

| Status | Meaning |
| --- | --- |
| `candidate` | Manifest and marker/recovery evidence are reviewable, but accepted proof is missing. |
| `accepted` | Dialog/action, background and recovery frames are isolated and replay/probe or typed contract proof supports the row. |
| `expected_error` | The reviewed expected diagnostic marker was observed; infrastructure failure remains a separate non-accepted outcome. |
| `rejected` | The row is unsafe, unsupported or contradicts observed evidence. |
| `blocked` | Required runtime, provider or fixture capability is unavailable. |
| `partial` | Useful evidence exists but required proof is incomplete. |
| `timeout` | Runtime or probe execution did not finish inside the reviewed budget. |

## Publication Result

Candidate rows are published in `dialog_manifest_rows.jsonl`.

No raw capture payloads, generated replay output, platform logs or full
form-analysis dumps are committed. Runtime marker and reset proof belongs under
ignored `.artifacts/openspec/` paths and must be summarized before any accepted
promotion.

## Decision

Decision counts: `{"candidate": 8, "accepted": 0}`.

Rows remain candidate because V4 dialog/action frame ranges, normalized hashes
and V4-specific same-scenario replay, direct Python-manager probe or accepted
typed contract proof are not retained yet.
