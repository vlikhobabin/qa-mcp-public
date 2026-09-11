# Manager Fixture V1 Pending Read-Only Classification

Run id: `20260606-live-fixture-ci-bootstrap-full-readonly-cleanup`

## Outcome

All nine non-accepted rows from the current cleanup run were classified. No row
is promoted by classification alone. The accepted gate remains unchanged:
replay or direct-probe evidence must match the current cleanup `case_id`,
manager frame range and `normalized_hash`.

## Source Evidence

- Live-join report:
  `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/frame_join_report.json`
- Corpus rows:
  `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/corpus_cases.jsonl`
- Runtime manifest:
  `runtime/protocol-research/captures/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/manager_harness_manifest.json`
- Current replay summary:
  `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-cleanup-summary419-uipath/summary.json`

## Classification Table

| case id | frames | primary classification | observed markers | expected marker | next evidence |
| --- | ---: | --- | --- | --- | --- |
| `tm-v1-diag-command-interface-dump` | `18..20` | missing replay/direct-probe evidence | none extracted | `ci_children_count=` | Run direct command-interface probe or replay and define count-marker contract. |
| `tm-v1-diag-window-children` | `21..22` | missing replay/direct-probe evidence | none extracted | `window_children_count=` | Run direct window-children probe or replay and retain observed child/count contract. |
| `tm-v1-diag-window-find-form-marker` | `23..25` | wrong expected marker or wrong endpoint candidate | `QA MCP Protocol Fixture V1` | `PF_FIXTURE_VERSION` | Probe whether this endpoint returns title/form marker or should target version through another endpoint. |
| `tm-v1-diag-window-get-form-path` | `26..106` | ambiguous frame range | `QA MCP Protocol Fixture V1` | `PF_FIXTURE_VERSION` | Isolate form-path endpoint from the 81-frame window before accepting semantics. |
| `tm-v1-form-summary` | `117..119` | wrong expected marker or wrong endpoint candidate | `QA MCP Protocol Fixture V1` | `PF_FIXTURE_VERSION` | Run current-run form-summary probe; older form-summary marker probe is rejected/supporting only. |
| `tm-v1-checkbox-true` | `126..130` | replay marker mismatch | capture has `CheckBox`, `PF_CHECKBOX_TRUE`; replay observed `PF_CHECKBOX_TRUE` only | `CheckBox` | Reconcile older accepted checkbox probe with current run or keep mismatch. |
| `tm-v1-button-inert` | `131..390` | ambiguous frame range | `PF_BUTTON_INERT`; replay observed `pf_button_inert` | `TestedFormButton` | Isolate the 260-frame window or prove target-marker-only semantics. |
| `tm-v1-table-items` | `396..401` | wrong expected marker or wrong endpoint candidate | `PF_TABLE_ITEMS` | `PF_ROW_001` | Decide whether table summary returns table identity only or needs a row endpoint. |
| `tm-v1-group-main` | `408..413` | replay marker mismatch | capture has `PF_FORM_MAIN`, `PF_GROUP_MAIN`; replay observed `PF_GROUP_MAIN` only | `PF_FORM_MAIN` | Prove group identity semantics or keep PF_FORM_MAIN mismatch. |

## Candidate Manifest Changes

Candidate-only marker changes were identified for:

- `tm-v1-diag-window-find-form-marker`: candidate expected marker
  `QA MCP Protocol Fixture V1`.
- `tm-v1-form-summary`: candidate expected marker
  `QA MCP Protocol Fixture V1`.
- `tm-v1-button-inert`: candidate expected marker `PF_BUTTON_INERT`.
- `tm-v1-table-items`: candidate expected marker `PF_TABLE_ITEMS`.
- `tm-v1-group-main`: candidate expected marker `PF_GROUP_MAIN`.

These are not applied or accepted by this classification step. They require
current-run replay or direct-probe evidence before promotion.

## Notes

- Older marker-probe evidence for `tm-v1-checkbox-true` remains supporting
  context only until it is reconciled with the current cleanup run range and
  normalized hash.
- Joined response markers and replay endpoint markers can differ. The replay
  observation is the current blocker for `tm-v1-checkbox-true` and
  `tm-v1-group-main`.
- `tm-v1-diag-window-get-form-path` and `tm-v1-button-inert` have broad joined
  windows and should be isolated before any accepted dictionary entry is
  claimed.
