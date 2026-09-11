# Manager Fixture V1 Replay Probe: Pending Read-Only Review

Source capture:
`runtime/protocol-research/captures/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`

Curated join evidence:
`docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`

Classification evidence:
`docs/protocol-research/evidence/manager-fixture-v1-pending-readonly/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`

## Outcome

No additional row is accepted by this probe review. Four pending rows have
retained current-run transport-level replay observations from the successful
419-frame replay, but each still has a marker mismatch. Five rows were not
attempted because no live TestClient endpoint was available for a focused
Windows-native direct probe during this delivery pass.

The accepted gate remains unchanged: accepted replay/probe evidence must match
the cleanup `case_id`, manager frame range and `normalized_hash`.

## Runtime Availability

Windows-native runtime check:

- no `1cv8` process was present;
- ports `15381`, `15382` and `48001` had no available TestClient endpoint;
- no new replay/direct-probe process was started;
- cleanup scope is empty for this change.

Provider/runtime gap:

```yaml
provider_gap:
  provider_id: project-runtime
  owner_path: project:qa-mcp
  missing_capability: running TestClient endpoint for focused pending-row replay/direct probes
  missing_evidence_type: scenario_log
  impact: no additional pending row can be accepted in this change
  current_workaround: retain current-run negative replay observations and keep not-attempted rows pending
  sensitivity: no credentials or raw payloads copied
```

## Retained Negative Observations

These rows replayed transport-level successfully in the current-run
`summary419` replay, but are not accepted:

| case id | frames | observed marker | missing expected marker | status |
| --- | ---: | --- | --- | --- |
| `tm-v1-checkbox-true` | `126..130` | `PF_CHECKBOX_TRUE` | `CheckBox` | `transport_ok_marker_mismatch` |
| `tm-v1-button-inert` | `131..390` | `pf_button_inert` | `TestedFormButton` | `transport_ok_marker_mismatch` |
| `tm-v1-table-items` | `396..401` | `PF_TABLE_ITEMS` | `PF_ROW_001` | `transport_ok_marker_mismatch` |
| `tm-v1-group-main` | `408..413` | `PF_GROUP_MAIN` | `PF_FORM_MAIN` | `transport_ok_marker_mismatch` |

## Not Attempted In This Pass

| case id | reason |
| --- | --- |
| `tm-v1-diag-command-interface-dump` | No current live TestClient endpoint was available; summary419 did not retain endpoint marker proof. |
| `tm-v1-diag-window-children` | No current live TestClient endpoint was available; summary419 did not retain endpoint marker proof. |
| `tm-v1-diag-window-find-form-marker` | No current live TestClient endpoint was available; endpoint/expected-marker contract still needs review. |
| `tm-v1-diag-window-get-form-path` | No current live TestClient endpoint was available; the broad frame window needs isolation before acceptance. |
| `tm-v1-form-summary` | No current live TestClient endpoint was available; older direct probe remains rejected/supporting only. |

## Raw Output Policy

Raw replay output remains under ignored `runtime/protocol-research/replay-probe/`
paths. This reviewed evidence copies only compact marker, range and hash facts.
