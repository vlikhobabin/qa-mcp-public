## Context

The fixture already exposes read-only controls and a resettable local state
model. V2 needs a small set of safe handlers that operate only on the local
fixture surface and update the shared state model in a predictable way.

## Goals / Non-Goals

**Goals:**

- Implement handlers for the first V2 allowlist of non-mutating UI actions.
- Make every successful handler update the shared local state model.
- Fail closed for excluded action families.
- Keep menu, popup and page interactions local to the fixture.

**Non-Goals:**

- Business command execution.
- Text input or persisted value mutation.
- Manager runner, capture pipeline or recovery orchestration.

## Decisions

- Use one dispatcher that maps action families to small handler routines rather
  than branching in the UI event layer. That keeps the allowed surface explicit
  and easier to audit.
- Reuse the shared state update helper from the state-model change so handler
  success and reset semantics stay aligned.
- Treat popup, menu and group expansion as inert UI surface changes only when
  they do not execute a command. This preserves the V2 non-mutating boundary.
- Reject excluded requests before they reach the underlying control action so
  there is no accidental business-side effect.

## Risks / Trade-offs

- [Risk] A handler may accidentally execute a command path hidden behind a UI
  affordance.
  [Mitigation] Keep the allowlist narrow and verify the rejected families with
  live fixture evidence.
- [Risk] Row selection may affect a control beyond local UI state.
  [Mitigation] Restrict selection to the fixture-local table and confirm the
  reset hook restores the previous baseline.
- [Risk] Action result markers may become noisy if the counter updates on
  rejected actions.
  [Mitigation] Increment the counter only for allowlisted, successful
  fixture-local actions.
