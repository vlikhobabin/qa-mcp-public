## Context

V1 established a stable client fixture shell and read-only markers, but V2
needs a local state model that can be observed, reset and correlated with safe
actions. The new state must stay fixture-local so the action surface remains
non-mutating and recoverable.

## Goals / Non-Goals

**Goals:**

- Define a single local state record for the V2 fixture.
- Make marker updates deterministic for focus, page, row and action changes.
- Ensure reset returns the form to the V1 baseline after each safe action.
- Keep the state model isolated from business data and external services.

**Non-Goals:**

- Business object writes, posting, deletion or data exchange.
- Manager-side runner changes.
- Dialog or recovery semantics beyond the fixture reset hook.

## Decisions

- Store the V2 safe-action state inside the form module rather than in an
  external file or runtime service. This keeps the state observable with the
  fixture and avoids a second persistence layer.
- Update all `PF_*` markers through a small shared helper instead of scattering
  assignments across handlers. That reduces drift and keeps the reset path
  consistent.
- Treat `PF_ACTION_COUNTER` as a local monotonic counter for successful
  fixture-local actions only. This gives downstream evidence a stable order
  signal without implying business-side progress.
- Implement reset as a shared routine that restores the baseline state object
  instead of clearing fields ad hoc. That makes the baseline reproducible after
  every safe action.

## Risks / Trade-offs

- [Risk] Marker drift if one handler bypasses the shared helper.
  [Mitigation] Route all state changes through the same update routine and
  verify the reset path with a full local baseline check.
- [Risk] Hidden coupling between state markers and form initialization.
  [Mitigation] Keep the baseline state definition in one place and exercise it
  during startup and reset verification.
- [Risk] Recovery evidence may still depend on live runtime behavior.
  [Mitigation] Keep the change scoped to the fixture surface and require
  Windows-native proof before the card is promoted.
