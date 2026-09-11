# Bind TestClient To The Declared Project Runtime Target

## Status
4.done

## Owner
qa-mcp

## Series
oss-04

## Order Index
403

## OpenSpec Stage
coordination complete / bounded successors published

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Problem
qa-mcp can launch and own a TestClient, but project-bound launch configuration
does not carry one immutable target identity through lifecycle, operation
results, evidence and cleanup. The initial complete implementation passed its
runtime and test gates but review preflight measured `1265` added production
LOC, above the ChangeRail limit of `300` and the maximum bounded authorization
ceiling of `500`.

## Goal
Deliver the same target-binding outcome as bounded sequential, independently
reviewed and published payloads without weakening the frozen public contract or
discarding the retained Linux/Windows proof.

## Acceptance
- One immutable target identity is resolved from the frozen project handoff.
- Physical target configuration, credentials and evidence roots remain
  provider-owned, ignored and absent from model-controlled tool input.
- Lifecycle, common operations, artifacts and exact-owned cleanup preserve one
  target/session identity and fail closed before alternate-target side effects.
- Every ordinary child payload remains at or below `300` added production LOC;
  a larger successor requires a separate exact published authorization with a
  ceiling no greater than `500`. Every payload is independently reviewed before
  publication to `main`.
- Final OSS-04F proof reconciles the byte-identical final source with retained
  Linux/Windows lifecycle/read/display/cleanup evidence.

## Child Cards

| Step | Order | Card | Boundary |
| --- | ---: | --- | --- |
| A | 4031 | [Runtime-target contract](../4.done/oss-04a-define-runtime-target-contract.md) | models and schema; done |
| B | 4032 | [Provider profile resolver](../4.done/oss-04b-resolve-provider-target-profile.md) | ignored profile and frozen handoff; done |
| C | 4033 | [Project target composition](../4.done/oss-04c-compose-project-target-readiness.md) | application, readiness and doctor; done |
| D | 4034 | [Operation identity](../2.todo/oss-04d-propagate-target-session-operation-identity.md) | two unpublished exhausted lineages; do not deliver |
| D/R2 | 4034.75 | [Boundary investigation](../4.done/oss-04d-r2-investigate-operation-evidence-sanitization-boundary.md) | typed design and verification matrix; done |
| D/A1 | 4034.78 | [Bounded authorization](../4.done/oss-04d-a1-authorize-bounded-operation-evidence-boundary-payload.md) | exact 500-line/no-authority source; done |
| D/R3 | 4034.8 | [Typed operation boundary](../2.todo/oss-04d-r3-implement-typed-operation-evidence-boundary.md) | unpublished exhausted lineage; do not deliver |
| D/R4/R1 | 4034.855 | [Boundary design replacement](../4.done/oss-04d-r4-r1-replace-exhausted-boundary-investigation.md) | exact userinfo/control matrix and split handoff; done |
| D/A2 | 4034.856 | [Core authorization](../4.done/oss-04d-a2-authorize-core-operation-boundary-replacement.md) | exact R5 source; done |
| D/R5 | 4034.86 | [Core boundary](../2.todo/oss-04d-r5-implement-core-operation-boundary.md) | unpublished exhausted lineage; do not deliver |
| D/R5/R1 | 4034.8651 | [Positive boundary investigation](../2.todo/oss-04d-r5-r1-investigate-exhausted-core-operation-boundary.md) | unpublished exhausted design; do not deliver |
| D/R5/R2 | 4034.8652 | [Mismatch outcome replacement](../4.done/oss-04d-r5-r2-resolve-positive-result-mismatch-outcome.md) | exact positive/artifact design and handoff; done |
| D/A4 | 4034.866 | [Positive core authorization](../4.done/oss-04d-a4-authorize-positive-core-operation-boundary.md) | exact R7 source; done |
| D/R7 | 4034.867 | [Positive core boundary](../4.done/oss-04d-r7-implement-positive-core-operation-boundary.md) | reviewed and published; done |
| D/A5 | 4034.868 | [Positive integration authorization](../4.done/oss-04d-a5-authorize-positive-operation-boundary-integration.md) | reviewed and published; done |
| D/R8 | 4034.869 | [Positive public integration](../4.done/oss-04d-r8-integrate-positive-operation-boundary-public-paths.md) | reviewed and published; done |
| D/A3 | 4034.865 | [Old integration authorization](../2.todo/oss-04d-a3-authorize-operation-boundary-integration.md) | blocked/superseded |
| D/R6 | 4034.87 | [Old public integration](../2.todo/oss-04d-r6-integrate-operation-boundary-public-paths.md) | blocked/superseded |
| E | 4035 | [Lifecycle admission](../2.todo/oss-04e-bind-testclient-lifecycle-admission.md) | unpublished exhausted lineage; do not deliver |
| E/R1 | 4035.1 | [Lifecycle admission replacement](../4.done/oss-04e-r1-replace-exhausted-lifecycle-admission.md) | reviewed and published; done |
| F | 4036 | [Evidence and cleanup](oss-04f-enforce-target-evidence-cleanup.md) | reviewed and published; done |

## Dependencies
- [OSS-01](../4.done/oss-01-establish-qa-mcp-shared-core-boundary.md) is published.
- Frozen `agent-core` target contract commit:
  `9bdefadb2861e6998bd2fa845a19fb3fa75f1fb4`.

## Release Gate
- Mandatory for the stable public standalone runtime.
- Complete. OSS-04A through OSS-04F are published; the OSS-04 side of the
  OSS-06 planning dependency is satisfied.

## Verify
- Each child runs its focused and full non-live floor plus strict OpenSpec and
  ChangeRail preflight/review.
- OSS-04F retains source-bound Linux and Windows native lifecycle proof and
  exact post-cleanup inventory.

## Archive
- Child changes archive within their owning child cards.

## Result
The older oversized checkpoint is preserved in the named stash
`oss04-oversized-review-payload-20260825`; exact recovery of the final OSS-04D
tree is not claimed. Its reviewed findings and required behavior are retained
in the published R2 design.
OSS-04A through OSS-04C are published. OSS-04D, OSS-04D-R1 and OSS-04D-R3
exhausted review rescues without publication. The first R4 design investigation
also exhausted review with one exact public-URL matrix handoff missing.
OSS-04D-R4-R1 recreated A2 → R5 → A3 → R6, but R5 and its R5-R1 design
replacement exhausted review unpublished. R5-R2 recreated the clean
A4 → R7 → A5 → R8 sequence; all four cards are reviewed and
published. OSS-04E exhausted review rescue budget unpublished; OSS-04E-R1 is
the clean linked replacement and is reviewed and published. OSS-04F closed the
remaining schemas, evidence and exact-owned cleanup surfaces with exact-source
Linux and exact-wheel Windows proof, then passed critical review cycle 2.
Immutable runtime-target binding is complete.

## Next
- OSS-06 is planning-ready because OSS-04 is complete and OSS-05 is already
  apply-ready. OSS-05 remains the next implementation card.
- Do not invoke `$chrl-deliver` on this completed coordination card and do not
  start another card without a separate operator command.

## Log
- 2026-08-21 card created from sanitized field-validation evidence.
- 2026-08-24 complete implementation and Linux/Windows evidence passed, but
  deterministic review preflight required investigation at `1265` production
  LOC; no semantic review cycle or publish occurred.
- 2026-08-25 operator authorized a recoverable stash and bounded sequential
  split. Full payload fingerprint `sha256:616beea90d7415bec294450227f29cb3818c8c99bf5974d4ba8a2669afbc48e6`
  is retained under ignored ChangeRail evidence.
- 2026-08-25 OSS-04D-R2 published its reviewed typed boundary design; the next
  sequential child is OSS-04D-A1.
- 2026-08-25 OSS-04D-A1 published the exact bounded authorization source; the
  next sequential child is OSS-04D-R3.
- 2026-08-25 OSS-04A passed independent review cycle 3 with no findings and
  moved to `4.done`; OSS-04B is the next sequential child.
- 2026-08-25 OSS-04B passed independent review cycle 5 with no findings and
  moved to `4.done`; OSS-04C is the next sequential child.
- 2026-08-25 OSS-04C passed independent review cycle 3 with no findings and
  moved to `4.done`; OSS-04D is the next sequential child.
- 2026-08-25 OSS-04D and OSS-04D-R1 each ended cycle 3 `NO-GO` after rescue
  budget `2/2`; OSS-04D-R2 was authorized as the mandatory investigation before
  separate bounded authorization and typed implementation successors.
- 2026-08-25 OSS-04D-R3 and its first R4 design investigation both ended cycle
  3 `NO-GO` at rescue budget `2/2`. Exact payloads are verified named stashes;
  R4-R1 is the mandatory design replacement and next sequential card.
- 2026-08-25 R4-R1 recreated A2 → R5 → A3 → R6 with exact authorization paths,
  300-line runtime caps and the full URL hostile/control matrix, then passed
  review cycle 2 and moved to `4.done`; OSS-04D-A2 is next.
- 2026-08-26 OSS-04D-A2 published the exact R5 authorization with machine
  ceiling `301`, retained R5 cap `300` and no authority/wire expansion;
  OSS-04D-R5 is next.
- 2026-08-26 R5 and R5-R1 each ended cycle 3 `NO-GO` at rescue budget `2/2`;
  exact failed payloads are retained in evidence-only stashes. R5-R2 is the
  current clean design replacement and recreates A4 → R7 → A5 → R8; only R8
  may unblock OSS-04E.
- 2026-08-26 R5-R2 passed review cycle 3 and published; A4 is the current
  metadata-only authorization before R7.
- 2026-08-26 A4 completed its metadata-only authorization payload and exact
  candidate/mismatch proof; it is review-ready, with R7 next after publish.
- 2026-08-26 A4 published and R7 became the current apply-ready bounded core
  implementation; A5 remains blocked until reviewed R7 publishes.
- 2026-08-26 R7 implemented and archived its bounded positive core boundary
  with Linux and exact-source Windows offline evidence; fresh review is current
  and A5 remains blocked until R7 publishes.
- 2026-08-26 R7 passed independent review cycle 3 with no findings and
  published to `4.done`; A5 is the next sequential child.
- 2026-08-26 A5 passed independent review cycle 1 with 4/4 acceptance, no
  findings or unbacked claims, and published to `4.done`; R8 is next.
- 2026-08-26 R8 implemented the bounded public integration with semantic RED,
  735 focused and 1517 full non-live tests at 74.24%, plus final exact-source
  architect-Windows offline proof and exact owned cleanup; archive/review is
  current.
- 2026-08-26 R8 review cycle 1 found four blockers; bounded rescue 1 closes the
  formerly-bound bypass, route snapshot, runner re-read and trusted default
  handler conversion defects. Fresh gates are 748 focused and 1530 full
  non-live at 74.35%; exact-source Windows refresh and cycle 2 are current.
- 2026-08-26 R8 passed independent review cycle 2 with 7/7 acceptance and no
  findings or unbacked claims, then published to `4.done`; OSS-04E is next.
- 2026-08-26 OSS-04E ended review cycle 3 `NO-GO` after rescue budget `2/2`:
  incomplete raw remote `client_target` identity could still be normalized and
  admitted. The failed payload is retained in evidence-only stash
  `oss04e-exhausted-review-payload-20260826`; OSS-04E-R1 is the mandatory clean
  replacement and next sequential card.
- 2026-08-27 OSS-04E-R1 was freshly implemented and review rescue 1 closed
  subordinate numeric-equality admission at `248` production LOC. It
  passed Linux and exact-wheel Windows offline admission/cleanup gates, synced
  and archived its change, and is awaiting independent review.
- 2026-08-27 OSS-04E-R1 passed independent review cycle 2 with all six
  acceptance criteria, no findings or unbacked claims, then published to
  `4.done`; OSS-04F is the next sequential child.
- 2026-08-27 OSS-04F passed independent critical review cycle 2 with `9/9`
  acceptance, zero findings and zero unbacked claims, then published to
  `4.done`. Parent OSS-04 and immutable runtime-target binding are complete;
  OSS-06 is planning-ready while OSS-05 remains the next implementation card.
