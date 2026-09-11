## Context

The catalog defines safe candidates. This change adds the execution layer in
the manager fixture, using the existing TestManager/TestClient route and
keeping V1 read-only behavior intact.

## Goals / Non-Goals

**Goals:**

- Execute only catalog-approved V2 action rows.
- Keep actions non-mutating and local to the client fixture UI.
- Inspect pre-state and post-state around every action.
- Fail closed with clear result markers when a target is unavailable or unsafe.

**Non-Goals:**

- Text input, checkbox/value toggles, business command clicks or writes.
- Dialog/error/retry behavior from V4.
- Replay/probe acceptance or accepted mapping publication.

## Decisions

- Route every action through one dispatcher that checks catalog safety before
  calling an action handler. This avoids one-off handler shortcuts.
- Keep the first runner families aligned with `safe-ui-action-scope.md`.
  Broad clicks are not a V2 action family; inert button behavior belongs to V3
  mutation sandbox unless a row proves it is safe and non-mutating.
- Read pre-state and post-state via manager fixture observations rather than
  trusting the action call result alone. Action result text without state
  proof is candidate-only.
- Preserve V1 read-only command behavior and add V2 commands separately.

## Risks / Trade-offs

- [Risk] UI focus or page switching may be platform-sensitive.
  [Mitigation] Keep rows candidate until live evidence proves the expected
  markers.
- [Risk] A handler may accidentally execute a business command.
  [Mitigation] Keep commands restricted to allowlisted families and reject
  command-click paths.
- [Risk] Runner errors can be confused with action failures.
  [Mitigation] Emit typed failure reasons and keep infrastructure failures
  separate from rejected safe-action rows.

## Migration Plan

- Add V2 runner commands alongside V1 read-only commands.
- Start with the smallest candidate subset for later focused proof.
- Disable V2 execution by validation failure when catalog rows are incomplete.

## Open Questions

- Which manager-side API call gives the most stable focus evidence for the
  first proof?
- Should expand/collapse menu rows wait for a later proof if page/focus rows
  are enough to unblock V2?
