## Context

Card 60 established that real demo buttons can be blocked or routed rather than
treated as V2 safe-action proof. Card 61 deliberately opens a separate real-
demo mutation layer, but the first step remains read-only: identify a tiny set
of candidate rows that are worth manifest review.

## Goals / Non-Goals

**Goals:**

- Identify a primary document-form mutation candidate and up to two low-blast-
  radius catalog or processing candidates.
- Preserve selected, rejected and deferred candidates with evidence route and
  residual risk.
- Give the manifest-contract change concrete targets without executing them.

**Non-Goals:**

- Clicking the selected controls.
- Creating, changing or deleting demo10413 data.
- Proving frame ranges, replay status or accepted protocol mappings.
- Treating target selection as evidence that an action is safe or recoverable.

## Decisions

- Prefer targets with visible form context, stable element paths and simple
  recovery options. The pilot can be blocked if no such target is available.
- Keep the first row set intentionally small. One complete recoverable row is
  more valuable than several weak candidates.
- Record the evidence route for every candidate so `$opsx-do` can decide
  whether live UI evidence, metadata/EDT facts or existing compact evidence is
  sufficient for manifest review.
- Preserve rejected and deferred targets instead of omitting them, because
  hidden rejection reasons are a common source of unsafe follow-up clicks.

## Risks / Trade-offs

- [Risk] A target selected from static metadata may be hidden or disabled at
  runtime. Mitigation: mark evidence route and require a runtime pre-state
  recheck before any guarded execution.
- [Risk] A low-risk-looking action can still mutate data broadly. Mitigation:
  this change selects candidates only; the manifest contract must prove
  recovery before execution.
- [Risk] Demo10413 data varies between local infobases. Mitigation: the
  selection summary records lab paths, platform version and observed markers
  when runtime evidence is available.

## Migration Plan

- Review the previous demo-button target and real demo forms through read-only
  evidence.
- Write the target-selection summary with selected, rejected and deferred rows.
- Hand the first row set to `define-demo-mutation-manifest-contract`.

## Open Questions

- Which document-form target from card 60 is still visible and recoverable in
  the local `vanessa_client` infobase?
- Which catalog or processing form can provide a low-blast-radius row without
  relying on save/post/delete/fill/import/export behavior?
