## 1. Range Isolation

- [x] 1.1 Inspect the existing broad windows and event boundaries for
  `tm-v1-diag-window-get-form-path` and `tm-v1-button-inert`.
- [x] 1.2 Run or add a focused isolation capture/replay route for
  `tm-v1-diag-window-get-form-path`.
- [x] 1.3 Run or add a focused isolation capture/replay route for
  `tm-v1-button-inert`.
- [x] 1.4 Generate reviewed isolated corpus rows or explicit isolation-gap
  evidence for each row.
- [x] 1.5 Ensure isolated rows retain request/response sizes, dynamic fields,
  normalized hash and response markers.

## 2. Verification

- [x] 2.1 Run focused tests for reporter/range validation changes.
- [x] 2.2 Confirm broad rows remain non-accepted when isolation fails.
- [x] 2.3 Confirm no action semantics are claimed for `button-inert`.
- [x] 2.4 Run `openspec validate isolate-manager-fixture-v1-ambiguous-pending-ranges --strict`.

## Evidence

- Source frame report:
  `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/frame_join_report.json`.
- Isolation-gap summary:
  `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-ambiguous-range-isolation/isolation_summary.json`.
- `tm-v1-diag-window-get-form-path`: manager frames `26..106`,
  `selected_chunk_count=161`, `request_size=21059`,
  `response_size=17973`, normalized hash
  `0244782c3c4f28c8b3ad0bbf5dfaf37916cb642f0d82debe8543fdd08c71f85a`,
  status `not_isolated`.
- `tm-v1-button-inert`: manager frames `131..390`,
  `selected_chunk_count=519`, `request_size=57888`,
  `response_size=48090`, normalized hash
  `926585521047f8e7e2abe2316dacbbf690142f04867c73cb12c172139a153e86`,
  status `not_isolated`.
- Acceptance guard: both rows stayed `accepted_protocol_mapping=false` and
  `replay_status=pending`.
- Action-safety guard: `tm-v1-button-inert` records
  `action_semantics_claimed=false`.
- Focused test:
  `python -m pytest tests\test_manager_fixture_v1_report.py` passed `10`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Focused capture/replay for broad pending windows | Row-isolation command and reviewed range report | `scenario_log`, `data_assertion`, `cleanup_evidence` | `docs/protocol-research/evidence/manager-fixture-v1-live-join/<isolation-run-id>/` | required | `project:qa-mcp` | N/A | High: platform background traffic may remain inseparable |
| Form module or command | Manager harness command sequence and boundary events | Per-row before/after event timing and boundary waits | `scenario_file`, `scenario_log` | `runtime/protocol-research/captures/<isolation-run-id>/case_events.jsonl` | required | `project:qa-mcp` | N/A | Medium: changing waits can affect timing but should remain read-only |
| Managed form layout | Fixture form state during isolated command | Active window/form or response-marker proof for fixture route | `active_window`, `form_tree` or compact response-marker summary | `.artifacts/openspec/isolate-manager-fixture-v1-ambiguous-pending-ranges/<run-id>/ui-proof/` | required | `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A | Medium: UI provider gaps can limit independent form proof |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |
