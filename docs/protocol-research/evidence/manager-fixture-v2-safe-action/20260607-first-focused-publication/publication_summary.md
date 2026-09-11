# First Focused V2 Safe-Action Proof Publication

- Published at: `2026-06-07T19:40:00Z`
- Live capture: `20260607-first-focused-v2-safe-action-live-runner-2`
- Selection:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-subset/focused_safe_action_manifest.json`
- Frame isolation:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-live-action-frame-join/frame_isolation_summary.md`
- Proof decision:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-proof-decision/proof_summary.md`
- Accepted mapping output:
  `docs/protocol-research/evidence/accepted-mappings/manager-fixture-v2-first-focused-proof-20260607/accepted_mappings.md`

## Result

The first focused V2 safe-action proof produced reviewed candidate evidence for
two non-mutating fixture actions:

| Case | Family | Action frames | Normalized hash | Status | Reason |
| --- | --- | --- | --- | --- | --- |
| `safe-switch-fixture-page-b` | `switch_fixture_page` | `manager_to_client 59-61; client_to_manager 60-62` | `191824eda15e75980801e07ab5f443a9b0065f9f28d1ee5162bbbb6c803ded4a` | candidate | `replay_or_probe_or_typed_contract_unavailable` |
| `safe-focus-existing-edit-string` | `focus_existing_element` | `manager_to_client 70-71; client_to_manager 71-72` | `bbfa2978b211f2f6e54d84f3bc53f19aff713ee0ba66f5a7d8392ef619869b19` | candidate | `replay_or_probe_or_typed_contract_unavailable` |

No row is promoted to accepted protocol mapping in this publication. The
accepted-mapping output is intentionally empty because same-action V2 replay,
direct Python-manager probe or accepted typed contract proof is not retained.

## Safety Boundary

The V2 boundary remains unchanged. Text input, checkbox/value toggles, business
command clicks, object writes, save/post/delete/fill/import/export and external
side effects remain outside this focused proof and belong to later
mutation/recovery cards.

Raw captures, generated replay payloads, process logs and platform logs remain
under ignored runtime or artifact paths.
