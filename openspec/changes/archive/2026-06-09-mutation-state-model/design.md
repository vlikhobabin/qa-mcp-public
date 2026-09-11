## Context

V2 established a manifest-gated safe-action boundary with transient UI state
markers and reset behavior. V3 needs a richer local state model for mutation
scenarios, but the mutation state must still remain fixture-local and must not
imply business-data persistence or external side effects.

## Goals / Non-Goals

**Goals:**

- Define a single local mutation state record for the fixture.
- Keep baseline state and mutated state deterministic across repeated runs.
- Ensure reset returns the form to the V1 baseline after each mutation.
- Keep the state model isolated from business data and external services.

**Non-Goals:**

- Business object writes, posting, deletion or data exchange.
- Manager-side runner changes.
- Dialog, warning or error recovery semantics beyond the fixture reset hook.

## Decisions

- Store the mutation state inside the form module rather than in an external
  file or runtime service. This keeps the state observable together with the
  fixture and avoids another persistence layer.
- Update all `PF_*` markers through a shared helper instead of scattering
  assignments across handlers. That reduces drift and keeps the baseline reset
  path consistent.
- Treat action counters as local monotonic counters for successful
  fixture-local mutations only. This gives downstream evidence a stable order
  signal without implying business-side progress.
- Implement reset as a shared routine that restores the baseline state object
  instead of clearing fields ad hoc. That makes the baseline reproducible
  after every mutation scenario.

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
