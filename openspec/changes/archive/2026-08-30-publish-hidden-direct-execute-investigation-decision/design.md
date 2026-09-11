## Context

OSS-06-I1 retained exact-source hidden-desktop, direct-`/Execute`, real-prompt,
recovery and cleanup evidence. Its combined production payload is too large for
ChangeRail semantic review, so the evidence decision must become a clean
published prerequisite before implementation is decomposed.

## Goals / Non-Goals

**Goals:**

- Publish one exact-lineage, privacy-safe engineering decision.
- Distinguish the failed chooser hypothesis from the eligible direct route.
- Bind the decision to the exact final successor id required by ChangeRail.

**Non-Goals:**

- Publish or modify production code.
- Admit the stable tool or authorize a generic hidden-desktop executor.
- Repeat Windows actions or treat diagnostic visible-desktop evidence as proof.

## Decisions

### Publish a decision, not the retained implementation

The card owns only decision/spec/card documentation and a sanitized evidence
audit. Its manifest excludes every production path as preexisting successor
work. This keeps deterministic production complexity at zero.

### Preserve exact retained lineage

The decision references the final source/executable/wheel hashes, exact Windows
platform and declared target, prompt-off/on/recovery outcomes and cleanup
receipt. It does not copy raw UI, screenshots, credentials or configuration.

### Name one final successor

The published investigation `Blocks` exactly
`oss-06-s7-admit-hidden-direct-execute-public-route`. Intermediate foundation
cards remain non-admitting and cannot consume the final authorization.

## Risks / Trade-offs

- [Retained evidence is mistaken for fresh final certification] -> Mark it as
  investigation lineage and require a repeated exact-source native matrix in S7.
- [Dirty production paths leak into publication] -> Require exact manifest
  exclusion and working-tree scope-check before review.
- [Decision broadens authority] -> Keep production/runtime/profile behavior
  explicitly unchanged.

## Migration Plan

Publish this documentation-only card first. Then publish the separate bounded
authorization card and deliver foundation successors sequentially. Rollback is
removal of the decision documentation before publication; no runtime rollback
exists because this change performs no runtime action.

## Open Questions

- Exact foundation file/function partitions are finalized just-in-time by each
  successor FF pass while preserving its `<=300` preflight result.
