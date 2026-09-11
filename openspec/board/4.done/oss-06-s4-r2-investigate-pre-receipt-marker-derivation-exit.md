# Investigate Pre-Receipt S4 Marker-Derivation Exit

## Status
4.done

## Owner
unassigned

## Series
oss-06-s4-r2

## Order Index
405.103

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

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
Add one bounded, test-only typed diagnostic for the S4-R1 candidate and
determine why the exact passive run-1 marker-derivation row exits nonzero
before a positive receipt, without weakening admission or absorbing the
blocked S4-R1 production payload.

## Acceptance
- Preserve the published base `77a4b389b0ff78649c9b0846d48433cb424e659f`,
  the seven blocked S4-R1 Go paths, the blocked S7 payload and both tracked EPF
  binaries as protected inputs; this card adds no public caller or action.
- Admit a bounded typed failure row only from the implemented argv-identity,
  child-launch or nonzero-exit/checkpoint branches. A missing checkpoint after
  nonzero exit maps to `process_exit/candidate_exited_without_checkpoint`; a
  valid failed checkpoint maps to child launch, listener readiness,
  desktop/window inventory, main admission or passive UIA sampling. Harness
  precondition, setup, receipt freshness/allocation, timeout, checkpoint-read
  or validation, unexpected-zero-exit and unsafe-write failures abort
  fail-closed and are not admitted evidence rows. `diagnostic_setup` has no
  live producer. Do not retain raw UI text, screenshots, credentials or large
  platform logs.
- Keep every existing S3/S4 admission, exact job/desktop/process ownership and
  cleanup invariant fail-closed. A retry, alternate target, visible desktop,
  sentinel value or missing receipt cannot count as success.
- The committed diagnostic surface is test-only, compiles independently from
  the published base, and lives in new card-owned paths. If that boundary is
  insufficient, publish a `NOT-VERIFIABLE`/replacement decision instead of
  editing or committing the seven S4-R1 paths.
- Reproduce the exact S3-pass/S4-pre-receipt-exit classification on the only
  authorized Windows contour, then obtain two deterministic passive diagnostic
  runs that agree on the typed failure stage or record `NOT-VERIFIABLE` with an
  exact resume condition.
- Pass the published-base diagnostic floor and the clean
  `77a4b389`-plus-seven-S4-R1-path composition floor: focused/full Go tests,
  vet, Windows amd64/386 test and host cross-builds, strict OpenSpec and scope
  checks.
- Restore exact configuration bytes/ACL/metadata and remove only exact-owned
  task, stage, PID/job/desktop/TPort state after every run; preserve unrelated
  task and boot fingerprints.
- Publish one evidence-backed outcome: a runbook/environment correction, a
  bounded S4-R1 resume hypothesis with a concrete verification target, or
  `NOT-VERIFIABLE`. Do not resume S4 certification, S7, OSS-07 or OSS-08 inside
  this card.

## Depends On
- Blocked
  `openspec/board/3.inprogress/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`.
- Published S7-I1 investigation and S1-R1 through S6 foundations.

## Change Set
1. `investigate-pre-receipt-s4-marker-derivation-exit`

## Verify
- Portable direct tests for checkpoint-derived stage mapping, the observed
  missing-checkpoint process-exit mapping, hostile validator/checkpoint state
  and privacy-safe serialization passed, with zero production callers. They do
  not claim to execute every live emitting branch or a `diagnostic_setup`
  producer.
- Clean published-base and S4-R1 candidate-composition Go test/vet and Windows
  cross-build floors.
- The operator-approved immutable exact-contour receipt records an exact S3
  pass and two passive S4 rows agreeing on
  `process_exit/candidate_exited_without_checkpoint` with exit code `1`, zero
  action/retry and exact per-row cleanup. The resume performed no live rerun.
- Exact-owned cleanup, protected-path digests, evidence privacy scan, strict
  change/all OpenSpec, manifest scope and `git diff --check`.

## Archive
- `openspec/changes/archive/2026-09-01-investigate-pre-receipt-s4-marker-derivation-exit/`

## Related
- `docs/protocol-research/evidence/pre-receipt-marker-derivation-exit-2026-09-01/findings.md`
- `.runtime/changerail/evidence/oss-06-s4-r2-investigate-pre-receipt-marker-derivation-exit/fresh-matrix.json`
- `.runtime/changerail/evidence/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle/blocker.json`
- `openspec/board/3.inprogress/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`
- `openspec/board/3.inprogress/oss-06-s7-admit-hidden-direct-execute-public-route.md`
- `openspec/board/4.done/oss-06-s7-i1-investigate-hidden-direct-execute-main-window-absence.md`

## Result
Investigation complete with a bounded S4-R1 resume hypothesis. The new
test-only observer compiles independently from `77a4b389`, and the
operator-approved immutable receipt proves that both one-shot passive rows
exit with code `1` before the first checkpoint or listener readiness. Every
row restored configuration bytes, ACL and all four metadata fields exactly;
owned task/stage/process residue is zero and unrelated task/boot fingerprints
are unchanged. This establishes only the observed
`process_exit/candidate_exited_without_checkpoint` boundary; it does not prove
that every harness failure emits a typed row, and fail-closed harness aborts
remain non-evidence. S4-R1 and S7 remain stopped pending a separate
authorization and the concrete first-checkpoint verification target in the
curated decision.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `investigate-pre-receipt-s4-marker-derivation-exit`

### Why
S4-R1 passed its offline clean-composition floor and exact S3 control, but the
first passive run-1 marker-derivation row exited nonzero before any positive
receipt. The retained evidence intentionally contains no raw diagnostics, so a
typed stage is required before another certification attempt can distinguish a
runner/test failure from a child lifecycle, inventory, main-admission or UIA
failure.

### Goal
Publish the smallest privacy-safe diagnostic and an evidence-backed resume or
stop decision without changing S4-R1 production behavior.

### Scope
- One independently publishable test-only diagnostic surface in new paths.
- Ignored sanitized exact-contour receipts and a curated decision report.
- No S4-R1 production edit, marker admission, public route, prompt action,
  Python MCP change or external side effect.

### Acceptance
- The immutable receipt binds the same candidate, fixture hashes and argv and
  records two passive rows at
  `process_exit/candidate_exited_without_checkpoint`; no other live emitting
  branch is claimed as exercised.
- Protected S4-R1/S7/fixture bytes and every cleanup invariant remain exact.
- One fresh independent ordinary-risk review returns `GO` before publication.

### Depends On
- none

### Related
- `openspec/changes/investigate-pre-receipt-s4-marker-derivation-exit/`

## Log
- 2026-09-01 created from the S4-R1 safety stop. The operator authorized a
  separate Codex delivery session and only the bounded passive diagnostic live
  work described here; S4-R1 certification and S5 action remain excluded.
- 2026-09-01 fast-forward planning completed one apply-ready change for a
  clean-base, new-path-only test observer of the protected S4-R1 candidate;
  target substitution, visible proof, retries, S5 and downstream work remain
  excluded.
- 2026-09-01 delivery started after exact base/origin and remote-push preflight
  passed; the protected dirty tree was separated from the three intended
  planning inputs before manifest derivation.
- 2026-09-01 safety stop: clean-base and seven-path offline floors passed, exact
  S3 passed and two passive rows agreed on pre-checkpoint process exit. Exact
  task/stage/process cleanup completed and config bytes/ACL stayed exact, but
  configuration metadata could not be restored from the unavailable pre-run
  timestamp values. Recorded bounded `NOT-VERIFIABLE`; no review or publish.
- 2026-09-01 supervised resume accepted the completed post-timeout receipt as
  immutable unchanged-payload evidence without a live rerun. The receipt proves
  exact configuration content/ACL/all-four-metadata restoration and two
  agreeing pre-checkpoint process exits. Published the bounded first-checkpoint
  S4-R1 resume hypothesis; S4-R1, S7, OSS-07 and OSS-08 remain stopped.
- 2026-09-01 review metadata normalized: this linked investigation stops the
  repeated implementation staircase and adds zero production LOC, authority or
  wire protocol, so it is not itself another repeated-defect implementation.
- 2026-09-01 review cycle 1 returned `NO-GO` because the card, archived
  artifacts and synced spec over-claimed all-stage live emission and hostile
  branch coverage. Same-card rescue attempt 1 narrowed claims only: immutable
  code/evidence stayed unchanged, harness aborts remain fail-closed non-evidence
  and only the observed process-exit rows and exact cleanup are live-proven.
- 2026-09-01 review cycle 2 returned `NO-GO` on three remaining claim-only
  overstatements in the archived proposal and archived/synced scenario.
  Same-card rescue attempt 2 narrowed only those statements to implemented
  argv-identity, child-launch and nonzero-exit checkpoint branches; setup,
  freshness/allocation, timeout, checkpoint-read/validation, unexpected-zero
  and unsafe-write aborts remain fail-closed non-evidence. Immutable code and
  exact-contour evidence stayed byte-identical; no live execution occurred.
- 2026-09-01T11:11:13Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
