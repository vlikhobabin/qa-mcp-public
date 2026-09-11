# Decide Post-I11 Observation Certification Handoff

## Status
4.done

## Owner
unassigned

## Series
oss-06-s4-r1-i12

## Order Index
405.10195

## OpenSpec Stage
archived

## Parent Card
- `openspec/board/2.todo/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`

## Source
- Published I11 commit `964e29fa7ee8ba87df12d0db903ca7a331113c2f`.
- Published I11 card, archive, synced enforcement specification and curated
  predicate-equivalence decision.
- S4-R1 parent acceptance and the project roadmap at the same published tree.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Summary
Reconcile the S4-R1 parent and project roadmap after published I11, decide
which parent criteria are closed by offline evidence and which still require
separate exact-source certification evidence, and prepare one exact linked
successor without changing product or test code.

## Acceptance
- Prove local `HEAD`, credential-free HTTPS `origin/main` and the tracked I11
  publication identity equal `964e29fa7ee8ba87df12d0db903ca7a331113c2f`.
- Map every S4-R1 parent acceptance criterion to published I11/offline evidence
  or an explicit remaining evidence gap without treating an unexecuted matrix
  as passed.
- Record that I11 closes the private predicate-equivalence implementation
  defect while the parent remains incomplete until its exact-source S3/S4/S5
  and cleanup evidence exists.
- Update the parent and roadmap to remove stale I10/I10a/I11 instructions and
  name one exact linked certification successor before any parent or S7
  continuation.
- Prepare that successor as an apply-ready board/OpenSpec handoff with exact
  source identity, evidence floor, cleanup contract, review requirement and a
  fail-closed stop on unavailable execution evidence.
- Change documentation and OpenSpec workflow only; add no product/test code,
  public API, route, wire field, authority, retry, fallback or side effect.
- Preserve Apache-2.0 and remain Linux offline; deterministic unexecuted
  cross-builds are allowed, but no prohibited execution or external contact is
  part of this decision payload.

## Non-Goals
- Completing S4-R1 from offline evidence or resuming S7.
- Reopening I4/I9 or modifying their immutable evidence workspaces.
- Changing I11 product/test files or widening its published authority.
- Performing the future successor's exact-source execution matrix.

## Depends On
- `oss-06-s4-r1-i11-enforce-main-predicate-equivalence-contract`

## Blocks
- `oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle`

## Change Set
1. `decide-post-i11-observation-certification-handoff`

## Verify
- Local `HEAD`, credential-free HTTPS `origin/main`, repository-local helper,
  I11 card/archive/spec identity and exact published commit `964e29f` passed.
- Decision schema/value and seven-row criterion map, parent/roadmap/I13 graph,
  I13 apply readiness and zero implementation/wire authority checks passed.
- Strict I12 change/capability and all OpenSpec passed pre-archive (`64/64`);
  already-synced archive used `--skip-specs`, and post-archive all OpenSpec
  passed (`63/63`).
- Combined tracked/untracked scope is documentation/OpenSpec-only; product,
  test and `LICENSE` diffs are empty. Public-safety, Apache-2.0, tracked plus
  untracked whitespace and `git diff --check` gates passed.
- Execution and test-first RED evidence are not applicable to this docs-only
  decision; no future I13 certification row was executed.

## Archive
- `openspec/changes/archive/2026-09-02-decide-post-i11-observation-certification-handoff/`

## Related
- `openspec/board/4.done/oss-06-s4-r1-i11-enforce-main-predicate-equivalence-contract.md`
- `openspec/board/2.todo/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`
- `openspec/changes/decide-post-i11-observation-certification-handoff/`

## Result
Published I11 closes the private main-predicate equivalence defect and offline
proof floor but not the parent's exact-source observation, stable marker or
cleanup evidence. The parent and roadmap now remain blocked on one exact
apply-ready certification-only successor, I13, which has no product/test
implementation authority and must stop for a separate investigation on any
unavailable or failing evidence.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-post-i11-observation-certification-handoff`

### Why
Published I11 supplies the corrected private observation predicate and a full
offline proof floor, but its non-goals explicitly exclude the execution matrix
that the S4-R1 parent still requires.

### Goal
Publish a truthful, machine-auditable parent/roadmap reconciliation and an
exact apply-ready certification handoff without claiming unavailable evidence.

### Scope
- Published I11 and current parent/roadmap evidence.
- Per-criterion closure/gap decision.
- Parent and roadmap metadata.
- One exact linked successor and its OpenSpec artifacts.
- Documentation/OpenSpec only.

### Acceptance
- The decision names each closed and remaining criterion, keeps the parent
  blocked, and binds the successor to the published I11 tree.
- No production, test, runtime or external-operation surface changes.

### Depends On
- none

### Related
- `openspec/changes/decide-post-i11-observation-certification-handoff/`

## Log
- 2026-09-02 created from published I11 to reconcile the parent without
  misrepresenting offline evidence as the still-required execution matrix.
- 2026-09-02 fast-forwarded one documentation/OpenSpec-only handoff decision
  with an exact criterion map, certification-only successor contract and
  apply-ready artifacts; no product/test byte or external state changed.
- 2026-09-02 reconciled all seven parent criteria, published the curated and
  machine-readable decision, synchronized parent/roadmap, prepared apply-ready
  I13, synced the handoff capability and archived I12. Strict all OpenSpec
  passed `63/63`; exact graph/scope/public-safety/license/whitespace gates
  passed and no certification row was executed.
- 2026-09-02 independent review cycle 1 returned NO-GO: the S7 card still had
  a directly runnable `Next`, and I13 incorrectly declared zero mutation
  authority/action despite its two published S5-R1 confirmation rows.
- 2026-09-02 same-card rescue attempt 1 bound S7 itself to published I13 and
  parent prerequisites, classified I13 as critical mutation-authority scope,
  bound the published S5-R1 addressed-action contract and made exact action
  counts `0/0/0/0/1/1`; no product/test byte or certification row changed.
- 2026-09-02T04:30:05Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
