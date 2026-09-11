# Decide Hidden Direct-Execute Observation Liveness Boundary

## Status
4.done

## Owner
unassigned

## Series
oss-06-s4-r1-i2

## Order Index
405.1016

## OpenSpec Stage
archived

## Parent Card
- `openspec/board/3.inprogress/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`

## Summary
Use only retained privacy-safe evidence and offline source analysis to decide
the exact child, listener, window and inventory liveness boundary behind the
repeated pre-receipt S4 refusal, then authorize no more than one bounded
correction for a later separate S4-R1 delivery session.

## Source Lineage
- Blocked source card:
  `openspec/board/3.inprogress/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`.
- Latest safe published reference:
  `b25e30c1b42706c37804ea237c9d5186355b665e` (including published S4-R2
  baseline `ceb5778ed5a9a48006443b3cd6a2d7598f7fc60b`).
- Repeated blocker: the exact same-candidate retained row stopped at
  `first_window_inventory/first_window_inventory_failed`; the subsequent
  disposable no-1C probe reproduced `EnumDesktopWindows /
  ERROR_INVALID_DATA` and falsified current-hidden-desktop-handle reuse as a
  sufficient correction.
- Retained evidence:
  `.runtime/changerail/evidence/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle/live-confirmation-20260901t1825z/admission-bundle.json`
  and
  `.runtime/changerail/evidence/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle/retry-blocker-20260901t155633z.json`.

## Acceptance
- Remain completely offline: do not run or connect to 1C, do not access the
  real configuration, do not perform a new real-contour admission, and do not
  create or invoke a Windows task, stage, process, desktop or listener.
- Preserve the blocked S4-R1 implementation payload and every foreign S7,
  OSS-07 and OSS-08 path byte-for-byte; publish only this card's documentation,
  OpenSpec artifacts, synced specification and board move.
- Define mutually exclusive, privacy-safe observation states for exact child
  liveness, exact listener liveness, main-window presence, and successful
  non-empty, successful empty, or errored window inventory. A reported PID is
  not proof of current liveness, and an inventory error is not an empty
  inventory.
- Bind each state to an offline-observable predicate and fail-closed transition
  rule. No retry, sentinel, current-desktop-handle reuse, target substitution,
  extra job assignment or inferred success may erase an empty/error boundary.
- Publish exactly one bounded later-session correction authorization, or none:
  the authorized correction must stay inside the existing S4 observation seam,
  name one verification target, and preserve zero action, privacy and cleanup.
- State that this decision performs no S4-R1 implementation and grants no live
  confirmation authority; any later real-contour confirmation requires a new
  explicit operator resume and the source card's complete offline/session-0
  gates.
- Pass strict change/all OpenSpec validation, documentation privacy/scope
  checks, manifest reconciliation and `git diff --check`, followed by a fresh
  independent review before scoped publication.

## Change Set
1. `decide-hidden-direct-execute-observation-liveness-boundary`

## Verify
- Offline source inspection proved historical listener readiness was PID
  presence rather than current liveness and that successful empty inventory is
  distinct from `EnumDesktopWindows` failure; no executable runtime probe ran.
- The decision covers exclusive child/listener live, exited and unknown;
  inventory error, empty and non-empty; main absent/present; and post-fence
  lifecycle-change states.
- The exact 61 protected blocked S4-R1 and foreign S7/OSS-07/OSS-08 paths
  matched the immutable tree `7513f0fdf059c3c4d0890e13d538b3433b7a19c6`
  recorded by independent review cycle 1 before and after this bounded rescue.
  No unavailable delivery-start digest or historical before/after-delivery
  comparison is claimed.
- Current strict all-OpenSpec validation (57 items), indexed focused privacy,
  untracked-aware scoped-tree whitespace, manifest scope and `git diff --check`
  passed. The archived change's unavailable pre-archive strict-change output
  and the absent public-surface scanner are not claimed.

## Archive
- `openspec/changes/archive/2026-09-01-decide-hidden-direct-execute-observation-liveness-boundary/`

## Related
- `openspec/changes/archive/2026-09-01-decide-hidden-direct-execute-observation-liveness-boundary/`
- `docs/protocol-research/evidence/hidden-direct-execute-observation-liveness-decision-2026-09-01/findings.md`
- `openspec/board/3.inprogress/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`
- `openspec/board/3.inprogress/oss-06-s7-admit-hidden-direct-execute-public-route.md`

## Result
Retained evidence proves an inventory error but does not prove child or
listener liveness at the failing call or one API-level cause. The published
decision keeps error distinct from successful empty inventory and authorizes
exactly one later correction: a pre/post exact child-and-listener liveness
fence around one enumeration call at each existing S4 inventory boundary. It
adds no retry, fallback, job assignment, public caller, live authority or
second rescue. No 1C/runtime surface or blocked/foreign payload was touched.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `decide-hidden-direct-execute-observation-liveness-boundary`

### Why
The retained refusal proves only that the first inventory boundary failed. It
does not say whether the exact child or listener was alive at that instant,
and the existing timeline treated a non-zero listener PID as readiness rather
than proving current listener liveness.

### Goal
Publish one offline, evidence-bounded liveness state model and no more than one
later S4-R1 correction authorization without modifying the blocked payload.

### Scope
- Retained privacy-safe evidence and offline Go-source analysis.
- Documentation and an OpenSpec capability decision only.
- No production/test code, runtime harness, real target, 1C process or S7
  route.

### Acceptance
- Every child/listener/window/empty/error combination has one fail-closed
  classification or is explicitly invalid/unknown.
- The sole authorized correction has one exact seam and verification target;
  failure of that correction does not authorize a second rescue.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-09-01-decide-hidden-direct-execute-observation-liveness-boundary/`

## Log
- 2026-09-01 materialized as the mandatory offline investigation/design
  successor after the repeated first-inventory blocker; no implementation or
  live authority is included.
- 2026-09-01 fast-forwarded one documentation/OpenSpec-only decision change;
  its apply-ready artifacts authorize only one later liveness-fenced sample
  correction and no runtime execution.
- 2026-09-01 offline delivery published the exclusive liveness decision,
  synced its new capability and archived the change. All 57 OpenSpec items and
  current scoped verification checks passed; no 1C, SSH, Windows task, real
  configuration or new admission was used. Historical delivery-start digest
  and pre-archive strict-change output are not claimed.
- 2026-09-01 review-cycle-1 R1/R2 rescue retained indexed focused privacy and
  untracked-aware scoped-tree checks, and proved the exact 61 protected paths
  unchanged against cycle 1's immutable reviewed tree. The liveness decision,
  correction ceiling and all blocked/foreign payload remained unchanged.
- 2026-09-01T16:54:09Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
