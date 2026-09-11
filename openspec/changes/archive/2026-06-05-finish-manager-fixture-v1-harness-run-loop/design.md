## Context

The current manager fixture source defines a V1 command catalog, manifest
validation helpers, JSON/JSONL writers and a single read-only command
dispatcher. It does not yet expose a complete runner that loads the manifest,
connects to the proxy TestClient and executes the command list with durable
before/after events.

## Goals / Non-Goals

**Goals:**

- Provide one explicit harness entrypoint for a manifest-driven V1 run.
- Execute the selected read-only commands in manifest order.
- Preserve command events even when one command fails.
- Write a compact final result under the capture runtime directory.

**Non-Goals:**

- No clicks, input, page switches, row selection or business writes.
- No TCP parsing inside 1C.
- No accepted protocol mapping promotion.
- No full V2 safe-action behavior.

## Decisions

1. Treat command failure as run evidence.
   Rationale: a failed TestManager API call can still provide useful protocol
   evidence if the command boundary and exception are retained.

2. Emit both before and after events for each command.
   Rationale: frame join needs a narrow side-channel window and a post-result
   marker for review.

3. Keep final status separate from per-command event rows.
   Rationale: `case_events.jsonl` is append-friendly, while
   `manager_harness_result.json` gives the capture runner one compact summary.

4. Reject non-read-only commands before opening the TestClient connection.
   Rationale: the V1 pipeline must stay safe even when a malformed manifest is
   supplied.

## Verification Matrix

The implementation change affects 1C form-module behavior and runtime
execution. The detailed evidence requirements are tracked in `tasks.md`.

## Risks / Trade-offs

- The harness entrypoint must be invokable from the current manager startup
  path. If Vanessa EPF or direct 1C invocation cannot call it, the capture
  runner change must record a provider/runtime gap.
- TestManager APIs may return localized object presentations. The run loop
  should store target markers separately from result previews.
- A command sequence that shares one TestClient session can include background
  refresh traffic. Frame join remains a later analyzer responsibility.
