# Client Fixture V3 Mutation Manifest Contract

Published at: `2026-06-09T04:43:17Z`.

This reviewed publication defines the V3 mutation manifest shape and evidence
boundary. It publishes candidate rows only; it does not accept any protocol
mapping.

## Required Row Fields

Every V3 mutation row must include:

| Field | Requirement |
| --- | --- |
| `mutation_id` | Stable row id. |
| `target_marker` | Reviewed fixture-local `PF_*` marker. |
| `mutation_family` | One of `text_input`, `number_input`, `date_input`, `checkbox_toggle`, `inert_button`. |
| `pre_state` | Baseline observable markers before the action. |
| `action` | Concrete fixture-local action and intended value or route. |
| `post_state` | Expected target marker, action marker and mutation post-state markers. |
| `recovery_expectation` | Reset path and expected baseline markers. |
| `mutates_business_data` | Must be `false`. |
| `expected_action_result_markers` | Compact markers that distinguish the action result from background traffic. |

Rows may add `action_frame_range`, `background_frame_ranges`,
`recovery_frame_range`, `dynamic_fields`, `normalized_hash`,
`recovery_result`, `rerun_determinism`, `proof_routes`,
`mutation_review_status` and `accepted_protocol_mapping` as evidence becomes
available.

## Fail-Closed Rules

A row fails closed before capture or publication when:

- a required field is missing;
- `mutates_business_data` is absent or not `false`;
- `mutation_family` is outside the reviewed V3 family list;
- `target_marker` is outside the reviewed fixture-local marker set;
- `recovery_expectation` does not return to the V1 baseline;
- the row attempts catalogs, documents, registers, settings storage, external
  files, network resources, clipboard/keyboard side effects or other business
  data paths.

## Status Taxonomy

| Status | Meaning |
| --- | --- |
| `candidate` | Manifest and marker/recovery evidence are reviewable, but accepted proof is missing. |
| `accepted` | Action, background and recovery frames are isolated and replay/probe or typed contract proof supports the row. |
| `rejected` | The row is unsafe, unsupported or contradicts observed evidence. |
| `blocked` | Required runtime, provider or fixture capability is unavailable. |
| `partial` | Useful evidence exists but required proof is incomplete. |
| `timeout` | Runtime or probe execution did not finish inside the reviewed budget. |

## Publication Result

Candidate rows are published in `mutation_manifest_rows.jsonl`. The paired
accepted-mapping output is intentionally empty:

`docs/protocol-research/evidence/accepted-mappings/client-fixture-v3-mutation-20260609/`

No raw capture payloads, generated replay output, platform logs or full
form-analysis dumps are committed. Underlying runtime marker and reset proof
remains in ignored `.artifacts/openspec/` paths and is summarized by:

`docs/protocol-research/evidence/client-fixture-v3-mutation/20260609-recovery-proof/`

## Decision

Decision counts: `{"candidate": 5, "accepted": 0}`.

Rows remain candidate because mutation action frame ranges, normalized hashes
and same-action replay, direct Python-manager probe or accepted typed contract
proof are not retained yet.
