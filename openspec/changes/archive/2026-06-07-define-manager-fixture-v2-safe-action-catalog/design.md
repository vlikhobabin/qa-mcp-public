## Context

Client fixture V2 and the V2 tooling pipeline are archived. The missing piece
is the manager-side allowlist that tells the harness which fixture actions may
be attempted and which safety/recovery facts must be present before execution.

## Goals / Non-Goals

**Goals:**

- Define the catalog row shape consumed by the manager V2 runner.
- Keep row validation fail-closed and aligned with the V2 manifest contract.
- Link each action row to client fixture target markers and expected result
  markers.
- Preserve unsupported and blocked rows explicitly instead of dropping them.

**Non-Goals:**

- Executing actions or producing live frame ranges.
- Accepting protocol mappings.
- Adding V3 mutation families or V4 dialog/recovery behavior.

## Decisions

- Use a reviewed catalog row with the same safety fields as the V2 tooling
  manifest. Reusing the row contract prevents the manager harness from
  widening the safety boundary.
- Record allowed family and concrete action separately. The family enforces the
  safety class; the concrete action describes the exact manager runner step.
- Keep unsupported rows visible with reason, owner and residual risk. That
  preserves target coverage gaps without accidentally attempting unsafe UI
  behavior.
- Treat row validation as permission to execute a candidate action only, not as
  protocol acceptance.

## Risks / Trade-offs

- [Risk] Catalog rows can drift from the client fixture target map.
  [Mitigation] Require target ids and `PF_*` markers from reviewed fixture
  target evidence.
- [Risk] A valid-looking row could still point at a business command.
  [Mitigation] Require allowlisted action family and fail closed on excluded
  action families.
- [Risk] Unsupported rows may block early proof selection.
  [Mitigation] Keep rows explicit and let the focused proof select the narrow
  supported subset.

## Migration Plan

- Introduce the catalog before runner execution.
- Validate rows offline before any live capture.
- Keep existing V1 read-only harness behavior unchanged.

## Open Questions

- Should the first live catalog select only `switch_fixture_page` and
  `focus_existing_element`, or also include active-window/form activation?
- Should catalog rows live with manager harness generation or with protocol
  evidence manifests?
