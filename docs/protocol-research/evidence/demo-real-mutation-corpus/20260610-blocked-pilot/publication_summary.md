# Demo Real Mutation Corpus Pilot

Run id: `20260610-blocked-pilot`

## Decision

The first real-demo mutation pilot is published as `blocked`. No real-demo UI
action was executed, no demo data was changed and no accepted mutation mapping
was produced.

| Field | Value |
| --- | --- |
| Selected target | `demo10413-operation-goods-toggle-activity` |
| Source target | `Document.OperatsiyaPoUchetuTovarov.Form.FormaDokumenta` |
| Element path | `TovarnyeZapasyKomandnayaPanel/PereklyuchitAktivnost` |
| Operation family | `document_register_record_activity_toggle` |
| `mutates_business_data` | `true` |
| Runtime preflight | `passed` |
| Guarded execution | `blocked_before_runtime_action` |
| Frame isolation | `blocked_no_action_frames` |
| Recovery status | `not_required_no_action` |
| Accepted mapping status | empty |

## Evidence Chain

- Target selection:
  `.artifacts/openspec/select-demo-real-mutation-targets/20260610-demo-real-mutation-selection/target-selection/`
- Manifest review:
  `.artifacts/openspec/define-demo-mutation-manifest-contract/20260610-demo-real-mutation-manifest/manifest-review/`
- Runtime preflight and blocked execution:
  `.artifacts/openspec/execute-demo-mutation-guarded-pilot/20260610-demo-real-mutation-pilot/runtime-pilot/`
- Runtime cleanup:
  `.artifacts/openspec/execute-demo-mutation-guarded-pilot/20260610-demo-real-mutation-pilot/runtime-cleanup/`
- UI evidence summary:
  `docs/protocol-research/evidence/demo-real-mutation-corpus/20260610-blocked-pilot/ui-evidence.md`
- Frame isolation:
  `.artifacts/openspec/isolate-demo-mutation-action-frames/20260610-demo-real-mutation-frame-isolation/frame-isolation/`
- Accepted mapping output:
  `docs/protocol-research/evidence/accepted-mappings/demo-real-mutation-corpus-20260610/`

## Why It Is Blocked

The capture-mode preflight passed, so the blocker is not local runtime
availability. The row still failed closed because execution requires all of the
following evidence before a mutating click:

- live active form and target marker recheck;
- selected document/register-record row pre-state;
- expected post-state marker;
- reviewed recovery or cleanup wrapper;
- owner-safe action/recovery phase logging.

The selected row currently has source-reviewed mutation intent and a theoretical
inverse-toggle recovery idea only. That is not enough to mutate the disposable
demo data.

## Corpus Status

| Target id | Final status | Proof route | Accepted | Reason |
| --- | --- | --- | --- | --- |
| `demo10413-operation-goods-toggle-activity` | `blocked` | `blocked_validation` | `false` | live pre-state and reviewed recovery wrapper are missing |

## Coverage And Batch Decision

No API coverage mapping was added because this pilot produced no accepted or
candidate protocol frame evidence. `docs/protocol-research/coverage-report.md`
was regenerated after confirming that the case map has no newly proven
demo-mutation correspondence.

The mutation scheme is not yet proven enough to plan the 30-50 row batch corpus
card described in `docs/protocol-research/methodology.md`. The next real-demo
mutation attempt should first add a reviewed wrapper that can prove pre-state,
action, post-state and recovery for exactly one row.

No raw captures, screenshots, platform logs, generated replay payloads or live
data rows are included in reviewed git.
