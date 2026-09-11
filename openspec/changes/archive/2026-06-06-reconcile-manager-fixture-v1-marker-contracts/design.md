## Context

Candidate marker changes from the classification:

- `tm-v1-diag-window-find-form-marker`: candidate `QA MCP Protocol Fixture V1`
- `tm-v1-form-summary`: candidate `QA MCP Protocol Fixture V1`
- `tm-v1-button-inert`: candidate `PF_BUTTON_INERT`
- `tm-v1-table-items`: candidate `PF_TABLE_ITEMS`
- `tm-v1-group-main`: candidate `PF_GROUP_MAIN`

Current marker mismatches:

- `tm-v1-checkbox-true`: capture has `CheckBox` and `PF_CHECKBOX_TRUE`, replay
  observed `PF_CHECKBOX_TRUE` only.
- `tm-v1-group-main`: capture has `PF_FORM_MAIN` and `PF_GROUP_MAIN`, replay
  observed `PF_GROUP_MAIN` only.

## Goals / Non-Goals

**Goals:**

- Decide marker contracts per affected row using current-run proof.
- Update manifest/catalog expectations only for proven semantics.
- Retain mismatch summaries for rows that remain pending.

**Non-Goals:**

- No acceptance by simply changing expected markers.
- No V2 action behavior or mutation semantics.
- No broad-window acceptance without range isolation.

## Decisions

1. Separate semantic contract from transport replay.
   Transport success can prove reachability, but marker semantics decide
   acceptance.

2. Require reporter validation after any marker change.
   A corrected marker must still match `case_id`, frame range and
   `normalized_hash`.

3. Preserve old expectations in evidence.
   Candidate changes should record previous marker, candidate marker and proof
   path.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BSL-only module edit | Manager fixture harness/catalog source if expected markers are changed in 1C source | Changed routines/catalog entries and read-only behavior risk | `bsl_diagnostics`, source diff summary | `.artifacts/openspec/reconcile-manager-fixture-v1-marker-contracts/<run-id>/bsl-diagnostics/` | required | `project:qa-mcp`, `/opt/edt-lab` | N/A | Medium: source and PowerShell/JSON catalog can drift if only one side is updated |
| Delivery or runtime apply | Reporter validation after marker corrections | Regenerated report with old/new marker proof links | `scenario_log`, `data_assertion` | `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/<marker-contract-run-id>/` | required | `project:qa-mcp` | N/A | High: corrected marker can still fail normalized-hash or frame-range validation |
| Managed form layout | Fixture form markers used as semantic proof | Active form/window or response-marker evidence for corrected marker semantics | `active_window`, `form_tree` or compact response-marker summary | `.artifacts/openspec/reconcile-manager-fixture-v1-marker-contracts/<run-id>/ui-proof/` | required | `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A | Medium: UI proof may be unavailable for direct replay-only evidence |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |

## Risks / Trade-offs

- Updating marker expectations may make the manifest more truthful but can
  hide endpoint mistakes if not proven. Mitigation: require current-run proof
  and retain prior marker in evidence.
- If BSL and generated manifest catalogs diverge, downstream captures become
  ambiguous. Mitigation: add or run a catalog drift check.
