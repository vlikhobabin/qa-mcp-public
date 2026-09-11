## Context

The protocol lab has archived the controlled read-only fixture and element
hash cards, but their final outcomes remain partially unresolved. The next
card must therefore define a safe action boundary before capture tooling is
allowed to broaden from read-only requests into UI state transitions.

The current source of truth remains captured TestManager/TestClient traffic,
compact evidence under `docs/protocol-research/evidence/` and raw output under
ignored `runtime/protocol-research/`. Help, metadata and EDT sources may label
targets but cannot prove action protocol behavior.

## Goals / Non-Goals

Goals:

- Define the allowed first action families: focus or activate an element,
  activate an already opened window, switch an existing tab/page and expand a
  menu without invoking a command.
- Require every candidate action to document pre-state, action, post-state,
  recovery/cleanup expectation and accepted/unresolved precondition decisions.
- Keep unresolved read-only fixture and element-hash evidence visible when
  selecting action targets.
- Provide downstream changes with a stable safety gate before capture starts.

Non-goals:

- Do not capture live action traffic in this change.
- Do not add clicks that invoke business commands, text input, checkbox
  toggles, table edits, saves, posting, deletion or persisted data mutation.
- Do not promote package action descriptors.
- Do not depend on EDT/meta providers for raw protocol proof.

## Decisions

### Treat Safe Actions As A New Evidence Class

Safe UI action cases should use an explicit safety class such as
`safe_ui_action` rather than being folded into read-only rows. This preserves
the read-only boundary and makes action evidence reviewable during publication.

Alternative considered: label these as read-only because they should not write
business data. That would hide the fact that focus, activation and page
switching can still change transient UI state and require recovery evidence.

### Gate Each Candidate Before Capture

Each candidate action must name the target, why it is non-mutating, what state
will be observed before and after the action, and how the lab returns to a
known state. If a target depends on unresolved read-only fixture evidence, the
row must mark that dependency as deferred or blocked before capture.

Alternative considered: run captures first and decide safety afterward. That
would make it too easy to collect broad action traffic without an operator
review of mutation risk.

### Keep Business Mutations Out Of This Card

The first action layer should not treat command execution, input or write
semantics as safe even when performed against demo data. Those cases need a
separate rollback/recovery design and explicit operator intent.

## Risks / Trade-offs

- Safe UI actions can still trigger background refresh traffic -> mitigate by
  requiring action/result markers and a later analyzer separation step.
- Current fixture gaps may limit available targets -> mitigate by allowing
  `unsupported`, `pending` or `blocked` action rows rather than inventing
  evidence.
- Window or tab activation may alter transient state -> mitigate with
  pre-state, post-state and recovery expectations for every row.

## Migration Plan

No migration is required. The implementation should add docs/spec policy and
leave existing read-only evidence unchanged.

## Open Questions

- Which current lab form exposes a tab/page or expandable menu that can be
  manipulated without executing a command?
- Whether active-window activation can be confirmed by direct Python-manager
  probing or only by captured Vanessa/TestManager traffic in the first pass.
