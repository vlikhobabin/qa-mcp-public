## Context

The manager V2 runner and V2 tooling already define fail-closed row validation,
phase events and compact reporting. This change consumes the reviewed focused
subset and produces the first live run evidence for the proof, without adding
new action families or accepting mappings.

## Goals / Non-Goals

**Goals:**

- Execute only reviewed focused rows through the Windows-native V2 safe-action
  scenario.
- Record phase-aware side-channel events for pre-read, action, post-read and
  recovery.
- Preserve runtime output under ignored directories and compact summaries under
  retained evidence paths.
- Fail closed when the selected row is unavailable, unsafe or cannot recover.

**Non-Goals:**

- Running broad manager V2 coverage.
- Accepting protocol frame ranges.
- Executing business commands, text input, checkbox/value toggles, object
  writes, save/post/delete/fill/import/export or external side effects.

## Decisions

- Use the existing `manager-fixture-v2-safe-action` scenario rather than a
  bespoke proof runner. This keeps phase semantics aligned with the tooling
  pipeline.
- Use one run id across runtime output and compact summaries so later changes
  can trace action rows without copying raw traffic.
- Require recovery or documented known-state evidence after each attempted row.
  Rows without recovery proof stop before frame acceptance review.
- Treat blocked, rejected, partial and timeout outcomes as useful evidence when
  they include typed status and reason fields.

## Risks / Trade-offs

- [Risk] Live 1C startup can fail because local lab paths or sessions are not
  ready. [Mitigation] Retain startup/preflight summaries and mark rows blocked
  instead of retrying broad actions.
- [Risk] Cleanup traffic can be confused with action traffic. [Mitigation] Keep
  recovery events separate and leave frame grouping to the next change.
- [Risk] A selected row mutates state unexpectedly. [Mitigation] Stop the run,
  record fail-closed status and do not continue to additional rows.

## Migration Plan

- Consume the focused subset manifest.
- Run the Windows capture wrapper or manager runner scenario with a single run
  id.
- Retain compact run summaries and hand runtime paths to
  `isolate-focused-v2-safe-action-frames`.
- Retain a lightweight timestamp-to-traffic join when the live run emits both
  phase events and proxy traffic; joined rows remain candidate until the later
  replay/probe contract change.

## Open Questions

- Should the first run execute both selected rows in one capture, or execute the
  first row alone and use a second capture only after recovery is confirmed?
- Which operator-owned live-session preflight should be mandatory before the
  run starts?
