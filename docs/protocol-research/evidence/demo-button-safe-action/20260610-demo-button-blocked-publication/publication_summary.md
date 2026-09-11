# Demo Button Safe-Action Pilot Decision

Run id: `20260610-demo-button-blocked-publication`

## Decision

The demo real-button pilot is published as `routed_to_v3`. No safe-action
capture was executed and no accepted V2 mapping was produced.

| Field | Value |
| --- | --- |
| Selected target | `demo10413-operation-goods-toggle-activity` |
| Source target | `Document.OperatsiyaPoUchetuTovarov.Form.FormaDokumenta` |
| Element path | `TovarnyeZapasyKomandnayaPanel/PereklyuchitAktivnost` |
| Element family | `Button` |
| Safety classification | `business_mutation` |
| Capture status | `blocked` |
| Final status | `routed_to_v3` |
| Accepted mapping status | empty |

## Evidence Chain

- Target selection:
  `.artifacts/openspec/select-demo-safe-button-target/20260610-demo-button-selection/target-selection/`
- Safety classification:
  `.artifacts/openspec/classify-demo-button-safety-contract/20260610-demo-button-classification/classification/`
- Blocked capture:
  `.artifacts/openspec/capture-demo-button-safe-action-pilot/20260610-demo-button-blocked-capture/runtime-capture/`
- UI/provider summary:
  `docs/protocol-research/evidence/demo-button-safe-action/20260610-demo-button-blocked-publication/ui-evidence.md`
- Accepted-mapping publication:
  `docs/protocol-research/evidence/accepted-mappings/demo-button-safe-action-20260610/`

## Why It Is Not A V2 Safe Action

The selected button is source-visible and source-enabled, but source metadata
ties the target to document register-record activity state:

- the table is bound to `Object.RegisterRecords.TovarnyeZapasy`;
- the active-state field is bound to
  `Object.RegisterRecords.TovarnyeZapasy.Active`;
- the selected button name means "toggle activity";
- the document form/object source contains write and movement handling.

The pilot therefore cannot justify `mutates_business_data=false`, cannot
provide an allowlisted V2 action family and cannot define a safe recovery
expectation. The guarded capture correctly stopped before TestClient
connection, pre-state recheck or click.

## Result

This is a safe blocker outcome. The card produced a reviewed real demo-button
target and classified it before execution. The target is routed to V3 or later
mutation/recovery work, and V2 accepted mappings remain unchanged.

No raw captures, screenshots, platform logs, generated replay payloads or live
data rows are included in reviewed git.
