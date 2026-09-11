## Context

The missing-proof rows are:

- `tm-v1-diag-command-interface-dump`
- `tm-v1-diag-window-children`
- `tm-v1-diag-window-find-form-marker`
- `tm-v1-diag-window-get-form-path`
- `tm-v1-form-summary`

The current source cleanup run is
`20260606-live-fixture-ci-bootstrap-full-readonly-cleanup`. Accepted evidence
must match the current cleanup `case_id`, manager frame range and
`normalized_hash`.

## Goals / Non-Goals

**Goals:**

- Attempt each missing-proof row with a row-specific replay or direct-probe
  strategy.
- Record response markers, missing expected markers, dynamic-field adaptation
  and normalized hash validation.
- Produce retained summaries that `report_manager_fixture_v1.py` can fold into
  the cleanup report.

**Non-Goals:**

- No acceptance from older probes unless reconciled with current cleanup
  range/hash.
- No manifest expected-marker change without proof.
- No action or mutation protocol claims.

## Decisions

1. Probe count/diagnostic rows separately from form-marker rows.
   Count-marker contracts and form identity contracts have different evidence
   shapes.

2. Treat `diag-window-get-form-path` as proof-attempt plus broad-range input.
   It may need the separate range-isolation change before acceptance.

3. Retain negative observations.
   A transport-ok marker mismatch is useful protocol evidence but must remain
   non-accepted.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Focused replay/direct probes for five missing-proof rows | Probe command transcript and retained summary per row family | `scenario_log`, `data_assertion`, `cleanup_evidence` | `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/<probe-id>/` | required | `project:qa-mcp` | N/A | High: live endpoint or dynamic adaptation may block proof |
| Managed form layout | Fixture form and diagnostic command surfaces observed by probes | Active form/window or response marker proof for target fixture | `active_window`, `form_tree` or compact response-marker summary | `.artifacts/openspec/probe-manager-fixture-v1-missing-proof-rows/<run-id>/ui-proof/` | required | `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A | Medium: provider UI proof can be unavailable, but response-marker proof may still be enough |
| BSL-only module edit | 1C BSL source | N/A unless a direct-probe helper requires manager/client BSL source edits | `bsl_diagnostics` if edited | `.artifacts/openspec/probe-manager-fixture-v1-missing-proof-rows/<run-id>/bsl-diagnostics/` | N/A | `project:qa-mcp`, `/opt/edt-lab` | Planned work should use existing fixture sources and Python tooling | Medium: if helper BSL changes become necessary, matrix row must become required |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |

## Risks / Trade-offs

- Some rows may need endpoint retargeting rather than replay. Mitigation:
  record wrong-endpoint proof and pass candidate corrections to the marker
  reconciliation change.
- Broad windows may still block acceptance. Mitigation: feed those rows to
  `isolate-manager-fixture-v1-ambiguous-pending-ranges`.
