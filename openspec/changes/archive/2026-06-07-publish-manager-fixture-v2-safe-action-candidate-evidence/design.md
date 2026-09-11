## Context

The first focused proof needs a reviewed candidate input set from the manager
V2 runner. This change publishes compact evidence while preserving the rule
that action-frame joins alone do not become accepted protocol knowledge.

## Goals / Non-Goals

**Goals:**

- Publish compact V2 safe-action evidence for the supported manager runner
  subset.
- Preserve statuses such as candidate, accepted, rejected, blocked, partial and
  timeout with explicit reasons.
- Link retained action, background and recovery range summaries.
- Keep raw runtime output outside reviewed git.

**Non-Goals:**

- Running broad demo button pilots.
- Accepting mappings without replay/probe or typed contract proof.
- Publishing V3 mutation or V4 dialog evidence.

## Decisions

- Use the existing V2 reporter and comparison gates where possible instead of
  creating a parallel evidence format.
- Keep candidate evidence valuable even when not accepted. The report should
  state exactly what remains missing.
- Update durable docs only with compact summaries and evidence paths; raw
  captures remain under ignored runtime paths.
- Treat this card as the handoff into the first focused V2 proof card.

## Risks / Trade-offs

- [Risk] Candidate evidence could be mistaken for accepted protocol knowledge.
  [Mitigation] Require explicit status and non-accepted reasons in every
  published row.
- [Risk] Reporter changes can regress earlier V1/V2 outputs.
  [Mitigation] Run focused tests and keep V2-only fields scoped to
  `safe_ui_action`.
- [Risk] Raw runtime output may leak into reviewed docs.
  [Mitigation] Link compact evidence only and keep raw paths ignored.

## Migration Plan

- Publish candidate evidence after runner, boundaries and recovery proof are
  available.
- Update docs/evidence index with compact evidence links.
- Keep the first focused proof card responsible for final accepted/candidate
  proof decision.

## Open Questions

- Should this publication include one selected row only, or all executable
  rows that passed recovery?
- Which direct Python-manager proof path will be feasible for the first
  accepted safe-action row?
