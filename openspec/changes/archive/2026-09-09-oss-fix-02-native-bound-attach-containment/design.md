## Context

The accepted product roadmap identifies reachability being promoted to target
provenance. OSS-FIX-01 supplies immutable target configuration; its unpublished
stopped run must be reconciled before this card can execute. This change keeps
the original FIX-02 containment scope while adopting native OpenSpec ownership.

## Goals / Non-Goals

Goals: block unproven non-owned project attach, preserve validated owned launch
and explicit standalone attach, and explain the remaining observer gap.

Non-goals: a new observer, live attach, business-data access, platform capture,
protocol reverse engineering, historical-run finalization or automatic release.

## Decisions

1. Exercise the registered MCP factory boundary with synthetic reachable
   endpoints and inspect session state plus backend call records before/after.
   Function-only mocks cannot establish admission ordering at the public boundary.
2. Use current provider-owned observation only if an already admitted producer
   proves target and generation for this process. Otherwise block the path.
   Copying configuration into an observation would reproduce the trust defect;
   adding an observer would exceed this containment card.
3. Preserve owned and unbound paths with positive controls through their existing
   entry points. Do not weaken identity validation to make a positive fixture pass.
4. Retain test observations under the QA evidence contract. Implementation covers
   refusal ordering; independent review checks provenance ownership; the final
   floor supplies compatibility test observations. Semantic sync adds the new
   requirement while preserving the existing lifecycle scenarios.

## Risks / Trade-offs

- Input safety: caller identity can masquerade as observation → reject declared
  identity without trusted current process evidence (C1/C2).
- Mutation and external effects: an unproven attach can admit a session or send
  native commands → assert unchanged session state and zero backend commands (C1).
- Compatibility: containment can accidentally block owned or standalone use →
  positive controls and documentation of the deliberate bound-attach limitation (C3).
- Restart and concurrency are not changed: no new persistence, locks or scheduler.
  Publication is outside this implementation; the runner retains its existing gates.
- No new wire claim: captures, frame ranges, dynamic fields and replay evidence
  are inapplicable to this Python admission correction. Synthetic endpoints do
  not establish native Linux/Windows qualification.

## Migration Plan

After the final FIX-01 baseline is available, admit this native plan, implement
its two ordered groups, then let the runner own review and finalization. No data
migration is needed. A rollback must preserve fail-closed admission; restoring
the unproven attach path is not an acceptable compatibility workaround.
