## 1. Marker Contracts

- [x] 1.1 Review candidate marker corrections from the classification output.
- [x] 1.2 Reconcile `tm-v1-diag-window-find-form-marker` semantics.
- [x] 1.3 Reconcile `tm-v1-form-summary` semantics.
- [x] 1.4 Reconcile `tm-v1-checkbox-true` against current run and older
  supporting probe evidence.
- [x] 1.5 Reconcile `tm-v1-button-inert` after broad-window isolation.
- [x] 1.6 Reconcile `tm-v1-table-items` endpoint or marker contract.
- [x] 1.7 Reconcile `tm-v1-group-main` group identity semantics.
- [x] 1.8 Apply manifest/catalog changes only where current-run proof validates
  the corrected marker.

## 2. Verification

- [x] 2.1 Run catalog drift checks when manifest/catalog expectations change.
- [x] 2.2 Run focused tests for reporter marker validation.
- [x] 2.3 Confirm old marker expectations and candidate replacements are linked
  in retained evidence.
- [x] 2.4 Run `openspec validate reconcile-manager-fixture-v1-marker-contracts --strict`.

## Evidence

- Marker reconciliation summary:
  `docs/protocol-research/evidence/manager-fixture-v1-marker-contracts/20260606-pending-marker-contract-reconciliation/marker_contract_summary.json`.
- Catalog drift report:
  `docs/protocol-research/evidence/manager-fixture-v1-marker-contracts/20260606-pending-marker-contract-reconciliation/catalog_comparison.json`.
- Catalog drift result: `status=ok`, `mismatches=0`,
  `catalog_command_count=17`, `bsl_command_count=17`.
- Catalog changes applied: `0`; `tools/protocol-research/manager_fixture_v1_command_catalog.json`
  has no git diff.
- Candidate-only rows retained:
  `tm-v1-diag-window-find-form-marker`, `tm-v1-form-summary`,
  `tm-v1-button-inert`, `tm-v1-table-items`, `tm-v1-group-main`.
- Mismatch retained:
  `tm-v1-checkbox-true`.
- Focused test:
  `python -m pytest tests\test_manager_fixture_v1_report.py` passed `10`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BSL-only module edit | Manager fixture harness/catalog source if expected markers are changed in 1C source | Changed routines/catalog entries and read-only behavior risk | `bsl_diagnostics`, source diff summary | `.artifacts/openspec/reconcile-manager-fixture-v1-marker-contracts/<run-id>/bsl-diagnostics/` | required | `project:qa-mcp`, `/opt/edt-lab` | N/A | Medium: source and PowerShell/JSON catalog can drift if only one side is updated |
| Delivery or runtime apply | Reporter validation after marker corrections | Regenerated report with old/new marker proof links | `scenario_log`, `data_assertion` | `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/<marker-contract-run-id>/` | required | `project:qa-mcp` | N/A | High: corrected marker can still fail normalized-hash or frame-range validation |
| Managed form layout | Fixture form markers used as semantic proof | Active form/window or response-marker evidence for corrected marker semantics | `active_window`, `form_tree` or compact response-marker summary | `.artifacts/openspec/reconcile-manager-fixture-v1-marker-contracts/<run-id>/ui-proof/` | required | `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A | Medium: UI proof may be unavailable for direct replay-only evidence |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |
