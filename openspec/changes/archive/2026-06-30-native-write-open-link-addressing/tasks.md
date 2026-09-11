## 1. Implementation

- [x] 1.1 Add optional `open_link` routing to the native write-session setup while preserving capture-backed defaults.
- [x] 1.2 Expose `open_link` through `write_form_value` and `write_form_values` MCP tools and include opened-form metadata in results.
- [x] 1.3 Make field-write failures fail closed with target field, open-link and blocked reason.

## 2. Tests

- [x] 2.1 Add offline unit tests for open-link parameter routing and default fixture compatibility.
- [x] 2.2 Add or update MCP tool-surface tests for the new result fields.

## 3. Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | Native write session opening arbitrary managed forms through `open_link` | Live scenario opens a catalog create/edit form by nav-link and writes a string field | `provider_gap`, `source_preflight`, `screenshot`, `cleanup_evidence` | `.artifacts/openspec/native-write-open-link-addressing/20260630-0708-do/live-gap-summary.json` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | demo10413 rejected the ownerless subordinate-catalog create URL; callers need explicit owner/open_link context before live targeting. |
| Delivery/runtime apply | MCP tool surface change for write helpers | Offline tests plus Linux runtime preflight before live probe | `source_preflight`, `scenario_log` | `.artifacts/openspec/native-write-open-link-addressing/20260630-0708-do/matrix-preflight.json, .artifacts/openspec/native-write-open-link-addressing/20260630-0708-do/live-gap-summary.json, .artifacts/openspec/native-write-open-link-addressing/20260630-0708-do/matrix-archive-gate.json` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Runtime proof is limited to preflight and blocked-gap evidence for the subordinate create target. |
| BSL-only module edit | N/A | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/bsl-mcp` | Python protocol manager change only; no BSL source is edited. | No BSL diagnostics expected for this change. |

| provider_id | owner_path | matrix_row | missing_evidence_type | impact | current_workaround |
| --- | --- | --- | --- | --- | --- |
| qa-mcp | `/opt/ai-dev-suite-for-1c/qa-mcp` | QA/TestClient UI automation | live open-link write bundle with form tree and read-back | The demo10413 contract create form cannot be live-targeted from an ownerless subordinate-catalog data link. | Provide an explicit owner/ref-aware `open_link` or mark the create step `requires_owner` so it fails closed before navigation. |

- [x] 3.1 QA/TestClient UI automation row: retain `.artifacts/openspec/native-write-open-link-addressing/20260630-0708-do/live-gap-summary.json` with live open-link provider-gap evidence.
- [x] 3.2 Delivery/runtime apply row: run Linux runtime preflight before live write proof and retain matrix checker output.
- [x] 3.3 BSL row: record `N/A` because no BSL source is edited.

## 4. Validation

- [x] 4.1 Run `python -m pytest tests/test_native_write.py` or the focused replacement available in this repo.
- [x] 4.2 Run `python -m compileall src/qa_mcp`.
- [x] 4.3 Run `openspec validate native-write-open-link-addressing --strict`.
- [x] 4.4 Run `git diff --check`.
- [x] 4.5 Record Windows-native verification as `N/A` under the current Linux-only runtime baseline and confirm no `.cmd`, `.bat`, PowerShell or WSL workflow entrypoints were added.
