## Context

There are two different date surfaces. A grid date cell uses an inline calendar editor and is handled by `set_table_date_cell`. A form-level date edit field is an `EditField` on the managed form and should be written through field addressing or a focused OS-input fallback. The create-flow card needs the latter.

## Goals / Non-Goals

**Goals:**
- Add a form-level date input operation with clear result shape.
- Accept and validate `DD.MM.YYYY` input.
- Route date field steps through create/write scenarios.
- Keep table date-cell behavior unchanged.

**Non-Goals:**
- Do not rewrite `set_table_date_cell`.
- Do not infer dates from locale-specific free text beyond the accepted format.
- Do not click guessed screen coordinates for form fields.

## Decisions

- Model form-date input as a field write, not a table-cell write. The result should say `surface=form_field_date`.
- Normalize the date before live execution so invalid dates fail before mutation.
- Prefer protocol field addressing when it commits; permit a bounded XTEST field-input fallback only when it targets the already opened form and reports display evidence.
- Keep runtime proof separate from unit tests because date widgets can be configuration/theme sensitive.

## Risks / Trade-offs

- Some date fields may format read-back with time (`0:00:00`) -> compare by date prefix and retain raw read-back summary.
- XTEST fallback needs display readiness -> fail closed with display provider error if no backend is available.
- Date input can trigger form handlers -> require UI/data assertion evidence when used in create flow.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | Form-level date `EditField` on arbitrary open-link form | Scenario that sets a date field and reads it back | `provider_gap`, `source_preflight`, `screenshot`, `scenario_log` | `.artifacts/openspec/native-write-form-date-input/20260630-0708-do/live-gap-summary.json` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | The demo10413 generated contract form did not open from the ownerless data link, so the date field was not targetable live. |
| Form module or command | Date change handlers that react to the field value | Create-flow scenario using date plus another field before save | `provider_gap`, `data_assertion` | `.artifacts/openspec/native-write-form-date-input/20260630-0708-do/date-handler-summary.json` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Handler proof depends on an approved saved create flow with cleanup evidence. |
| Report/DCS | N/A | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/meta-mcp` | No report or DCS surface is changed. | No residual report or DCS risk. |

## Migration Plan

1. Add date normalization and field-date operation.
2. Wire date steps into write/create scenario execution.
3. Verify table date-cell tests still cover grid behavior separately.
4. Retain live date evidence or a provider gap before archive.
