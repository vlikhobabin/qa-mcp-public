## 1. Implementation

- [x] 1.1 Add date normalization/validation for `DD.MM.YYYY` before live input.
- [x] 1.2 Add a form-level date field write operation with `surface=form_field_date` result metadata.
- [x] 1.3 Wire date field steps into the write/create scenario path.
- [x] 1.4 Keep `set_table_date_cell` grid behavior and result shape unchanged.

## 2. Tests

- [x] 2.1 Add offline tests for valid/invalid date normalization.
- [x] 2.2 Add tests for date-prefix read-back acceptance with optional time suffix.
- [x] 2.3 Add regression coverage that table date-cell code still routes as a grid operation.

## 3. Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | Form-level date `EditField` on arbitrary open-link form | Scenario sets a date field and reads it back | `provider_gap`, `source_preflight`, `screenshot`, `scenario_log` | `.artifacts/openspec/native-write-form-date-input/20260630-0708-do/live-gap-summary.json` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | The demo10413 generated contract form did not open from the ownerless data link, so the date field was not targetable live. |
| Form module or command | Date change handlers that react to the field value | Create-flow scenario uses date plus another field before save | `provider_gap`, `data_assertion` | `.artifacts/openspec/native-write-form-date-input/20260630-0708-do/date-handler-summary.json` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Handler proof depends on an approved saved create flow with cleanup evidence. |
| Report/DCS | N/A | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/meta-mcp` | No report or DCS surface is changed. | No residual report or DCS risk. |

| provider_id | owner_path | matrix_row | missing_evidence_type | impact | current_workaround |
| --- | --- | --- | --- | --- | --- |
| qa-mcp | `/opt/ai-dev-suite-for-1c/qa-mcp` | Managed form layout | live date field screenshot/readback | The target form did not open from the ownerless subordinate-catalog create link. | Use an explicit valid owner/ref-aware `open_link` before running `write_form_date` live. |
| qa-mcp | `/opt/ai-dev-suite-for-1c/qa-mcp` | Form module or command | saved date-handler proof | Date handler and auto-name behavior were not verified because save was blocked by cleanup policy. | Run the create/save scenario only after reviewed cleanup evidence is available. |

- [x] 3.1 Managed form layout row: retain `.artifacts/openspec/native-write-form-date-input/20260630-0708-do/live-gap-summary.json` with provider-gap evidence.
- [x] 3.2 Form command/handler row: retain `date-handler-summary.json` as blocked provider-gap evidence.
- [x] 3.3 Report/DCS row: record `N/A` because no report/DCS surface is changed.

## 4. Validation

- [x] 4.1 Run focused pytest coverage for date write parsing/routing.
- [x] 4.2 Run `python -m compileall src/qa_mcp`.
- [x] 4.3 Run `openspec validate native-write-form-date-input --strict`.
- [x] 4.4 Run `git diff --check`.
- [x] 4.5 Record Windows-native verification as `N/A` under the current Linux-only runtime baseline and confirm no retired-platform entrypoints were added.
