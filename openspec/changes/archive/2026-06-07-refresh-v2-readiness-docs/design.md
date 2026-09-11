## Context

The 2026-06-06 status report records the full manager fixture V1 cleanup story:
an initial cleanup run accepted 8 of 17 joined rows, later focused proofs
accepted six former pending rows through marker-contract evidence, and then
three diagnostic rows through typed manager side-channel contracts. The final
state says V2 safe-action planning is `unblocked_by_v1_readonly`.

The safe-action scope doc was written before that closure and still frames some
V1 fixture-family outcomes as deferred gates. That was correct before the
follow-up proofs. It now needs to distinguish current V1 readiness from future
V2 action proof, without implying that V2 action mappings are already accepted.

## Goals / Non-Goals

Goals:

- Make the current V2 readiness state easy for later cards to cite.
- Preserve the side-channel caveat for diagnostic rows.
- Keep the docs fail-closed: V1 read-only readiness unblocks planning, not V2
  action protocol acceptance.
- Avoid changing any runtime, fixture or capture behavior.

Non-goals:

- Do not run live 1C captures.
- Do not modify the client fixture, manager harness or Python manager.
- Do not promote any safe-action protocol row.
- Do not rewrite historical evidence files; update current summary docs only.

## Decisions

### Current Readiness Wins Over Baseline Counts

The status report may keep baseline counts as historical context, but the
reader-facing readiness statement should use the final follow-up proofs. V2
cards should not have to reconcile older baseline pending rows by hand.

Alternative considered: leave all wording unchanged and rely on the report's
later sections. That makes downstream cards prone to citing stale blockers.

### Side-Channel Proofs Stay Labeled

The three diagnostic rows accepted by typed manager side-channel contracts must
remain visibly different from direct wire marker proof. That caveat matters for
safe-action protocol acceptance because V2 must not infer a direct wire marker
claim from manager-side result previews.

### Scope Doc Separates Prerequisite Closure From Action Acceptance

`safe-ui-action-scope.md` should say V1 read-only no longer blocks V2 planning,
but also that every V2 action still needs its own pre-state, action, post-state,
recovery and replay/direct-probe evidence before acceptance.

## Risks / Trade-offs

- Overstating V1 closure could make V2 look accepted by inheritance. Mitigation:
  keep a direct statement that safe-action mappings remain unaccepted until V2
  evidence exists.
- Understating V1 closure could cause redundant V1 work. Mitigation: cite the
  final accepted evidence paths and readiness label.
- Documentation-only changes can drift from task cards. Mitigation: validate
  OpenSpec and update the downstream card links during `$opsx-do`.

## Migration Plan

No migration is required. During implementation, update current docs in place
and leave raw captures and historical evidence directories unchanged.

## Open Questions

- Whether to create a short `docs/protocol-research/v2-readiness.md` index in
  a later card if downstream V2 work keeps citing multiple evidence paths.
