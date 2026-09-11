## Context

`NativeWriteSession` already keeps one socket open for multiple field writes. `run_write_scenario` uses that path for `input_text`, but command steps are treated as unsupported. The create flow needs open form -> fill N fields -> invoke save -> verify the record, without closing the form between steps.

## Goals / Non-Goals

**Goals:**
- Run write scenario steps against one native write session.
- Support save/command steps with explicit target command names.
- Preserve per-step result reporting and unsupported-step diagnostics.
- Provide a verification hook for UI/read-back/data assertions after save.

**Non-Goals:**
- Do not auto-run arbitrary business commands without an explicit step.
- Do not bypass project cleanup policy for test records.
- Do not replace the read-only `ScenarioRunner` path.

## Decisions

- Keep write/create orchestration in the write scenario path rather than overloading read-only `run_scenario`.
- Represent save as a command step with an explicit command target, defaulting to a safe known save command only when the caller asks for create/save semantics.
- Return step-level statuses so a partially filled form is visible and the archive gate can point to the missing evidence.
- Treat persistence verification as required for create acceptance. A command accepted by the client is not enough.

## Risks / Trade-offs

- Save commands mutate business data -> require explicit operator intent, approved target env and cleanup/read-back evidence.
- Command button names vary by configuration/language -> allow caller-supplied command names and fail closed when not found.
- A save may open validation dialogs -> report dialog state/provider gap instead of sending blind keystrokes.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | Managed form save/write command invoked by native write scenario | Scenario with field inputs, save command and expected persisted state | `provider_gap`, `source_preflight`, `screenshot`, `cleanup_evidence` | `.artifacts/openspec/native-write-create-flow/20260630-0708-do/live-gap-summary.json` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Live create/save is blocked until demo10413 supplies explicit owner/open_link context plus cleanup proof. |
| Live data reads | Post-save assertion that the new row exists | UI list/read-back or read-only data assertion plan | `provider_gap`, `data_assertion` | `.artifacts/openspec/native-write-create-flow/20260630-0708-do/persistence-summary.json` | blocked | `/opt/ai-dev-suite-for-1c/live-mcp` |  | Post-save data assertion cannot run because no save was authorized. |
| Delivery/runtime apply | Runtime execution of data-changing QA flow | Linux runtime preflight and explicit target env | `runtime_apply_log`, `scenario_log`, `cleanup_evidence` | `.artifacts/openspec/native-write-create-flow/20260630-0708-do/live-gap-summary.json` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Linux runtime preflight passed, but data-changing execution is blocked by missing cleanup route. |

## Migration Plan

1. Add command/save step handling behind explicit scenario input.
2. Verify unsupported steps still report errors.
3. Add persistence assertion result and cleanup evidence paths.
4. Run live proof only against an approved demo/lab target.
