# Investigate I13 S4 Early Exit And Task-Topology Drift

## Status
4.done

## Owner
unassigned

## Series
oss-06-s4-r1-i14

## Order Index
405.10197

## OpenSpec Stage
archived

## Parent Card
- `openspec/board/3.inprogress/oss-06-s4-r1-i13-certify-published-i11-observation-lifecycle-evidence.md`

## Source
- I13 exact-source attempt decision and bounded retained evidence.
- Published I11 commit `964e29fa7ee8ba87df12d0db903ca7a331113c2f`.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Credential or mutation authority: `yes`
- Live admission: `yes`
- Final certification: `no`
- Published investigation authorization: `none`

## Summary
Determine why the exact I13 S4 candidate exited before an observation receipt
and why the protected unrelated-task-set fingerprint changed, without changing
product/test code or treating an investigation run as certification.

## Acceptance
- Reconfirm the unchanged five-blob published-I11 lineage and the same exact
  operator-authorized contour; no target, identity, platform, fixture or argv
  substitution is allowed.
- Reproduce or isolate the S4 pre-receipt exit with bounded typed evidence that
  retains no raw UI, screenshots, credentials, connection strings or broad
  dumps.
- Determine whether the task-topology hash change is deterministic harness
  behavior, independent system drift or an actual ownership violation without
  modifying or removing unrelated tasks; if the bounded evidence cannot
  distinguish those causes, retain `NOT-VERIFIABLE` and infer none.
- Publish a decision that classifies the failure as contour, harness or
  published-behavior scope and names any separately authorized successor; do
  not implement a correction in I14.
- Restore and verify only the configuration and exact-owned surfaces for which
  an initial before-image or typed receipt exists; explicitly retain any
  unprovable continuity or zero-state as `NOT-VERIFIABLE`. Remove only
  exact-owned state and prove each executed cleanup rerun is a no-op.

## Non-Goals
- Retrying or completing I13 certification.
- Modifying product/test source, adding instrumentation to published paths or
  widening action/wire/public authority.
- Killing, altering or deleting unrelated processes, tasks or state.

## Depends On
- none; the retained I13 failure attempt is source evidence, not a completion
  dependency

## Blocks
- `oss-06-s4-r1-i13-certify-published-i11-observation-lifecycle-evidence`
- `oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle`

## Change Set
1. `investigate-i13-s4-early-exit-and-task-topology-drift`

## Verify
- Planned exact-source/runtime identity, one-attempt typed investigation,
  protected topology attribution, double-cleanup, privacy, focused/full Go,
  strict OpenSpec, manifest scope and public-surface gates.

## Archive
- `openspec/changes/archive/2026-09-02-investigate-i13-s4-early-exit-and-task-topology-drift/`

## Related
- `docs/protocol-research/evidence/i13-published-i11-certification-attempt-2026-09-02/decision.json`
- `docs/protocol-research/evidence/i13-published-i11-certification-attempt-2026-09-02/findings.md`
- `docs/protocol-research/evidence/i14-i13-s4-early-exit-and-task-topology-investigation-2026-09-02/decision.json`
- `docs/protocol-research/evidence/i14-i13-s4-early-exit-and-task-topology-investigation-2026-09-02/findings.md`
- `openspec/changes/archive/2026-09-02-investigate-i13-s4-early-exit-and-task-topology-drift/`

## Result
`NOT-VERIFIABLE` contour decision retained. The exact EPFs were available, but
the original interactive task route did not admit a typed Session-1 canary, so
I14 accepted no candidate result and performed no retry. Protected task
topology matched the historical before hash throughout an excluded exact-owned
task lifecycle, which rules out simple inclusion of that task but cannot
distinguish historical harness/start behavior from external drift; topology is
therefore `NOT-VERIFIABLE` and no cause is inferred. Exact task, stage, process
and 1C cleanup is proven, but initial configuration last-access continuity and
job/desktop/transport zero-state are not verifiable. I13 remains uncertified
and unarchived.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `investigate-i13-s4-early-exit-and-task-topology-drift`

### Why
I13 reached the exact contour but the first tracked S4 row failed before a
receipt, while protected task topology also changed without being targeted.

### Goal
Produce a bounded decision that identifies the failing boundary and the exact
next authority, if any, without changing published behavior.

### Scope
- Exact-source S4 pre-receipt failure classification.
- Protected unrelated-task topology classification.
- Exact-owned cleanup and privacy-safe evidence.

### Acceptance
- The decision is evidence-backed, retains no private UI or secrets, changes no
  product/test code, and does not claim I13 certification.

### Depends On
- none

### Related
- `docs/protocol-research/evidence/i13-published-i11-certification-attempt-2026-09-02/`

## Log
- 2026-09-02 created as the required separate investigation after I13 stopped
  on its first tracked S4 row and retained protected-task topology drift.
- 2026-09-02 fast-forwarded one investigation-only change with exact contour,
  bounded failure/topology evidence, exact cleanup and critical-review gates;
  no runtime row or product/test change occurred during planning.
- 2026-09-02 exact source, platform, target, candidate and the two immutable
  EPF hashes passed preflight. The interactive task route did not admit a typed
  Session-1 canary within 180 seconds, so no candidate result was accepted and
  no retry occurred. The protected task set matched I13's before hash during
  and after the excluded exact-owned task lifecycle, ruling out simple task
  inclusion but not distinguishing historical harness/start behavior from
  external drift. Exact task/stage/process and 1C cleanup passed; initial
  configuration last-access continuity and job/desktop/transport zero-state
  remain unverified. I14 retained a `NOT-VERIFIABLE` decision without inferring
  a topology cause.
- 2026-09-02 review cycle 1 returned `NO-GO` with two blockers and one major.
  Same-card rescue attempt 1 added the retained seven-entry typed evidence
  index, corrected the credential/mutation risk declaration, withdrew the
  unsupported independent-drift conclusion, and made the three unresolved
  cleanup/topology surfaces explicit before fresh critical/xhigh re-review.
- 2026-09-02 review cycle 2 returned `NO-GO` with one blocker after confirming
  the cycle-1 evidence and risk findings were resolved. Same-card rescue
  attempt 2 corrected the two remaining downstream board summaries that still
  called the unresolved topology delta independent drift; fresh critical/xhigh
  review cycle 3 is the final permitted review, and no fourth cycle is allowed.
- 2026-09-02T08:41:53Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
