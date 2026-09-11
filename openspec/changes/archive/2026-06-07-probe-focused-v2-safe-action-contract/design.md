## Context

The focused run can produce isolated candidate frames, but the main spec already
requires accepted replay, direct Python-manager probe or typed contract proof
before safe-action mappings are promoted. This change is the proof gate for the
first focused row.

## Goals / Non-Goals

**Goals:**

- Attempt the strongest feasible proof route for each focused row.
- Preserve enough compact evidence to reproduce the accepted or candidate
  decision.
- Keep candidate status explicit when proof cannot be completed.
- Avoid raw replay/probe payloads in reviewed git.

**Non-Goals:**

- Adding broad replay infrastructure unrelated to the focused row.
- Accepting rows with frame isolation only.
- Executing mutating UI actions or business commands.
- Requiring every selected row to become accepted in the first proof.

## Decisions

- Prefer direct Python-manager probe or replay when the isolated request shape
  can be exercised safely. Use typed contract validation only when it proves the
  same action semantics without live mutation.
- Treat infeasible proof as a valid outcome when the report keeps the row
  candidate and records the missing evidence.
- Preserve normalized hash and dynamic-field details in compact form. Raw
  request series, generated replay payloads and platform logs remain ignored.
- Do not accept rows whose recovery proof was missing or whose action result
  markers are incomplete.

## Risks / Trade-offs

- [Risk] Replay can require live timing or session state that is not stable.
  [Mitigation] Record the gap and keep the row candidate instead of forcing a
  fragile acceptance.
- [Risk] Typed contract proof can be weaker than replay. [Mitigation] Require it
  to prove the same non-mutating action row and action result markers.
- [Risk] Proof artifacts can leak raw payloads. [Mitigation] publish compact
  summaries only and keep raw payload paths ignored.

## Migration Plan

- Consume isolated candidate rows from
  `isolate-focused-v2-safe-action-frames`.
- Run the feasible proof attempt and retain compact evidence.
- Hand the accepted/candidate decision to
  `publish-focused-v2-safe-action-proof`.

## Open Questions

- Which proof route is feasible first for `switch_page`: replay, direct probe or
  typed contract validation?
- Should a row with accepted typed contract proof but no replay be labeled
  accepted or accepted-with-contract in the publication output?
