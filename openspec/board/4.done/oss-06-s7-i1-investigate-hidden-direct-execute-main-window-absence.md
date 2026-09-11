# Investigate Hidden Direct-Execute Main Window Absence

## Status
4.done

## Owner
unassigned

## Series
oss-06-s7-i1

## Order Index
405.101

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
Investigate why the exact published S4 hidden direct-execute observation does
not see the expected 1C main window for the tracked form-bearing EPFs even
though the same hidden foundation and real S3 TestClient pass and a visible
Windows `/Execute` run opens the form correctly.

## Acceptance
- Preserve published S1-R1 through S6 source/test bytes and the blocked S7
  production payload; this investigation adds no public route or authority.
- Reproduce the exact authorized Windows `8.3.27.2214` failure with the tracked
  `run-1.epf` and distinguish process exit, desktop/window enumeration,
  window-class/ownership, security prompt, `/Execute` loading and form-open
  timing without retaining raw UI or credentials.
- Compare exact S3 and S4 argv, environment, worker/job/desktop identity and
  process/window timelines; every diagnostic is test-only or ignored runtime
  evidence and cannot enter a public production caller.
- Explain the transient `EnumDesktopWindows / ERROR_INVALID_DATA` observation
  and the later stable states without weakening S3/S4 admission invariants or
  treating retries as success.
- Produce one evidence-backed root-cause decision: environment/fixture/runbook
  correction, bounded replacement-card scope, or `NOT-VERIFIABLE` with an exact
  resume condition.
- Prove exact-owned cleanup of task, stage, PID/job/desktop/TPort/config state
  after every diagnostic; unrelated protected task/listener/Docker/boot state
  remains unchanged.
- No S7 review, archive, publication or OSS-07 implementation starts from an
  unresolved investigation result.

## Depends On
- Blocked `openspec/board/3.inprogress/oss-06-s7-admit-hidden-direct-execute-public-route.md`
- Published S3/S4/S6 foundations.

## Change Set
1. `investigate-hidden-direct-execute-main-window-absence`

## Verify
- Exact-source Windows preflight and controlled S3/S4 comparison on the
  authorized target without target substitution.
- Bounded process, job, desktop, top-level window/class/owner and exit timeline
  evidence for tracked `run-1.epf`; a second run confirms the classification.
- Focused diagnostic tests/cross-builds with zero production callers and byte-
  identical published predecessors/S7 payload.
- Exact-owned cleanup inventory, privacy scan, strict change/all OpenSpec,
  untracked whitespace and `git diff --check`.

## Archive
- `openspec/changes/archive/2026-09-01-investigate-hidden-direct-execute-main-window-absence/`

## Related
- `openspec/changes/archive/2026-09-01-investigate-hidden-direct-execute-main-window-absence/`
- `docs/protocol-research/evidence/hidden-direct-execute-main-window-investigation-2026-09-01/findings.md`
- `openspec/board/2.todo/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`
- `openspec/board/3.inprogress/oss-06-s7-admit-hidden-direct-execute-public-route.md`

## Result
The retained evidence does not establish a positive hidden-main or passive-UIA
admission. It records an exact baseline S3 exit of zero, S4
`main_not_ready`/`window_inventory_failed` failures, and later bounded receipts
that reach listener readiness with seven job-owned windows before
`0xC0000005` exit without main admission. These variable pre-admission outcomes
do not identify a sole root cause or rule out absent-main/early-exit behavior.
The decision is a bounded S4-R1 replacement to stabilize and structurally
recertify the worker/job/desktop observation boundary before deriving the
privacy-safe marker hash. S7 remains blocked.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `investigate-hidden-direct-execute-main-window-absence`

### Why
S7 cannot edit certified S1-S6 files, and repeated exact-source runs localize
the blocker to the published S4 observation/lifecycle boundary rather than a
missing form or an immediate 1C process exit.

### Goal
Publish a privacy-safe, exact-source root-cause decision and the smallest safe
continuation boundary without changing production behavior.

### Scope
- Test-only/ignored diagnostic instrumentation and repeated exact Windows runs.
- S3 versus S4 process/desktop/window timeline comparison.
- Root-cause decision, successor scope and cleanup evidence.
- No production implementation, public capability, prompt action or S7 review.

### Acceptance
- The causal boundary is supported by repeated exact-source evidence rather
  than inferred from process exit or missing-window status alone.
- Published predecessor and blocked S7 production bytes remain unchanged.
- One fresh independent high-risk review returns `GO` before publication.

### Depends On
- Published S3/S4/S6 and blocked S7 diagnostic evidence.

### Related
- `openspec/changes/investigate-hidden-direct-execute-main-window-absence/`

## Log
- 2026-09-01 created after S7 fixture repair and visible proof did not unblock
  hidden certification. Exact diagnostics prove synthetic lifecycle and real
  S3 PASS, while S4 advances from transient `ERROR_INVALID_DATA` to stable
  `main_not_ready`; S7 cannot alter published S4 within its authorization.
- 2026-09-01 ChangeRail delivery started after artifacts and strict all-change
  validation passed; exact authorized Windows diagnostic evidence is required.
- 2026-09-01 exact S5 security-config hold/restore reproduced on the authorized
  target. Retained S4 rows show status-unspecified, `main_not_ready`,
  `window_inventory_failed` and pre-admission `0xC0000005` exit outcomes; no
  retained receipt proves hidden main/UIA admission. Exact-owned cleanup
  restored config bytes/ACL/metadata and preserved protected resources.
- 2026-09-01 decision: publish no production fix; queue bounded S4-R1 lifecycle
  and marker-hash recertification before S7 resumes.
- 2026-09-01 corrected historical-user-only receipt matrix added `0xC0000005` as another
  exact lifecycle outcome; it reinforces variability and does not replace the
  bounded S4-R1 decision.
- 2026-09-01 same-card rescue attempt 1 after review cycle 1 NO-GO restored
  evidence provenance, narrowed every positive admission claim to retained
  receipt bounds and strengthened structural `main_admitted` validation.
- 2026-09-01 the R3 hostile test mutates the validator's receipt input at the
  behavior source. Missing class, wrong owner, dead/out-of-job child, absent
  listener readiness, wrong stage and zero window count were RED under the old
  boolean-only predicate and are GREEN only with the structural binding, so a
  regression that removes that binding fails the focused test.
- 2026-09-01 rescue verification passed focused/full Go tests, Go vet, offline
  Windows cross-build, strict investigation/all OpenSpec (53 items), exact
  predecessor/S7 byte identity, final evidence/manifest validation, scope,
  tracked/untracked whitespace and `git diff --check`.
- 2026-09-01T08:04:40Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
