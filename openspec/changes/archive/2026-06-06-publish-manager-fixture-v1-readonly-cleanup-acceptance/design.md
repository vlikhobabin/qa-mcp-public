## Context

The current status report already points to a next route: resolve the nine
pending rows, retain replay/probe summaries, adjust manifest only when
evidence proves the marker is wrong, and regenerate the cleanup live-join
report. This change is the publication gate for that route.

## Goals / Non-Goals

**Goals:**

- Produce one reviewed cleanup report for the 17 joined rows.
- Fold in only replay/probe summaries that satisfy the accepted gate.
- Preserve pending rows with exact reasons and next owner route.
- Update docs so the V1/V2 decision is reviewable.

**Non-Goals:**

- No new probe semantics; that belongs to the probe change.
- No historical evidence rewrite beyond updating the current reviewed cleanup
  state.
- No V2 safe action implementation.

## Decisions

1. Keep the accepted gate unchanged.
   The report may increase accepted counts only through matching replay/probe
   evidence.

2. Publish residual pending status explicitly.
   If any row remains pending, the report must explain whether V2 is blocked
   or can proceed with a documented residual risk.

3. Keep raw output ignored.
   Reviewed evidence links to compact summaries; raw traffic and full replay
   output remain under `runtime/`.

## Risks / Trade-offs

- Updating the existing cleanup evidence directory can obscure previous state.
  Mitigation: link classification and probe summaries and keep git history as
  the reviewed timeline.
- V1 may still have pending rows after this card. Mitigation: require an
  explicit V2 unblock/block decision in docs.

## Verification Matrix

Detailed rows are in `tasks.md`.
