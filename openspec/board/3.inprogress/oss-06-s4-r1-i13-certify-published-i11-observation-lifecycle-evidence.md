# Certify Published I11 Observation Lifecycle Evidence

## Status
3.inprogress

## Owner
qa-mcp

## Series
oss-06-s4-r1-i13

## Order Index
405.10196

## OpenSpec Stage
artifacts

## Parent Card
- `openspec/board/2.todo/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`

## Source
- Published I11 commit `964e29fa7ee8ba87df12d0db903ca7a331113c2f`.
- Published I11 final blob lineage in
  `openspec/board/4.done/oss-06-s4-r1-i11-enforce-main-predicate-equivalence-contract.md`.
- Published I12 handoff decision and criterion map.
- Published S5-R1 addressed-action contract:
  `openspec/board/4.done/oss-06-s5-r1-replace-prompt-fingerprint-with-addressed-admission.md`.

## Review
- Risk tier: `critical`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Credential or mutation authority: `yes`
- Live admission: `yes`
- Final certification: `yes`
- Published investigation authorization: `none`
- Published action authority:
  `oss-06-s5-r1-replace-prompt-fingerprint-with-addressed-admission`

## Summary
Certify the unchanged published I11 observation lifecycle with the exact-source
S3/S4/S5 and cleanup evidence still required by S4-R1. This card may retain
evidence but has no product/test implementation authority.

## Acceptance
- Start from a clean branch whose five I11 product/test blobs exactly match the
  published final lineage and whose diff against `964e29f` changes none of
  those paths.
- Pass the exact S3 control, two fresh tracked run-1 S4 rows, one uninstrumented
  S4 confirmation and two run-distinct S5 rows for the required platform
  version without changing source between rows.
- Prove the same tracked fixture and exact argv reach one stable privacy-safe
  marker match in both passive samples on every applicable row.
- Retain row-distinct public-safe evidence for source identity, observation
  outcome, marker hashes and topology; prove zero action for S3/S4 and exactly
  one published addressed S5 confirmation per S5 row, with zero forbidden or
  global input, without raw private UI text, screenshots or broad dumps.
- Restore exact configuration bytes, ACL and all required metadata and remove
  only exact-owned task, stage, process/job/desktop and transport state after
  every row; prove rerun-safe cleanup.
- Treat missing execution access, source drift, missing main, inventory error,
  marker mismatch, topology drift, child failure or incomplete cleanup as
  `BLOCKED` or `NOT-VERIFIABLE`; do not change product/test code in this card.
- Pass focused/full offline regression, deterministic unexecuted cross-builds,
  strict OpenSpec, evidence/manifest scope, public-safety, Apache-2.0 and
  whitespace gates before fresh critical review.
- Keep S4-R1 and downstream work blocked until this card is independently
  reviewed and published.

## Non-Goals
- Modifying the five I11 product/test paths or any other product/test code.
- Adding authority, public or wire surface, retries, fallbacks, waits or any
  action/side effect beyond the two exact S5-R1 certification confirmations.
- Rescuing a failed certification row inside I13; failure requires a separately
  authorized investigation card.
- Resuming S7 or completing the S4-R1 parent.

## Depends On
- `oss-06-s4-r1-i12-decide-post-i11-observation-certification-handoff`

## Blocks
- `oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle`

## Change Set
1. `certify-published-i11-observation-lifecycle-evidence`

## Verify
- Exact source, platform, fixture, argv, configuration before-image and
  uncontended-surface preflight passed.
- S3 passed with zero action and exact double cleanup. The first tracked S4 row
  exited nonzero before an observation receipt; four rows were not started.
- Exact configuration and owned-state cleanup passed, but the protected
  unrelated-task-set fingerprint drifted without being targeted.

## Archive
- not started

## Related
- `docs/protocol-research/evidence/post-i11-observation-certification-handoff-2026-09-02/findings.md`
- `docs/protocol-research/evidence/i15-session1-admission-and-s4-isolation-2026-09-02/findings.md`
- `docs/protocol-research/evidence/i16-stable-profile-omission-after-i15-2026-09-02/findings.md`
- `openspec/changes/certify-published-i11-observation-lifecycle-evidence/`

## Result
`NOT-VERIFIABLE`. I13 stopped fail-closed after S3 passed and the first tracked
S4 row exited before an observation receipt. The six-row matrix is incomplete,
no S4/S5 certification is claimed, and the change remains active/unarchived.
I15 later admitted no new row: its one typed Session-1 canary produced no
receipt and candidate invocation count remained zero.

## Next
- Preserve this `NOT-VERIFIABLE` handoff. I15 used its one separately
  authorized original-route canary, admitted no Session-1 receipt and invoked
  no candidate. No retry is authorized; a separate successor would require
  independently available typed admission and new explicit authority.
- I16 omits `open_external_processor` from stable standalone support but does
  not archive, certify, supersede or authorize continuation of I13.

## Change 1: `certify-published-i11-observation-lifecycle-evidence`

### Why
I11 closes the offline classifier defect, but the parent still requires fresh
exact-source observation and cleanup evidence before it can complete.

### Goal
Certify the unchanged published I11 bytes against the remaining parent matrix
without adding implementation authority.

### Scope
- Exact published I11 product/test blob identity.
- Parent-required S3/S4/S5 rows and stable passive marker evidence.
- Exact restoration, exact-owned cleanup and rerun proof.
- Retained public-safe evidence and fresh critical review.

### Acceptance
- Every row and cleanup assertion passes against unchanged source, or the card
  stops fail-closed without a product/test change.

### Depends On
- none

### Related
- `openspec/changes/certify-published-i11-observation-lifecycle-evidence/`

## Log
- 2026-09-02 prepared by I12 as the exact certification-only successor after
  published I11; no execution or implementation is included in I12.
- 2026-09-02 fast-forwarded one evidence-only certification change with exact
  source, six-row matrix, marker/privacy, cleanup and critical-review gates;
  no certification row was executed during planning.
- 2026-09-02 review-rescue correction classifies I13 as mutation-authority
  critical, binds the published S5-R1 one-addressed-action contract, and
  distinguishes passive zero-action S3/S4 rows from exact one-action S5 rows.
- 2026-09-02 exact-contour preflight passed against unchanged published I11
  bytes. S3 passed with zero action and double cleanup; the first tracked S4
  row exited before a receipt, so all later rows were withheld. Configuration
  and exact-owned cleanup passed, protected unrelated-task topology drifted
  without being targeted, and linked I14 now owns investigation. I13 remains
  unarchived and unpublished.
- 2026-09-02 I15 used its one authorized original-route canary after exact
  preflight; no typed Session-1 receipt arrived, candidate invocation stayed
  zero, and exact cleanup passed. I13 remains unarchived and uncertified.
- 2026-09-02 I16 preserves I13 active, unarchived and uncertified while
  satisfying the separate stable-release gate through tool-profile omission.
