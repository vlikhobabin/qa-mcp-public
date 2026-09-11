## Context

The state model change gives V3 a deterministic local baseline. The next
piece is the handler layer that updates that baseline without crossing into
business commands or other persistent side effects.

## Goals / Non-Goals

**Goals:**

- Add local input, toggle and inert action handlers that mutate only fixture
  state.
- Keep handler behavior deterministic and resettable.
- Fail closed for targets that are outside the mutation sandbox.
- Preserve a clear path back to the V1 baseline after each interaction.

**Non-Goals:**

- Business command execution or data writes.
- Manager-side runner changes.
- Dialog, warning or error workflow support beyond inert local handling.

## Decisions

- Use a shared handler dispatcher rather than independent ad hoc event code.
  This keeps the allowed mutation paths explicit and makes it harder for a
  control-specific branch to bypass the reset model.
- Treat inert button clicks as local marker updates only. Alternatives such as
  wiring them to business commands were rejected because that would blur the
  V2/V3 boundary and complicate recovery evidence.
- Reject unsupported targets early instead of trying to coerce them into a
  mutation path. That keeps the sandbox fail-closed and reduces accidental
  writes.

## Risks / Trade-offs

- [Risk] A control could look inert but still trigger a platform command.
  [Mitigation] Only allow handlers that are tied to the reviewed mutation
  target map and verify the no-write path with runtime evidence.
- [Risk] Handler branching could drift from the shared state model.
  [Mitigation] Keep the update helper central and make the handler tests
  assert marker transitions, not just return codes.
- [Risk] Input normalization may differ across platform builds.
  [Mitigation] Keep the scope to stable local targets and preserve the raw
  observed marker values in the evidence plan.
