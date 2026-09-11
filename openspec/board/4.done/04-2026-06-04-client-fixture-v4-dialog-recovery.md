# 04. Client Fixture Processor V4: Dialogs And Recovery

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Order Index
80

## Source
- 2026-06-04 planning session
- `docs/protocol-research/client-fixture-processor-roadmap.md`
- V1/V2/V3 client fixture processor cards
- Closed V2 safe-action readiness, tooling and focused-proof cards
- Closed V3 mutation sandbox surface and candidate-only evidence/promotion
  cards

## Summary
Complete the fixture processor with complex UI scenarios: warnings, questions,
modal forms, expected errors, waits and recovery paths. V4 should provide the
remaining controlled surfaces needed for advanced TestClient protocol
research without turning the fixture into business functionality.

## Expected Scope
- Add warning and question scenarios with deterministic text markers.
- Add one or more modal/dialog form scenarios with stable open/close markers.
- Add expected error scenarios that return controlled diagnostic text.
- Add wait/progress scenarios with bounded duration and observable state.
- Add cancel/retry/recovery paths for dialog and wait scenarios.
- Ensure every scenario can return to the baseline fixture state.
- Document which scenarios are safe, which are mutation-like and which require
  special recovery evidence.

## Out Of Scope
- Real business workflow automation.
- Unbounded waits or background jobs.
- External services, files, mail, crypto, printing or OS dialogs.
- Platform-version portability claims without separate evidence.

## Acceptance
- Dialog and recovery scenarios are deterministic and bounded.
- Every scenario has explicit pre-state, expected result and recovery markers.
- Failed scenario execution can be reset without restoring the infobase.
- Capture/probe tooling can distinguish expected errors from infrastructure
  failures.
- V4 completes the planned fixture processor surface; later changes are
  targeted additions for newly discovered platform API classes.

## Delivery Gate
- Treat the manager fixture V2 safe-action runner, first focused V2 proof, V3
  mutation sandbox surface and V3 candidate-only mutation evidence/promotion
  prerequisites as satisfied by the related `4.done` cards.
- V4 delivery may start as fixture-local dialog, wait, expected-error and
  recovery work, but protocol mappings remain candidate unless replay, direct
  Python-manager probe or typed contract proof supports accepted status.

## Change Set
- `openspec/changes/v4-dialog-surface-model/`
- `openspec/changes/v4-bounded-wait-error-scenarios/`
- `openspec/changes/v4-dialog-recovery-verification/`
- `openspec/changes/v4-dialog-corpus-manifest-updates/`

## Verify
- `bin\openspec.cmd validate v4-dialog-surface-model --strict`
- `bin\openspec.cmd validate v4-bounded-wait-error-scenarios --strict`
- `bin\openspec.cmd validate v4-dialog-recovery-verification --strict`
- `bin\openspec.cmd validate v4-dialog-corpus-manifest-updates --strict`
- `bin\openspec.cmd validate --all`
- `git diff --check -- openspec/changes/v4-dialog-surface-model openspec/changes/v4-bounded-wait-error-scenarios openspec/changes/v4-dialog-recovery-verification openspec/changes/v4-dialog-corpus-manifest-updates openspec/board`

## Archive
- `openspec/changes/archive/2026-06-09-v4-dialog-surface-model/`
- `openspec/changes/archive/2026-06-09-v4-bounded-wait-error-scenarios/`
- `openspec/changes/archive/2026-06-09-v4-dialog-recovery-verification/`
- `openspec/changes/archive/2026-06-09-v4-dialog-corpus-manifest-updates/`

## Related
- `docs/protocol-research/client-fixture-processor-roadmap.md`
- `openspec/board/4.done/01-2026-06-04-client-fixture-v1-control-surface.md`
- `openspec/board/4.done/02-2026-06-04-client-fixture-v2-safe-actions.md`
- `openspec/board/4.done/10-2026-06-07-v2-readiness-docs-and-safety-contract.md`
- `openspec/board/4.done/40-2026-06-07-v2-safe-action-tooling-pipeline.md`
- `openspec/board/4.done/06-2026-06-04-manager-fixture-v2-safe-action-runner.md`
- `openspec/board/4.done/50-2026-06-07-v2-first-focused-safe-action-proof.md`
- `openspec/board/4.done/03-2026-06-04-client-fixture-v3-mutation-sandbox-surface.md`
- `openspec/board/4.done/70-2026-06-08-client-fixture-v3-mutation-evidence-promotion.md`
- `openspec/changes/v4-dialog-surface-model/`
- `openspec/changes/v4-bounded-wait-error-scenarios/`
- `openspec/changes/v4-dialog-recovery-verification/`
- `openspec/changes/v4-dialog-corpus-manifest-updates/`
- `docs/protocol-research/corpus-evidence-contract.md`
- `docs/protocol-research/evidence/client-fixture-v4-dialog-recovery/`
- `docs/protocol-research/safe-ui-action-scope.md`

## Result
published; V4 fixture-local dialog, expected-error, bounded-wait and recovery
markers are implemented in the client fixture source and deployed to the live
client infobase, with candidate-only manifest and runtime evidence retained

## Next
- none; V4 accepted protocol mapping promotion remains a separate proof-gated
  follow-up

## Change Plan Notes
The upstream V2/V3 delivery gate is satisfied. Keep accepted protocol mapping
promotion proof-gated; V4 runtime rows can publish candidate evidence without
weakening V1/V2/V3 acceptance boundaries.

## Change 1: `v4-dialog-surface-model`

### Why
V4 needs deterministic dialog markers before handlers or captures can be
trusted.

### Goal
Define fixture-local warning, question and modal-form state markers plus
safety classification.

### Scope
- Define dialog family, lifecycle, expected text, selected result and recovery
  markers.
- Define baseline/reset expectations for the V4 marker set.
- Classify dialog families before runtime execution.

### Acceptance
- The V4 baseline marker set is observable.
- Unsafe or incomplete dialog candidates fail closed before capture.
- No OS, file, print or external-service dialog is introduced.

### Depends On
- none

### Related
- `openspec/changes/v4-dialog-surface-model/`

### Notes For `$openspec-ff-change`
- Keep this to state/model artifacts and fixture-local marker design.

## Change 2: `v4-bounded-wait-error-scenarios`

### Why
The fixture needs deterministic warning, question, modal, expected-error and
bounded-wait scenarios after the V4 marker model exists.

### Goal
Add controlled scenario handlers with stable markers and bounded lifetime.

### Scope
- Add warning/question/modal scenario handlers.
- Add expected-error handlers with reviewed diagnostic markers.
- Add bounded wait/progress handlers with cancel/retry/completion markers.

### Acceptance
- Every scenario exposes deterministic result markers.
- Expected errors are distinguishable from infrastructure failures.
- Wait scenarios are bounded and resettable.

### Depends On
- `v4-dialog-surface-model`

### Related
- `openspec/changes/v4-bounded-wait-error-scenarios/`

### Notes For `$openspec-ff-change`
- Do not add unbounded waits, background jobs or OS dialogs.

## Change 3: `v4-dialog-recovery-verification`

### Why
V4 scenarios can leave modal, wait or expected-error state behind unless
recovery proof is explicit.

### Goal
Define before/action/result/recovery evidence and reset expectations for every
V4 scenario family.

### Scope
- Define V4 recovery proof sequence.
- Separate dialog/action, background, expected-error and recovery ranges.
- Require rerun or baseline proof after recovery.

### Acceptance
- Failed, cancelled or completed V4 cases return to the baseline or remain
  candidate with documented residual state.
- Expected diagnostic mismatches fail closed.
- No V4 row is promoted without reviewed recovery proof.

### Depends On
- `v4-bounded-wait-error-scenarios`

### Related
- `openspec/changes/v4-dialog-recovery-verification/`

### Notes For `$openspec-ff-change`
- Upstream V2/V3 prerequisites are closed; accepted V4 promotion remains gated
  by V4-specific replay, direct probe or typed contract proof.

## Change 4: `v4-dialog-corpus-manifest-updates`

### Why
Dialog, wait and expected-error evidence needs a fail-closed manifest and
publication contract before captures are reviewed.

### Goal
Define V4 corpus rows and compact evidence publication rules.

### Scope
- Define V4 row fields for scenario family, markers, bounded duration,
  expected result and recovery expectation.
- Keep expected errors separate from infrastructure failures.
- Keep raw captures and replay payloads under ignored runtime paths.

### Acceptance
- Incomplete V4 rows fail closed before capture or publication.
- Compact evidence records markers, ranges, hashes and recovery results.
- Existing V1/V2/V3 corpus output remains scoped away from V4-only fields.

### Depends On
- `v4-dialog-recovery-verification`

### Related
- `openspec/changes/v4-dialog-corpus-manifest-updates/`

### Notes For `$openspec-ff-change`
- Treat manifest validation as permission to review/capture only, not as
  protocol acceptance.

## Log
- 2026-06-04T12:04:00Z card created
- 2026-06-07T00:00:00Z order index updated to 80 after V2 and V3 evidence gates
- 2026-06-07T00:00:00Z refreshed with current V2 proof/tooling dependencies,
  V3 todo state and explicit delivery gate
- 2026-06-07T00:00:00Z fast-forwarded into four OpenSpec changes; card kept in
  `1.backlog` because V4 delivery is gated
- 2026-06-09T00:00:00Z refreshed after V2 runner/proof, V3 surface and V3
  candidate mutation evidence/promotion cards were archived in `4.done`;
  delivery is ready to move to `2.todo`
- 2026-06-09T05:49:15Z moved to `2.todo` with existing V4 OpenSpec artifacts
  reused as the apply-ready change set
- 2026-06-09T18:20:16Z implemented V4 fixture-local dialog/wait/error/recovery
  surface, retained Vanessa fallback runtime proof, synced `qa-mcp-protocol-lab`
  spec, archived all four OpenSpec changes and moved the card to `4.done`
- 2026-06-09T18:20:16Z published V4 docs, compact evidence, synced spec and
  archived OpenSpec state; exact commit hash is available in Git history
