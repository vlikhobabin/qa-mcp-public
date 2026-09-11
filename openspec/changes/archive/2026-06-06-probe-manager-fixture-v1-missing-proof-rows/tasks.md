## 1. Missing-Proof Probes

- [x] 1.1 Load the current pending-row classification and cleanup corpus rows.
- [x] 1.2 Run focused proof for `tm-v1-diag-command-interface-dump`.
- [x] 1.3 Run focused proof for `tm-v1-diag-window-children`.
- [x] 1.4 Run focused proof for `tm-v1-diag-window-find-form-marker`.
- [x] 1.5 Run focused proof for `tm-v1-diag-window-get-form-path` or record
  why broad-window isolation is required first.
- [x] 1.6 Run focused proof for `tm-v1-form-summary`.
- [x] 1.7 Retain positive and negative summaries with current cleanup run id,
  case id, frame range, normalized hash and marker validation.

## 2. Verification

- [x] 2.1 Run focused tests for any changed replay/direct-probe tooling.
- [x] 2.2 Confirm the reporter accepts only summaries that match current
  cleanup identity fields.
- [x] 2.3 Confirm no row is promoted from older supporting evidence alone.
- [x] 2.4 Run `openspec validate probe-manager-fixture-v1-missing-proof-rows --strict`.

## Evidence

- Source classification:
  `docs/protocol-research/evidence/manager-fixture-v1-pending-readonly/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/classification.json`.
- Runtime blocker inherited from change 1:
  `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-readonly-runtime-preflight/runtime_summary.json`.
- Retained missing-proof summary:
  `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-pending-missing-proof-runtime-gap/summary.json`.
- Reporter guard output:
  `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-missing-proof-runtime-gap-report/frame_join_report.json`.
- Reporter guard result: `case_count=17`, `joined=17`,
  `accepted_count=8`; the five missing-proof rows remained
  `accepted_protocol_mapping=false`.
- Focused test:
  `python -m pytest tests\test_manager_fixture_v1_report.py` passed `10`.
- JSON validation:
  `summary.json` parsed successfully with PowerShell `ConvertFrom-Json`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Focused replay/direct probes for five missing-proof rows | Probe command transcript and retained summary per row family | `scenario_log`, `data_assertion`, `cleanup_evidence` | `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/<probe-id>/` | required | `project:qa-mcp` | N/A | High: live endpoint or dynamic adaptation may block proof |
| Managed form layout | Fixture form and diagnostic command surfaces observed by probes | Active form/window or response marker proof for target fixture | `active_window`, `form_tree` or compact response-marker summary | `.artifacts/openspec/probe-manager-fixture-v1-missing-proof-rows/<run-id>/ui-proof/` | required | `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A | Medium: provider UI proof can be unavailable, but response-marker proof may still be enough |
| BSL-only module edit | 1C BSL source | N/A unless a direct-probe helper requires manager/client BSL source edits | `bsl_diagnostics` if edited | `.artifacts/openspec/probe-manager-fixture-v1-missing-proof-rows/<run-id>/bsl-diagnostics/` | N/A | `project:qa-mcp`, `/opt/edt-lab` | Planned work should use existing fixture sources and Python tooling | Medium: if helper BSL changes become necessary, matrix row must become required |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |
