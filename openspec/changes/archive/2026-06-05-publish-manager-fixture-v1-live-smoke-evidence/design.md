## Context

The first live proof should be intentionally small. A two or three command
run reduces background traffic and lets the analyzer prove the core sequence:
custom manager harness command, proxy traffic, side-channel event, join row,
normalized corpus row and replay/probe status.

## Goals / Non-Goals

**Goals:**

- Run active-window, active-form and one marker-bearing fixture field command
  when runtime prerequisites are available.
- Publish compact live smoke evidence.
- Preserve unresolved gaps with owner routing.
- Establish the go/no-go gate for full V1 catalog expansion.

**Non-Goals:**

- No full V1 catalog run.
- No V2 safe actions.
- No mutation or business data write.
- No accepted mapping without replay/probe proof.

## Decisions

1. Smoke scope is limited to two or three commands.
   Rationale: a small scope makes frame joins reviewable and failures cheaper.

2. One joined normalized row is enough for this smoke.
   Rationale: the smoke proves the pipeline; full coverage comes later.

3. Provider gaps are publishable outcomes.
   Rationale: missing EPF/runtime assets should be explicit delivery evidence,
   not hidden as skipped work.

## Verification Matrix

This is a live evidence publication change. The detailed matrix is in
`tasks.md`.

## Risks / Trade-offs

- If the runtime asset remains absent, the change may publish a provider gap
  instead of live corpus evidence. That blocks full-catalog expansion but still
  preserves the delivery state.
- Direct Python replay/probe may not support the new request family yet. Rows
  must remain `pending` or `unsupported` until proof exists.
