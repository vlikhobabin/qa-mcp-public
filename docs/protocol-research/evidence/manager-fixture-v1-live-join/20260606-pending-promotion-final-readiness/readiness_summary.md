# Manager Fixture V1 Pending Promotion Readiness

- Source cleanup run: `20260606-live-fixture-ci-bootstrap-full-readonly-cleanup`
- Final report: `frame_join_report.json`
- Joined command windows: `17/17`
- Accepted before this card: `8/17`
- Accepted after this card: `8/17`
- Promoted by this card: `0`
- Pending after this card: `9/17`

## Verdict

Manager fixture V1 read-only coverage remains useful but incomplete. The
pending-promotion work did not promote additional rows because the focused
runtime endpoint is unavailable and the remaining rows still have unresolved
marker-contract, endpoint-choice or broad-range isolation gaps.

V2 safe-action live acceptance remains blocked. V2 planning can continue on
paper, but live acceptance should wait for runtime restoration plus focused V1
proof, or for an explicit residual-risk decision to proceed while the listed
read-only rows remain pending.

## Accepted Gate

The final report retains eight accepted protocol mappings. Each accepted row
has replay evidence matching the joined `case_id`, manager frame range and
`normalized_hash`. Joined frame evidence alone remains insufficient.

Accepted rows:

- `tm-v1-active-window`
- `tm-v1-active-form`
- `tm-v1-diag-window-find-field-marker`
- `tm-v1-diag-form-find-field-marker`
- `tm-v1-field-version`
- `tm-v1-field-string`
- `tm-v1-commandbar-main`
- `tm-v1-pages-main`

## Pending Rows

| case | frames | blocker | next route |
| --- | ---: | --- | --- |
| `tm-v1-diag-command-interface-dump` | `18..20` | No clean TestClient endpoint was available; command-interface count-marker contract was not directly probed. | Restore the Vanessa EPF/runtime endpoint, then run a focused command-interface probe or replay. |
| `tm-v1-diag-window-children` | `21..22` | No clean TestClient endpoint was available; window-children count contract was not directly probed. | Restore the endpoint, then run a focused window-children probe or replay. |
| `tm-v1-diag-window-find-form-marker` | `23..25` | Joined evidence observes the title/form marker, but title semantics versus version semantics are unproven. | Restore runtime and prove endpoint semantics before changing the expected marker. |
| `tm-v1-diag-window-get-form-path` | `26..106` | The row covers 81 manager frames and has no semantic payload token that isolates the operation. | Rerun a focused capture or add narrower side-channel boundaries. |
| `tm-v1-form-summary` | `117..119` | Older direct-probe evidence is supporting only; no current endpoint was available for marker proof. | Restore runtime and rerun form-summary direct proof. |
| `tm-v1-checkbox-true` | `126..130` | Current replay observed only the target marker while the cleanup capture also contains the type marker. | Validate checkbox identity and normalized hash with a current-run probe or parser. |
| `tm-v1-button-inert` | `131..390` | The row covers 260 manager frames; target-marker repetition alone is not a minimal operation proof. | Restore runtime and rerun a focused read-only button-state probe with narrower boundaries. |
| `tm-v1-table-items` | `396..401` | Table identity marker is observed, but table-summary versus row-marker semantics are unproven. | Prove table-summary endpoint contract or add a separate row endpoint. |
| `tm-v1-group-main` | `408..413` | Group target marker is observed, but target-marker-only group semantics are not independently proven. | Validate group identity semantics with a current-run direct probe or parser. |

## Supporting Evidence

- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-readonly-runtime-preflight/`
- `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-pending-missing-proof-runtime-gap/`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-ambiguous-range-isolation/`
- `docs/protocol-research/evidence/manager-fixture-v1-marker-contracts/20260606-pending-marker-contract-reconciliation/`
