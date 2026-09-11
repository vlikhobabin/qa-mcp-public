## Context

The fixture state model and handlers must be discoverable before downstream
capture and runner work can use them. This change publishes the reviewed
target-map and manifest notes that point at those safe-action surfaces.

## Goals / Non-Goals

**Goals:**

- Publish the V2 safe-action target rows in compact docs.
- Link each target row to the local marker set and reset hook.
- Keep excluded controls out of the safe-action manifest.
- Preserve compact evidence references instead of raw runtime payloads.

**Non-Goals:**

- New fixture handlers or state semantics.
- Manager runner execution.
- Live capture or replay work.

## Decisions

- Keep the publication step documentation-first. The target map should explain
  the fixture surface and the evidence path, but it should not claim accepted
  protocol behavior on its own.
- Reuse the existing protocol-research evidence index pattern so the new
  target rows stay compact and easy to cross-reference.
- Treat excluded controls as explicit non-targets rather than incomplete rows.
  That keeps the safe-action boundary fail-closed.

## Risks / Trade-offs

- [Risk] Published target rows may drift from the fixture implementation.
  [Mitigation] Keep the rows linked to the same marker names and evidence path
  conventions used by the fixture changes.
- [Risk] Readers may confuse publication with acceptance.
  [Mitigation] State clearly that the target map is reviewed documentation, not
  replay or probe proof.
- [Risk] Evidence links may become stale if the retained bundle layout changes.
  [Mitigation] Keep the bundle path convention stable and verify it during
  publish checks.
