# Focused V2 Safe-Action Frame Isolation

- Capture id: `20260607-first-focused-v2-safe-action-live-runner-2`
- Reviewed evidence path:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-live-action-frame-join/`
- Runtime path:
  `runtime/protocol-research/captures/20260607-first-focused-v2-safe-action-live-runner-2/`
- Frame join status: 2 joined rows
- Acceptance status: candidate only; no replay/probe or typed contract proof is
  retained yet.

| Case | Action frames | Background frames | Recovery frames | Request bytes | Response bytes | Dynamic fields | Normalized hash | Non-accepted reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `safe-switch-fixture-page-b` | `manager_to_client 59-61 (3); client_to_manager 60-62 (3)` | `manager_to_client 55-62 (5); client_to_manager 56-63 (5)` | `manager_to_client 63-65 (3); client_to_manager 64-66 (3)` | 731 | 622 | 7 | `191824eda15e75980801e07ab5f443a9b0065f9f28d1ee5162bbbb6c803ded4a` | `replay_or_probe_unavailable` |
| `safe-focus-existing-edit-string` | `manager_to_client 70-71 (2); client_to_manager 71-72 (2)` | `manager_to_client 66-72 (5); client_to_manager 67-73 (5)` | `manager_to_client 73-74 (2); client_to_manager 74-75 (2)` | 534 | 245 | 5 | `bbfa2978b211f2f6e54d84f3bc53f19aff713ee0ba66f5a7d8392ef619869b19` | `replay_or_probe_unavailable` |

## Review Notes

- Action, background and recovery ranges are retained separately and recovery
  chunks are not treated as action protocol shape.
- `pre_normalization_hash` is retained in `corpus_cases.jsonl`; normalized
  hashes use `manager_fixture_v2_safe_action_binary_frame_signature.v1`.
- Dynamic fields are compact metadata only. Raw TCP payloads and generated
  replay output remain under ignored runtime paths.
- Rows remain candidate and are handed to
  `probe-focused-v2-safe-action-contract`.
