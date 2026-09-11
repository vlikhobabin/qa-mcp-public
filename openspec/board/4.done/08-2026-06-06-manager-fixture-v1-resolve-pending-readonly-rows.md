# 08. Manager Fixture V1: Resolve Pending Read-Only Rows

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Order Index
08

## Source
- 2026-06-06 protocol research review session
- `docs/protocol-research/status-report-2026-06-06.md`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`
- `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-cleanup-readonly-fields/`
- `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-cleanup-commandbar-main/`
- `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-cleanup-summary419-uipath/`
- `docs/protocol-research/protocol-corpus-runner.md`

## Summary
Resolve the nine non-accepted rows from the current manager fixture V1
read-only cleanup run before starting V2 safe-action protocol work. The goal
is to classify each pending row, add retained replay or direct-probe proof
where possible, adjust manifest expectations only when evidence proves they
are wrong, and republish the cleanup live-join evidence without weakening the
accepted mapping gate.

Current pending rows:

- `tm-v1-diag-command-interface-dump`
- `tm-v1-diag-window-children`
- `tm-v1-diag-window-find-form-marker`
- `tm-v1-diag-window-get-form-path`
- `tm-v1-form-summary`
- `tm-v1-checkbox-true`
- `tm-v1-button-inert`
- `tm-v1-table-items`
- `tm-v1-group-main`

## Expected Scope
- Classify every pending row as wrong expected marker, wrong endpoint,
  missing replay/direct-probe evidence, ambiguous frame range, or retained
  pending with a precise reason.
- Preserve the current acceptance rule: replay/probe evidence must match the
  joined `case_id`, manager frame range and `normalized_hash`.
- Add or run focused replay/direct-probe support for rows whose current
  frames can be validated safely.
- Retain positive and negative replay/probe summaries under compact reviewed
  evidence paths.
- Update manifest expected markers only where the current response proves the
  previous marker was too strict or pointed at the wrong surface.
- Regenerate the cleanup live-join report and corpus rows with all accepted
  replay/probe summaries folded in.
- Update protocol research docs and evidence index with the final accepted
  and pending state.

## Out Of Scope
- V2 safe UI actions.
- Text input, clicks, page switches, table selection or mutation acceptance.
- Business object writes or fixture state mutation.
- Accepting joined rows without replay/direct-probe proof.
- Treating older probe evidence from a different run as accepted proof unless
  it is reconciled with the current cleanup run range and normalized hash.

## Acceptance
- Every one of the nine pending rows has a retained classification artifact.
- Rows that can be accepted have replay/direct-probe evidence matching the
  current cleanup run `case_id`, frame range and `normalized_hash`.
- Rows that remain pending have precise, actionable reasons and owner route.
- The cleanup live-join report still shows all 17 joined command windows and
  only marks rows accepted when the accepted gate is satisfied.
- Protocol research docs identify whether manager fixture V1 read-only
  coverage is complete enough to unblock V2 safe-action planning.

## Change Set
- `openspec/changes/archive/2026-06-06-classify-manager-fixture-v1-pending-readonly-rows/`
- `openspec/changes/archive/2026-06-06-probe-manager-fixture-v1-pending-readonly-rows/`
- `openspec/changes/archive/2026-06-06-publish-manager-fixture-v1-readonly-cleanup-acceptance/`

## Verify
- `openspec validate classify-manager-fixture-v1-pending-readonly-rows --strict`
- `openspec validate probe-manager-fixture-v1-pending-readonly-rows --strict`
- `openspec validate publish-manager-fixture-v1-readonly-cleanup-acceptance --strict`
- `openspec validate --all`
- `git diff --check -- openspec/changes openspec/board docs/protocol-research tools/protocol-research tests`

## Archive
- `openspec/changes/archive/2026-06-06-classify-manager-fixture-v1-pending-readonly-rows/`
- `openspec/changes/archive/2026-06-06-probe-manager-fixture-v1-pending-readonly-rows/`
- `openspec/changes/archive/2026-06-06-publish-manager-fixture-v1-readonly-cleanup-acceptance/`

## Related
- `openspec/board/4.done/07-2026-06-05-manager-fixture-v1-live-corpus-pipeline.md`
- `openspec/board/1.backlog/02-2026-06-04-client-fixture-v2-safe-actions.md`
- `openspec/board/1.backlog/06-2026-06-04-manager-fixture-v2-safe-action-runner.md`
- `docs/protocol-research/status-report-2026-06-06.md`
- `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`
- `docs/protocol-research/evidence/manager-fixture-v1-pending-readonly/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/`
- `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/20260606-pending-readonly-review/`
- `openspec/changes/archive/2026-06-06-classify-manager-fixture-v1-pending-readonly-rows/`
- `openspec/changes/archive/2026-06-06-probe-manager-fixture-v1-pending-readonly-rows/`
- `openspec/changes/archive/2026-06-06-publish-manager-fixture-v1-readonly-cleanup-acceptance/`

## Result
All three OpenSpec changes were implemented, verified, synced to
`qa-mcp-protocol-lab` and archived.

The nine pending manager fixture V1 read-only rows now have retained
classification evidence. A pending-readonly replay review preserves four
current-run transport-level marker-mismatch observations and a runtime gap for
the five rows that need a fresh live TestClient endpoint. The cleanup live-join
report was regenerated with all retained summaries folded in; accepted coverage
remains 8 of 17 rows, and 9 rows remain pending with precise next routes.

V2 safe-action protocol acceptance remains blocked unless a later project
decision explicitly accepts the residual risk of proceeding while these V1
read-only rows remain pending.

## Next
- none for this card; V2 safe-action acceptance remains gated by the pending
  V1 read-only rows or an explicit residual-risk decision.

## Change 1: `classify-manager-fixture-v1-pending-readonly-rows`

### Why
The cleanup run has joined traffic for all 17 commands, but nine rows remain
non-accepted. The next work needs a row-by-row diagnosis before any manifest
or replay changes are made.

### Goal
Publish a compact classification for the nine pending rows that explains the
blocking reason and the exact evidence needed for promotion or continued
pending status.

### Scope
- Inspect the current cleanup `frame_join_report.json`, `corpus_cases.jsonl`,
  runtime manifest and replay summaries.
- Compare `target_marker`, `expected_marker`, observed response markers,
  endpoint shape, frame range and normalized hash per pending row.
- Publish a classification summary and machine-readable classification JSON.
- Identify manifest marker corrections as candidates only; do not apply them
  without evidence.

### Acceptance
- All nine pending rows have a single current classification.
- Classification values are actionable and stable enough for tooling/tests.
- No row is promoted to accepted by classification alone.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-06-06-classify-manager-fixture-v1-pending-readonly-rows/`

### Notes For `$openspec-ff-change`
- Treat the 20260606 cleanup run as the source of truth for current acceptance.

## Change 2: `probe-manager-fixture-v1-pending-readonly-rows`

### Why
Pending rows need retained replay or direct-probe proof tied to the current
cleanup run before they can become accepted protocol mappings.

### Goal
Run or extend focused replay/direct-probe support for pending rows and retain
positive and negative proof without weakening the accepted gate.

### Scope
- Use the classification output to select rows and probe strategy.
- Reuse `replay_probe.py` and `manager_fixture_marker_probe.py` where possible.
- Add narrow replay/probe support only when current tooling cannot validate a
  safe read-only row.
- Record dynamic-field adaptations, response markers, normalized hashes and
  negative controls.
- Keep rows non-accepted when proof is absent, mismatched or from the wrong
  run.

### Acceptance
- Every attempted row has retained replay/probe summary evidence.
- Accepted probe summaries match current cleanup `case_id`, frame range and
  normalized hash.
- Non-accepted probe observations remain visible with mismatch details.

### Depends On
- `classify-manager-fixture-v1-pending-readonly-rows`

### Related
- `openspec/changes/archive/2026-06-06-probe-manager-fixture-v1-pending-readonly-rows/`

### Notes For `$openspec-ff-change`
- Prefer read-only probes and owned-process cleanup; do not add action or
  mutation semantics.

## Change 3: `publish-manager-fixture-v1-readonly-cleanup-acceptance`

### Why
The project needs one reviewed manager fixture V1 cleanup state before deciding
whether V2 safe-action planning is unblocked.

### Goal
Regenerate and publish the cleanup live-join report with all accepted
replay/probe summaries folded in, plus docs that state the final accepted and
remaining pending read-only coverage.

### Scope
- Run the manager fixture V1 reporter against the cleanup runtime directory
  with all retained replay/probe summaries.
- Update reviewed live-join evidence, corpus rows, status report, README or
  protocol-corpus docs as needed.
- Update the evidence index with new classification/probe/report paths.
- Preserve raw traffic and replay runtime output under ignored runtime paths.

### Acceptance
- The reviewed cleanup report has coherent accepted/pending counts.
- Accepted rows include explicit replay/probe evidence links.
- Remaining pending rows have exact reasons and next route.
- Docs state whether manager fixture V1 read-only coverage is sufficient for
  V2 triage.

### Depends On
- `classify-manager-fixture-v1-pending-readonly-rows`
- `probe-manager-fixture-v1-pending-readonly-rows`

### Related
- `openspec/changes/archive/2026-06-06-publish-manager-fixture-v1-readonly-cleanup-acceptance/`

### Notes For `$openspec-ff-change`
- Do not archive or claim V1 completion if required pending rows still lack
  proof and no accepted residual-risk decision is recorded.

## Log
- 2026-06-06T17:02:12+03:00 card created and decomposed into three OpenSpec changes
- 2026-06-06T17:45:00+03:00 all three changes implemented, verified, synced and archived; card moved to `4.done`
- 2026-06-06T18:21:46+03:00 published after first committing the previous
  manager fixture V1 dirty block
