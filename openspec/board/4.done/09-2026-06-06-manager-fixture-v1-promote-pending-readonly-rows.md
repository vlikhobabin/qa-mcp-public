# 09. Manager Fixture V1: Promote Pending Read-Only Rows

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Order Index
09

## Source
- 2026-06-06 manager fixture V1 pending-row review
- `openspec/board/4.done/08-2026-06-06-manager-fixture-v1-resolve-pending-readonly-rows.md`
- `docs/protocol-research/status-report-2026-06-06.md`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`
- `docs/protocol-research/evidence/manager-fixture-v1-pending-readonly/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`
- `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-pending-readonly-review/`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-promotion-final-readiness/`

## Summary
Promote the remaining nine manager fixture V1 read-only pending rows to
accepted protocol mappings where current-run replay or direct-probe proof can
be retained. Rows that still cannot be accepted must keep precise blocker
evidence, not disappear from the report.

The current cleanup route is already useful: all 17 manager fixture V1 command
windows are joined to proxy traffic and 8 rows are accepted. This card focuses
on the remaining 9 rows that block treating V1 read-only coverage as complete
enough for V2 safe-action acceptance.

## Current State
- Cleanup run: `20260606-live-fixture-ci-bootstrap-full-readonly-cleanup`.
- Joined command windows: `17/17`.
- Accepted replay/probe rows: `8/17`.
- Pending rows: `9/17`.
- Accepted rows currently require replay or direct-probe evidence matching the
  current cleanup `case_id`, manager frame range and `normalized_hash`.
- Joined frame evidence alone is not accepted protocol knowledge.
- Pending-promotion pass result: `0/9` rows promoted.
- Final V2 live safe-action readiness: blocked unless runtime proof is restored
  or an explicit residual-risk decision is recorded.

Current accepted rows:

- `tm-v1-active-window`
- `tm-v1-active-form`
- `tm-v1-diag-window-find-field-marker`
- `tm-v1-diag-form-find-field-marker`
- `tm-v1-field-version`
- `tm-v1-field-string`
- `tm-v1-commandbar-main`
- `tm-v1-pages-main`

## Pending Row Worklist
| case id | frames | blocker | current observation | required next proof |
| --- | ---: | --- | --- | --- |
| `tm-v1-diag-command-interface-dump` | `18..20` | missing replay/direct-probe evidence | no marker extracted; expected `ci_children_count=` | Run focused command-interface direct probe or replay and define a stable count-marker contract. |
| `tm-v1-diag-window-children` | `21..22` | missing replay/direct-probe evidence | no marker extracted; expected `window_children_count=` | Run focused window-children direct probe or replay and retain observed child/count contract. |
| `tm-v1-diag-window-find-form-marker` | `23..25` | wrong expected marker or wrong endpoint candidate | observed `QA MCP Protocol Fixture V1`; expected `PF_FIXTURE_VERSION` | Prove this endpoint intentionally returns the title/form marker, or retarget the endpoint that returns version semantics. |
| `tm-v1-diag-window-get-form-path` | `26..106` | ambiguous frame range | observed `QA MCP Protocol Fixture V1`; expected `PF_FIXTURE_VERSION` | Isolate the form-path endpoint from the 81-frame window before accepting semantics. |
| `tm-v1-form-summary` | `117..119` | wrong expected marker or wrong endpoint candidate | observed `QA MCP Protocol Fixture V1`; expected `PF_FIXTURE_VERSION` | Run current-run form-summary probe; older rejected probe remains supporting only. |
| `tm-v1-checkbox-true` | `126..130` | replay marker mismatch | capture has `CheckBox` and `PF_CHECKBOX_TRUE`; replay observed `PF_CHECKBOX_TRUE` only | Reconcile older accepted checkbox probe with current run range/hash or keep mismatch. |
| `tm-v1-button-inert` | `131..390` | ambiguous frame range and marker mismatch | replay observed `pf_button_inert`; expected `TestedFormButton` | Isolate the 260-frame window or prove target-marker-only semantics with a current-run probe. |
| `tm-v1-table-items` | `396..401` | wrong expected marker or wrong endpoint candidate | observed `PF_TABLE_ITEMS`; expected `PF_ROW_001` | Decide whether table summary returns table identity only or needs a row endpoint. |
| `tm-v1-group-main` | `408..413` | replay marker mismatch | capture has `PF_FORM_MAIN` and `PF_GROUP_MAIN`; replay observed `PF_GROUP_MAIN` only | Prove group identity semantics or keep the `PF_FORM_MAIN` mismatch. |

## Expected Scope
- Start or attach a clean Windows-native TestClient endpoint for the manager
  fixture route.
- Run focused replay or direct probes for the five not-attempted rows:
  `tm-v1-diag-command-interface-dump`, `tm-v1-diag-window-children`,
  `tm-v1-diag-window-find-form-marker`,
  `tm-v1-diag-window-get-form-path` and `tm-v1-form-summary`.
- Reconcile the four current-run marker-mismatch rows:
  `tm-v1-checkbox-true`, `tm-v1-button-inert`, `tm-v1-table-items` and
  `tm-v1-group-main`.
- Isolate broad joined windows before accepting rows that currently span too
  much traffic, especially `tm-v1-diag-window-get-form-path` and
  `tm-v1-button-inert`.
- Apply candidate manifest expected-marker corrections only after current-run
  replay or direct-probe evidence proves the corrected semantics.
- Regenerate the cleanup live-join report with all new accepted and
  non-accepted probe summaries folded in.
- Update protocol research docs and evidence index with final accepted/pending
  counts and V2 readiness.

## Tooling And Evidence Needs
- Use Windows-native capture/replay entrypoints only.
- Use `tools/protocol-research/replay_probe.py` for replay evidence when the
  current frame family can be safely adapted.
- Use `tools/protocol-research/manager_fixture_marker_probe.py` or a narrow
  successor for direct marker probes when replay is not the right shape.
- Use `tools/protocol-research/report_manager_fixture_v1.py` to regenerate
  reviewed live-join evidence.
- Preserve raw captures and generated replay output under ignored
  `runtime/protocol-research/` paths.
- Preserve compact reviewed evidence under `docs/protocol-research/evidence/`.

## Out Of Scope
- V2 safe UI actions.
- Text input, clicks, page switching, table selection or mutation acceptance.
- Business object writes, posting, saving, data exchange or settings mutation.
- Accepting a row by changing only the manifest expected marker.
- Accepting joined rows without replay or direct-probe proof tied to the
  current cleanup `case_id`, frame range and `normalized_hash`.

## Acceptance
- All nine pending rows are attempted or explicitly retained with a fresh
  current-run blocker.
- Any promoted row has replay or direct-probe evidence that matches the current
  cleanup `case_id`, manager frame range and `normalized_hash`.
- Any manifest expected-marker correction is backed by retained current-run
  evidence and does not weaken the accepted gate.
- Broad frame windows are either isolated or kept non-accepted with a precise
  isolation gap.
- The regenerated live-join report still shows all 17 command windows and has
  coherent accepted/pending counts.
- Protocol research docs state whether manager fixture V1 read-only coverage
  now unblocks V2 safe-action acceptance, remains blocked, or requires an
  explicit residual-risk decision.
- Cleanup stops only runner-owned 1C, proxy and manager PIDs.

## Change Set
1. `openspec/changes/archive/2026-06-06-prepare-manager-fixture-v1-pending-probe-runtime/`
2. `openspec/changes/archive/2026-06-06-probe-manager-fixture-v1-missing-proof-rows/`
3. `openspec/changes/archive/2026-06-06-isolate-manager-fixture-v1-ambiguous-pending-ranges/`
4. `openspec/changes/archive/2026-06-06-reconcile-manager-fixture-v1-marker-contracts/`
5. `openspec/changes/archive/2026-06-06-republish-manager-fixture-v1-pending-promotion-readiness/`

## Verify
- 2026-06-06T19:14:16+03:00 passed:
  `bin\openspec.cmd validate prepare-manager-fixture-v1-pending-probe-runtime --strict`.
- 2026-06-06T19:14:16+03:00 passed:
  `bin\openspec.cmd validate probe-manager-fixture-v1-missing-proof-rows --strict`.
- 2026-06-06T19:14:16+03:00 passed:
  `bin\openspec.cmd validate isolate-manager-fixture-v1-ambiguous-pending-ranges --strict`.
- 2026-06-06T19:14:16+03:00 passed:
  `bin\openspec.cmd validate reconcile-manager-fixture-v1-marker-contracts --strict`.
- 2026-06-06T19:42:19+03:00 passed:
  JSON parse for final `runtime_summary.json`, `frame_join_report.json`,
  `readiness_summary.json`, missing-proof summary, isolation summary and
  marker-contract summary.
- 2026-06-06T19:42:19+03:00 passed:
  `python -m pytest tests\test_manager_fixture_v1_report.py` with 10 passed.
- 2026-06-06T19:42:19+03:00 passed:
  `bin\openspec.cmd validate republish-manager-fixture-v1-pending-promotion-readiness --strict`.
- 2026-06-06T19:42:19+03:00 passed:
  `bin\openspec.cmd validate qa-mcp-protocol-lab --strict`.
- 2026-06-06T19:42:19+03:00 passed:
  `bin\openspec.cmd validate --all` before archive with 2 passed, 0 failed.
- 2026-06-06T19:42:19+03:00 passed:
  `bin\openspec.cmd validate --all` after archive with 1 passed, 0 failed.
- 2026-06-06T19:42:19+03:00 passed:
  `git diff --check -- openspec/changes openspec/board docs/protocol-research tools/protocol-research tests`
  with LF-to-CRLF warnings only for Markdown docs.

## Archive
- `openspec/changes/archive/2026-06-06-prepare-manager-fixture-v1-pending-probe-runtime/`
- `openspec/changes/archive/2026-06-06-probe-manager-fixture-v1-missing-proof-rows/`
- `openspec/changes/archive/2026-06-06-isolate-manager-fixture-v1-ambiguous-pending-ranges/`
- `openspec/changes/archive/2026-06-06-reconcile-manager-fixture-v1-marker-contracts/`
- `openspec/changes/archive/2026-06-06-republish-manager-fixture-v1-pending-promotion-readiness/`

## Related
- `openspec/board/4.done/08-2026-06-06-manager-fixture-v1-resolve-pending-readonly-rows.md`
- `openspec/board/1.backlog/06-2026-06-04-manager-fixture-v2-safe-action-runner.md`
- `openspec/changes/archive/2026-06-06-prepare-manager-fixture-v1-pending-probe-runtime/`
- `openspec/changes/archive/2026-06-06-probe-manager-fixture-v1-missing-proof-rows/`
- `openspec/changes/archive/2026-06-06-isolate-manager-fixture-v1-ambiguous-pending-ranges/`
- `openspec/changes/archive/2026-06-06-reconcile-manager-fixture-v1-marker-contracts/`
- `openspec/changes/archive/2026-06-06-republish-manager-fixture-v1-pending-promotion-readiness/`
- `docs/protocol-research/status-report-2026-06-06.md`
- `docs/protocol-research/protocol-corpus-runner.md`
- `docs/protocol-research/evidence-index.md`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`
- `docs/protocol-research/evidence/manager-fixture-v1-pending-readonly/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`
- `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-pending-readonly-review/`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-readonly-runtime-preflight/`
- `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-pending-missing-proof-runtime-gap/`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-ambiguous-range-isolation/`
- `docs/protocol-research/evidence/manager-fixture-v1-marker-contracts/20260606-pending-marker-contract-reconciliation/`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-pending-promotion-final-readiness/`
- `tools/protocol-research/replay_probe.py`
- `tools/protocol-research/manager_fixture_marker_probe.py`
- `tools/protocol-research/report_manager_fixture_v1.py`
- `tools/protocol-research/run_protocol_capture.ps1`

## Result
All five OpenSpec changes were implemented, verified, synced to
`qa-mcp-protocol-lab` and archived.

The pending-promotion pass attempted to resolve the nine remaining manager
fixture V1 read-only pending rows. It promoted `0/9` rows. The final reviewed
state remains 17 joined command windows, 8 accepted replay/probe mappings and
9 pending rows.

The work did preserve the missing evidence instead of losing it:

- runtime preflight shows a `runtime_gap` before 1C process startup because the
  default Vanessa EPF asset is missing;
- five missing-proof rows have current cleanup frame/hash blockers and next
  routes;
- two broad rows remain non-accepted because form-path and button-state
  operation windows were not isolated;
- marker-contract reconciliation applies no catalog changes and accepts no row
  by expected-marker change alone.

V2 safe-action live acceptance remains blocked. V2 planning may continue on
paper, but live acceptance requires restored runtime proof for the needed V1
prerequisites or an explicit residual-risk decision.

## Next
- none for this card.

## Change Plan Notes
This card is decomposed into five OpenSpec changes. The order keeps runtime
readiness and evidence quality ahead of row promotion so accepted protocol
claims remain tied to current-run frame ranges, normalized hashes and retained
probe/replay output.

## Change 1 - prepare-manager-fixture-v1-pending-probe-runtime
Why: the pending-row probes require a clean, owned Windows-native TestClient
endpoint before any row can be promoted.

Goal: prove the manager fixture V1 route is runnable, identify the active
endpoint and capture runner-owned cleanup state.

Scope: runtime preflight, provider-gap diagnosis if the endpoint is unavailable,
and evidence-retention path checks.

Acceptance: either a clean endpoint is ready for focused probes, or the change
publishes a precise blocker that later changes consume.

Depends on: none.

## Change 2 - probe-manager-fixture-v1-missing-proof-rows
Why: five pending rows have no current-run replay or direct-probe proof.

Goal: attempt the missing-proof rows and retain accepted or blocked evidence for
each one.

Scope: focused replay/direct probes for command-interface dump, window children,
find-form marker, form-path and form-summary rows.

Acceptance: every row is attempted with evidence tied to current `case_id`,
frame range and `normalized_hash`, or retained with a fresh blocker.

Depends on: `prepare-manager-fixture-v1-pending-probe-runtime`.

## Change 3 - isolate-manager-fixture-v1-ambiguous-pending-ranges
Why: two pending rows have broad frame windows that can hide multiple protocol
operations.

Goal: isolate `tm-v1-diag-window-get-form-path` and `tm-v1-button-inert` before
any acceptance decision.

Scope: narrow probes/replay segmentation and report annotations for ambiguous
frame spans.

Acceptance: each broad row is narrowed enough for acceptance or kept pending
with a precise isolation gap.

Depends on: `prepare-manager-fixture-v1-pending-probe-runtime`.

## Change 4 - reconcile-manager-fixture-v1-marker-contracts
Why: four rows have marker mismatches or candidate endpoint uncertainty.

Goal: decide whether each mismatch is a legitimate endpoint contract, a manifest
expected-marker correction, a retargeting need or a retained blocker.

Scope: evidence-gated reconciliation for checkbox, button, table and group
rows, plus any marker-contract findings from changes 2 and 3.

Acceptance: no expected-marker correction is made without retained current-run
proof, and the accepted gate is not weakened.

Depends on:
`probe-manager-fixture-v1-missing-proof-rows`,
`isolate-manager-fixture-v1-ambiguous-pending-ranges`.

## Change 5 - republish-manager-fixture-v1-pending-promotion-readiness
Why: the final result must be visible in project docs, evidence index and V2
readiness language.

Goal: regenerate the manager fixture V1 reviewed report and publish final
accepted/pending counts with a V2 readiness statement.

Scope: report regeneration, compact evidence index/docs update and card-result
summary.

Acceptance: all 17 joined windows remain represented, final counts are
coherent, and V2 readiness is stated as unblocked, blocked or residual-risk.

Depends on all previous changes in this card.

## Log
- 2026-06-06T18:53:45+03:00 card created from the manager fixture V1
  pending-row review.
- 2026-06-06T19:03:19+03:00 decomposed with `$opsx-ff`, moved to `2.todo/`
  and linked to five active OpenSpec changes.
- 2026-06-06T19:42:19+03:00 all five changes implemented, verified, synced
  and archived; card moved to `4.done/`.
- 2026-06-06T21:00:37+03:00 published with `$opsx-pub`; scoped commit
  includes card-owned docs, evidence, spec sync and archived changes.
