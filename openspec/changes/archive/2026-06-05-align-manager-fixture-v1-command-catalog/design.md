## Context

The V1 dry-run manifest lists a smaller command set than the current manager
harness source. If this drift reaches a live capture, command events and frame
join reports will be ambiguous because the analyzer will not know which command
set is authoritative.

## Goals / Non-Goals

**Goals:**

- Establish one reviewed V1 catalog shape.
- Align PowerShell and BSL catalog command ids.
- Define a bounded smoke subset separately from the full catalog.
- Preserve rejected action/mutation command kinds.

**Non-Goals:**

- No full API inventory expansion.
- No live capture execution.
- No protocol normalization changes.

## Decisions

1. Keep command ids stable and kebab-like.
   Rationale: command ids appear in manifests, events, reports and reviewed
   evidence, so renames are expensive.

2. Treat the smoke subset as an execution filter, not a separate catalog.
   Rationale: the full catalog remains visible while the first live run stays
   small.

3. Require target marker and expected marker for every command.
   Rationale: marker drift should fail during catalog review before a live
   capture is attempted.

## Verification Matrix

The implementation change affects BSL catalog source and protocol tooling.
The detailed matrix is in `tasks.md`.

## Risks / Trade-offs

- A generated shared catalog reduces drift but adds one more artifact to keep
  reviewed.
- A static catalog can become stale if the client fixture changes; target-map
  evidence must remain linked.
