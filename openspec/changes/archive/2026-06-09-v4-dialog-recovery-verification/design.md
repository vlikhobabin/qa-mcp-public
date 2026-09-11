## Context

Dialog, expected-error and bounded-wait scenarios can leave the UI in a
non-baseline state. V2 and V3 already require before/action/post/recovery
evidence; V4 extends that discipline to modal lifecycles, expected failures
and wait cancellation or retry paths.

## Goals / Non-Goals

**Goals:**

- Define a before/open-or-action/result/recovery/recovery-read sequence for
  every V4 scenario family.
- Prove that failed or cancelled V4 scenarios return to the baseline without
  restoring the infobase.
- Keep expected errors separate from infrastructure failures.
- Preserve compact reviewed evidence and keep raw traffic under ignored
  runtime paths.

**Non-Goals:**

- Implementing new scenario handlers.
- Business rollback, reposting or cleanup of application data.
- Promoting protocol mappings without replay/probe or typed contract evidence.

## Prerequisite Gate

The manager fixture V2 safe-action runner, first focused V2 proof, V3 mutation
sandbox surface and V3 candidate-only mutation evidence/promotion prerequisites
are already closed by the related board cards. This change may now verify V4
fixture-local recovery behavior and publish candidate rows, but it must not
promote V4 capture rows as accepted protocol mappings unless V4-specific
replay, direct Python-manager probe or typed contract proof supports the row.

## Decisions

- Treat recovery as part of every V4 scenario row, not as an optional cleanup
  note. This keeps rows fail-closed when reset cannot be proved.
- Add expected-error classification to the recovery proof. An expected error
  must carry the reviewed diagnostic marker; otherwise it is an infrastructure
  failure, rejected row or blocker.
- Keep recovery frame ranges separate from dialog/action and background ranges
  so reviewers can tell what triggered the UI behavior and what cleaned it up.
- Require rerun proof after reset for the first accepted V4 families. A single
  successful reset can hide state leakage that only appears on the next run.

## Risks / Trade-offs

- [Risk] Modal focus or wait progress can produce ambiguous frame boundaries.
  [Mitigation] Require phase events and keep candidate rows unaccepted until
  the boundary is reviewed.
- [Risk] Recovery may succeed visually but leave hidden markers stale.
  [Mitigation] Read the full V4 marker set after recovery and rerun at least
  one case.
- [Risk] Expected-error handling can normalize real infrastructure failures.
  [Mitigation] Require explicit diagnostic markers and classify mismatches as
  non-accepted.

## Migration Plan

- Introduce recovery proof expectations after V4 handlers exist.
- Publish compact evidence only after each scenario family has before/result
  and recovery reads.
- Roll back by keeping V4 rows in candidate or blocked status until proof is
  available.

## Open Questions

- Should V4 recovery use the same reporter status labels as V2/V3, or add a
  distinct `expected_error` accepted subtype?
- How many repeated runs are enough for the first modal and wait recovery
  proof before evidence can be considered stable?
