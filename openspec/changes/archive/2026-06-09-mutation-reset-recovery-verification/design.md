## Context

The mutation state and handler layers make V3 capable of changing local
fixture values. This change defines how we prove the sandbox recovers after a
mutation so the evidence can be trusted and repeated.

## Goals / Non-Goals

**Goals:**

- Define the recovery sequence and reset expectations for V3 mutation cases.
- Keep recovery proof separate from the mutation implementation itself.
- Preserve a clear before/action/post/reset narrative for evidence review.
- Ensure the candidate action frame range is isolated from background traffic.

**Non-Goals:**

- New mutation handlers or new state fields.
- Business workflow recovery, rollback or repost logic.
- Accepting protocol mappings as final evidence without proof review.

## Prerequisite Gate

The V2 safe-action tooling, runner and focused proof prerequisites are already
closed by the related board cards. The remaining promotion boundary is
mutation-specific: this change may review recovery proof and publish candidate
mutation rows, but it must not promote mutation protocol rows as accepted
mappings unless same-action replay, direct Python-manager probe or typed
contract proof supports the row.

## Decisions

- Treat recovery proof as a first-class artifact instead of an informal note.
  Alternatives such as relying on manual inspection were rejected because they
  do not give a repeatable acceptance boundary.
- Capture before/action/post/reset evidence in one sequence and keep
  background/cleanup traffic out of the action range. This makes the result
  easier to review and reduces false positives when the lab refreshes.
- Record recovery expectations even when the outcome is a rejected or partial
  case. That preserves the reason the row is still candidate rather than
  accepted.

## Risks / Trade-offs

- [Risk] Background refresh traffic may blur the action range.
  [Mitigation] Keep candidate-range isolation explicit and review frame ranges
  before promotion.
- [Risk] Reset logic could restore the UI visually but miss a hidden marker.
  [Mitigation] Require the full marker set in the recovery proof and verify it
  after every reset.
- [Risk] A failed mutation may leave unexpected residue.
  [Mitigation] Define the cleanup path alongside the recovery proof and keep
  the scenario isolated to fixture-local state.

## Migration Plan

- Introduce recovery-proof expectations without changing the mutation handler
  interface.
- Validate the reset sequence on the existing V3 baseline once the earlier
  state and handler changes are in place.
- Roll back the change by keeping the old proof boundary if the runtime evidence
  cannot isolate the action frame range reliably.

## Open Questions

- Which exact frame-range summary format should be retained for candidate and
  cleanup traffic in the compact evidence bundle?
- Do we need a separate accepted/rejected label for recovery proofs, or is the
  corpus status inherited from the underlying mutation row?
