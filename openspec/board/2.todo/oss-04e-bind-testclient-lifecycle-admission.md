# Bind TestClient Lifecycle Admission

## Status
2.todo

## Owner
qa-mcp

## Series
oss-04e

## Order Index
4035

## OpenSpec Stage
blocked / exhausted review

## Parent Epic
- `openspec/board/4.done/oss-04-bind-testclient-to-declared-project-runtime-target.md`

## Replaced By
- `openspec/board/4.done/oss-04e-r1-replace-exhausted-lifecycle-admission.md`

## Source Lineage
- Latest safe published baseline:
  `0bc7f45d18b6ded8fe8f0720bd16357b49b8ced9`.
- Final reviewed tree `a28c892287e08ada62f2e3140cd0eb7a466a03e1`
  and fingerprint
  `sha256:566e0aef72e77b6670bbdc8517b891f2671209bec9843b1dc4f11cadb95e15ab`.
- Evidence-only stash `oss04e-exhausted-review-payload-20260826`, stash commit
  `9f68d9e2f8e7ba31d00b4ef03d4654fdf2a84a5b`; it MUST NOT be restored or
  published wholesale.
- Review cycles `1–3`; same-card rescue budget `2/2`, remaining `0`, exhausted
  `true`.

## Goal
Bind project-mode launch, attach and status to the resolved target and create an
immutable session only after non-mutating admission succeeds.

## Acceptance
- Project launch/attach ignore legacy fallback and use only the provider profile.
- Target overrides and unavailable or mismatched targets return typed blocked
  outcomes before Apache, Xvfb, platform, host-agent or protocol side effects.
- Attachment state contains target, session, generation, ownership and lifecycle
  identity without exposing connection material.
- Unbound standalone lifecycle schemas and behavior remain compatible.
- The payload stays at or below `300` added production LOC.

## Change Set
none; the published apply-ready artifacts are reassigned to OSS-04E-R1. The
failed implementation is retained only in the named evidence stash.

## Dependencies
- `oss-04d-r8-integrate-positive-operation-boundary-public-paths` must publish
  after R5-R2 → A4 → R7 → A5 before this card starts. Superseded R6 cannot
  satisfy this dependency.

## Verify
- Canonical ignored verdict/history and exact evidence-only stash lineage.
- Final attempted payload passed `19` target-bound, `400` focused and `1549`
  full non-live tests at `74.49%`, plus exact-wheel Windows proof and cleanup,
  but cycle 3 still found one fail-closed blocker.

## Result
Review cycle 3 returned `NO-GO`: project-bound remote launch still accepted a
`client_target` with absent/zero raw port or an `id` alias without an explicit
`lifecycle_id`, normalized the incomplete observation and created a session.
The payload is not publishable and the same-card rescue budget is exhausted.

## Next
- Do not deliver this card or restore its stash wholesale.
- OSS-04E-R1 is implemented/archived and awaiting independent review.

## Log
- 2026-08-25 created by the OSS-04 complexity investigation as payload E.
- 2026-08-25 dependency redirected to the only typed OSS-04D-R3 runtime
  successor after OSS-04D and OSS-04D-R1 exhausted review rescue budgets.
- 2026-08-25 dependency redirected from exhausted R3/R4 lineages to the R4-R1
  design replacement and its future final integration successor.
- 2026-08-25 dependency finalized on R6, the only public-integration successor
  created by the R4-R1 replacement.
- 2026-08-26 dependency redirected from exhausted R5/A3/R6 and R5-R1 to R8,
  the only public integration successor authorized by R5-R2.
- 2026-08-26 implementation, archive and Linux/Windows verification completed;
  review cycles 1 and 2 returned remote-admission blockers and consumed two
  bounded same-card rescues.
- 2026-08-26 review cycle 3 returned `NO-GO` on incomplete raw
  `client_target` identity. Rescue budget `2/2` is exhausted; the exact failed
  payload was preserved in `oss04e-exhausted-review-payload-20260826` and R1
  is the only continuation.
