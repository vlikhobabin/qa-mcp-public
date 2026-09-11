## Context

ChangeRail accepts a production exception above `300` only from a clean tracked
authorization source in `4.done`. That source must bind one published
investigation and one exact successor, and its ceiling cannot exceed `500`.

## Goals / Non-Goals

**Goals:**

- Publish the exact authorization consumed by final successor S7.
- Permit its declared backward-compatible capability within `500` LOC.
- Leave every other card under ordinary fail-closed rules.

**Non-Goals:**

- Authorize the combined `1982`-line candidate.
- Change the global ChangeRail ceiling or waive deterministic preflight.
- Implement, run or admit the external-processor route.

## Decisions

### Use the canonical inline JSON contract

The card declares exactly the six authorization source fields required by
ChangeRail. Paths and ids are canonical and immutable after publication.

### Limit the exception to final integration

Only S7 receives `production_loc_ceiling: 500` and
`allow_new_authority_or_wire_protocol: true`. S1-S6 remain independently
reviewed at `<=300` and cannot reference this authorization.

### Require a published investigation first

Delivery waits until OSS-06-I2 is a clean tracked `4.done` card. No prose or
operator approval substitutes for that machine-checkable relation.

## Risks / Trade-offs

- [Reference becomes stale after lane moves] -> Use the final canonical
  `4.done` investigation path and validate exact relations before review.
- [Authorization is treated as runtime authority] -> State that it changes no
  product source, API, profile or host state.
- [S7 grows beyond 500] -> Deterministic preflight blocks review; split or
  simplify instead of raising the ceiling.

## Migration Plan

Publish only after OSS-06-I2. S1-S6 may then deliver sequentially; S7 consumes
this authorization only after all foundations are published. Rollback before
publication removes the docs-only authorization. After publication, supersede
it with a separately reviewed source rather than editing history.

## Open Questions

- None; all path, id, ceiling and protocol allowance values are fixed.
