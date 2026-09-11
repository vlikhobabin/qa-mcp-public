## Context

The fixture state model, handlers and published target rows are in place, but
the V2 surface still needs a recovery proof that each action can be reset and
that the evidence isolates the action window from background traffic.

## Goals / Non-Goals

**Goals:**

- Define the recovery evidence sequence for every safe action.
- Prove that reset returns the fixture to the V1 baseline after each action.
- Keep action candidate ranges separate from refresh and cleanup traffic.
- Capture compact reviewed evidence instead of raw runtime payloads.

**Non-Goals:**

- New safe-action families.
- Business-data mutation or rollback semantics.
- Manager-runner implementation.

## Decisions

- Treat recovery as part of every safe-action case rather than as a separate
  optional follow-up. That keeps the V2 surface fail-closed.
- Record before, action, post and recovery checkpoints around the same target
  so evidence readers can compare state transitions without reconstructing the
  flow from logs.
- Label bootstrap, refresh and cleanup traffic separately from the candidate
  action range to avoid false positives when reading the capture.
- Keep the recovery proof local to the fixture. If reset fails, the action case
  is rejected rather than partially accepted.

## Risks / Trade-offs

- [Risk] Background refresh traffic may overlap the action window.
  [Mitigation] Require an isolated candidate range and retain the cleanup
  labels separately.
- [Risk] Recovery can pass once but drift across repeated runs.
  [Mitigation] Compare repeated captures and keep the reset path deterministic.
- [Risk] The fixture may be resettable only on some platform builds.
  [Mitigation] Capture the build-dependent failure as a documented residual
  risk instead of treating it as acceptance.
