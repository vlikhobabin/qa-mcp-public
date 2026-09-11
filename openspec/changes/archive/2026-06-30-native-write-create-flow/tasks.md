## 1. Implementation

- [x] 1.1 Extend write scenario execution to keep one session across field input and command/save steps.
- [x] 1.2 Add command/save step handling with explicit target command names and fail-closed diagnostics.
- [x] 1.3 Add persistence verification output for read-back, list-read or data-layer assertions.
- [x] 1.4 Record cleanup evidence or residual risk for records created during live proof.

## 2. Tests

- [x] 2.1 Add offline tests for mixed input/command write scenarios.
- [x] 2.2 Add tests that unsupported write steps fail closed and keep the scenario failed.
- [x] 2.3 Add tests for persistence-verification result shape.

## 3. Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | Managed form save/write command invoked by native write scenario | Scenario with field inputs, save command and expected persisted state | `provider_gap`, `source_preflight`, `screenshot`, `cleanup_evidence` | `.artifacts/openspec/native-write-create-flow/20260630-0708-do/live-gap-summary.json` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Live create/save is blocked until demo10413 supplies explicit owner/open_link context plus cleanup proof. |
| Live data reads | Post-save assertion that the new row exists | UI list/read-back or read-only data assertion plan | `provider_gap`, `data_assertion` | `.artifacts/openspec/native-write-create-flow/20260630-0708-do/persistence-summary.json` | blocked | `/opt/ai-dev-suite-for-1c/live-mcp` |  | Post-save data assertion cannot run because no save was authorized. |
| Delivery/runtime apply | Runtime execution of data-changing QA flow | Linux runtime preflight and explicit target env | `runtime_apply_log`, `scenario_log`, `cleanup_evidence` | `.artifacts/openspec/native-write-create-flow/20260630-0708-do/live-gap-summary.json` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Linux runtime preflight passed, but data-changing execution is blocked by missing cleanup route. |

| provider_id | owner_path | matrix_row | missing_evidence_type | impact | current_workaround |
| --- | --- | --- | --- | --- | --- |
| qa-mcp | `/opt/ai-dev-suite-for-1c/qa-mcp` | Form module or command | live save scenario with cleanup evidence | The create/save path cannot be accepted without owner/open_link context and cleanup or rollback proof. | Use the implemented scenario route only after a reviewed mutation target and cleanup plan are supplied. |
| live-mcp | `/opt/ai-dev-suite-for-1c/live-mcp` | Live data reads | post-save live read proof | No persisted row exists because the live save was not run. | Re-run data assertion after an approved create/save proof. |
| qa-mcp | `/opt/ai-dev-suite-for-1c/qa-mcp` | Delivery/runtime apply | data-changing runtime apply log | Runtime boot passed, but the data-changing flow was blocked by cleanup policy. | Treat the implementation as offline-proven until a reviewed cleanup route exists. |

- [x] 3.1 Form command row: retain `.artifacts/openspec/native-write-create-flow/20260630-0708-do/live-gap-summary.json` with scenario/provider-gap and cleanup evidence.
- [x] 3.2 Live data read row: retain `persistence-summary.json` with a provider-gap record for data assertion.
- [x] 3.3 Delivery/runtime row: run Linux runtime preflight before live create proof and retain matrix checker output.

## 4. Validation

- [x] 4.1 Run focused pytest coverage for scenario/write runner behavior.
- [x] 4.2 Run `python -m compileall src/qa_mcp`.
- [x] 4.3 Run `openspec validate native-write-create-flow --strict`.
- [x] 4.4 Run `git diff --check`.
- [x] 4.5 Record Windows-native verification as `N/A` under the current Linux-only runtime baseline and confirm no retired-platform entrypoints were added.
