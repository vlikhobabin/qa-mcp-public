## Context

Prior V2 and V3 work kept action evidence candidate-only when frame windows
were ambiguous. Card 61 must keep the same discipline for real demo mutations:
runtime behavior, visual result and cleanup are not enough unless action frames
can be isolated or the row is explicitly classified as non-accepted.

## Goals / Non-Goals

**Goals:**

- Join guarded-pilot phase events to frame or chunk ranges where available.
- Separate action, background/refresh and recovery ranges for every attempted
  row.
- Record dynamic fields, normalized hashes, operation tokens and response
  markers when supported by the analyzer.
- Preserve precise unresolved reasons and provider gaps.

**Non-Goals:**

- Running additional demo mutations.
- Changing the manifest or target-selection contract.
- Publishing final corpus decisions; that belongs to
  `publish-demo-mutation-corpus-decision`.
- Accepting rows without replay, direct Python-manager probe or accepted typed
  contract proof.

## Decisions

- Treat action-frame isolation as an evidence review step, not an execution
  step.
- Allow `candidate`, `partial`, `timeout`, `rejected` or `blocked` outcomes
  when ranges cannot be joined; do not force an accepted classification.
- Keep background and recovery ranges separate even when they are adjacent to
  the action range.
- Route missing analyzer, provider or replay capabilities to their owner path
  rather than labeling them as generic manual work.

## Risks / Trade-offs

- [Risk] Background refresh traffic may look like action traffic. Mitigation:
  require phase labels and keep refresh-only ranges separate from action proof.
- [Risk] Frame joins may be unavailable if provider output is incomplete.
  Mitigation: classify the row as blocked, partial or candidate with owner
  route and retained evidence.
- [Risk] A cleaned-up mutation can still lack protocol proof. Mitigation:
  accepted status remains proof-gated and publication must preserve
  non-accepted rows.

## Migration Plan

- Consume the guarded-pilot evidence bundle.
- Run or review frame-range isolation against each attempted row.
- Write compact frame-isolation summaries and unresolved reasons.
- Hand the classification inputs to publication.

## Open Questions

- Which analyzer output format should become the compact reviewed artifact for
  real-demo mutation action ranges?
- Can any first-row-set action be directly probed by the Python manager, or
  will all rows initially remain candidate-only?
