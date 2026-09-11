## Context

V3 mutation scenarios are only useful if their rows can be validated and
published in a consistent format. The manifest and evidence contract need to be
clear before capture so the lab does not invent ad hoc row shapes later.

## Goals / Non-Goals

**Goals:**

- Define a compact manifest shape for V3 mutation rows.
- Keep validation fail-closed when required fields are missing.
- Tie reviewed evidence to compact bundle paths instead of raw payloads.
- Preserve a clean handoff from proof creation to evidence publication.

**Non-Goals:**

- New mutation handlers or new fixture state fields.
- Replay engine implementation details.
- Changing how raw runtime traffic is captured outside reviewed evidence.

## Prerequisite Gate

The V2 safe-action tooling, runner and focused proof prerequisites are already
closed by the related board cards. The V3 manifest can now define and publish
candidate mutation rows, but accepted status remains gated by mutation-specific
same-action replay, direct Python-manager probe or typed contract proof.

## Decisions

- Place manifest validation in front of evidence publication rather than after
  the fact. That avoids reviewing rows that can never be promoted.
- Keep `target_marker`, `mutation_family` and `mutates_business_data=false`
  mandatory for every V3 row. A row without those declarations is not a
  mutation sandbox row.
- Treat the evidence index as a compact publication surface and not as a dump
  of raw traffic. Alternatives that expose raw captures were rejected because
  they make review harder and broaden the artifact surface unnecessarily.

## Risks / Trade-offs

- [Risk] The manifest schema could drift from the runtime row shape.
  [Mitigation] Keep the schema and evidence index updated together and review
  them in the same change.
- [Risk] Fail-closed validation may reject a row that is almost complete.
  [Mitigation] Require explicit recovery expectations and status markers so the
  rejection reason stays reviewable.
- [Risk] Evidence publication may become too verbose.
  [Mitigation] Keep only compact reviewed links and summary fields in git; raw
  captures stay in ignored runtime paths.

## Migration Plan

- Introduce the manifest fields and evidence-link conventions in the planning
  artifacts first.
- Validate future V3 rows against the new fail-closed shape before capture or
  corpus promotion.
- Roll back by keeping the previous evidence contract if the new manifest
  shape cannot be enforced consistently across the tooling pipeline.

## Open Questions

- Should `expected_action_result_markers` be mandatory for every mutation row
  or only for rows that are expected to be promoted?
- Do we need a separate status taxonomy for raw capture review versus compact
  evidence publication, or can the existing candidate/accepted labels cover
  both?
