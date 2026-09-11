# Stabilize Hidden Direct-Execute Observation Lifecycle

## Status
2.todo

## Owner
qa-mcp

## Series
oss-06-s4-r1

## Order Index
405.102

## OpenSpec Stage
planning

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Credential or mutation authority: `no`
- Live admission: `yes`
- Final certification: `yes`
- Published investigation authorization: `none`

## Summary
Close the S4 observation lifecycle only after the published I11 predicate-
equivalence correction is certified by the exact-source passive observation,
marker and cleanup matrix before S7 resumes.

## Acceptance
- Preserve published S1-R1 through S3 and S5-R1/S6 behavior; modify only the
  minimum S4 observation/lifecycle seam and its tests, with no public caller.
- Hold the hidden desktop and observation thread deterministically across
  controller transfer, both window inventories and both passive UIA samples.
- Keep `EnumDesktopWindows` errors fail-closed; no retry, sentinel or extra job
  assignment becomes production success without an explicit invariant and
  hostile tests.
- Derive and freeze the tracked form marker from privacy-safe passive UIA hash
  evidence, not visual punctuation, OCR, screenshots or raw UI text.
- Pass exact S3, two fresh tracked run-1 S4 runs, one uninstrumented S4
  confirmation and two run-distinct S5 runs on Windows `8.3.27.2214`.
- Restore exact configuration bytes/ACL/metadata and remove only exact-owned
  task, stage, PID/job/desktop/TPort state after every run.
- Leave S7 blocked until this card is independently reviewed and published.

## Depends On
- Published implementation
  `oss-06-s4-r1-i11-enforce-main-predicate-equivalence-contract`.
- Pending certification
  `oss-06-s4-r1-i13-certify-published-i11-observation-lifecycle-evidence`.

## Change Set
1. `enforce-main-predicate-equivalence-contract` (archived and published)
2. `certify-published-i11-observation-lifecycle-evidence` (apply-ready)

## Verify
- Hostile lifecycle/desktop/thread/job transfer and exact marker-hash tests.
- Full Go tests/vet and deterministic Windows cross-builds.
- Exact-source Windows S3/S4/S5 matrix and exact-owned cleanup audit.
- Strict change/all OpenSpec, manifest scope, public scan and `git diff --check`.

## Archive
- `openspec/changes/archive/2026-09-02-enforce-main-predicate-equivalence-contract/`
- certification archive pending I13 delivery

## Related
- `docs/protocol-research/evidence/hidden-direct-execute-main-window-investigation-2026-09-01/findings.md`
- `docs/protocol-research/evidence/post-i11-observation-certification-handoff-2026-09-02/findings.md`
- `docs/protocol-research/evidence/i13-published-i11-certification-attempt-2026-09-02/findings.md`
- `openspec/board/4.done/oss-06-s4-r1-i11-enforce-main-predicate-equivalence-contract.md`
- `openspec/board/3.inprogress/oss-06-s4-r1-i13-certify-published-i11-observation-lifecycle-evidence.md`
- `openspec/board/4.done/oss-06-s4-r1-i14-investigate-i13-s4-early-exit-and-task-topology-drift.md`
- `openspec/board/4.done/oss-06-s4-r1-i15-retry-i13-s4-isolation-after-session1-admission-restoration.md`
- `openspec/board/4.done/oss-06-s4-r1-i16-record-stable-profile-omission-after-i15.md`
- `openspec/board/2.todo/oss-06-s7-admit-hidden-direct-execute-public-route.md`

## Result
Blocked on certification, not implementation. Published I11 commit
`964e29fa7ee8ba87df12d0db903ca7a331113c2f` closes the private predicate-
equivalence defect within five paths and 259 production LOC, preserves the
public/wire surface and passes its complete offline proof floor. I11 explicitly
does not execute the parent's exact-source S3/S4/S5, stable marker or cleanup
matrix, so those criteria remain open and cannot be inferred from offline
evidence.

## Next
- Keep this parent and S7 blocked. I14 ruled out simple inclusion of its
  excluded task but could not distinguish historical harness/start behavior
  from external drift or admit a Session-1 candidate result. I15 then used one
  separately authorized original-route canary, received no typed Session-1
  receipt and invoked no candidate. No retry is authorized; do not treat I13,
  I14 or I15 as certification.
- I16 records `open_external_processor` as omitted from the stable standalone
  profile/public support matrix. This release-scope decision does not complete
  or certify this parent and creates no resume authority.

## Change 1: `enforce-main-predicate-equivalence-contract`

### Why
Rejected I4/I9 attempts proved that a successful absence classification must be
exactly equivalent to both real admission predicates without adding external
calls or changing predecessor behavior.

### Goal
Enforce the complete private exact/absent/invalid predicate-equivalence
contract before any passive marker observation.

### Scope
- Exact five I11 product/test paths and 259 production LOC.
- Complete connected hostile matrix and predecessor call/control invariants.
- Offline Linux tests, vet, repository coverage and deterministic unexecuted
  cross-builds only.

### Acceptance
- Published I11 card, archive and synced enforcement specification retain the
  exact closed contract and complete offline proof floor.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-09-02-enforce-main-predicate-equivalence-contract/`

## Change 2: `certify-published-i11-observation-lifecycle-evidence`

### Why
I11 deliberately excludes the exact-source execution, stable marker and cleanup
evidence required by this parent.

### Goal
Certify the unchanged published I11 bytes against every remaining parent row
without adding implementation authority.

### Scope
- Exact source identity and required S3/S4/S5 rows.
- Stable passive marker hash and topology evidence.
- Exact restoration, exact-owned cleanup and rerun proof.
- Fresh critical independent review.

### Acceptance
- Every row and cleanup assertion passes against unchanged source, or I13 stops
  fail-closed for a separately authorized investigation.

### Depends On
- `enforce-main-predicate-equivalence-contract`

### Related
- `openspec/changes/certify-published-i11-observation-lifecycle-evidence/`

## Log
- 2026-09-01 created by the S7-I1 replacement decision; no production
  correction is included in the investigation payload.
- 2026-09-02 kept blocked after rejected/unpublished I4 and I9 repeated the
  predicate-equivalence invariant. I10 prepares a closed design, a separate
  authorization source and I11; no third I9 rescue or parent implementation is
  authorized.
- 2026-09-02 reconciled published I11: its private correction and offline floor
  are complete, while the exact-source matrix, stable marker and cleanup proof
  remain unavailable in this session. Prepared apply-ready I13 as the exact
  certification-only successor; parent and S7 remain blocked.
- 2026-09-02 I13 exact preflight and S3 passed, then the first tracked S4 row
  exited before an observation receipt and protected unrelated-task topology
  drifted without being targeted. I13 stopped unarchived. I14 ruled out simple
  inclusion of its excluded task, but could not distinguish historical
  harness/start behavior from external drift or admit a candidate receipt;
  its separate investigation remains `NOT-VERIFIABLE`.
- 2026-09-02 I15 exact preflight and cleanup passed, but its one authorized
  original-route canary produced no typed Session-1 receipt and candidate
  invocation remained zero. The parent and S7 remain blocked.
- 2026-09-02 I16 records the explicit stable-profile omission after I15 while
  preserving this parent incomplete and without retry or certification.
