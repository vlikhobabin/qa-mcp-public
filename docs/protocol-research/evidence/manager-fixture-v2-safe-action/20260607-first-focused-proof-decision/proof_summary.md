# Focused V2 Safe-Action Proof Summary

- Generated at: `2026-06-07T19:38:25Z`
- Source corpus: `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-live-action-frame-join/corpus_cases.jsonl`
- Decision counts: `{"candidate": 2}`
- Raw output policy: raw replay/probe payloads, generated request series, platform logs and full TCP captures stay under ignored runtime/protocol-research paths

| case | decision | routes | normalized hash | request bytes | response bytes | missing for acceptance |
| --- | --- | --- | --- | --- | --- | --- |
| safe-switch-fixture-page-b | candidate | {"replay": "infeasible", "direct_python_manager_probe": "infeasible", "typed_contract": "insufficient"} | 191824eda15e75980801e07ab5f443a9b0065f9f28d1ee5162bbbb6c803ded4a | 731 | 622 | ["accepted_replay_probe_or_typed_contract_proof"] |
| safe-focus-existing-edit-string | candidate | {"replay": "infeasible", "direct_python_manager_probe": "infeasible", "typed_contract": "insufficient"} | bbfa2978b211f2f6e54d84f3bc53f19aff713ee0ba66f5a7d8392ef619869b19 | 534 | 245 | ["accepted_replay_probe_or_typed_contract_proof"] |

## Decision

No focused V2 safe-action row is promoted to accepted status in this proof pass.
The live capture and frame isolation are retained as candidate evidence; replay, direct Python-manager probe and typed contract proof are not available for same-action V2 semantics yet.
