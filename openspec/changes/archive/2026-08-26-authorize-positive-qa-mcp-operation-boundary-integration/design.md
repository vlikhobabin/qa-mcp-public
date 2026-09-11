## Context

Published R5-R2 defines the clean A4 → R7 → A5 → R8 sequence, and R7 is
now reviewed and published. R8 is intentionally capped at 300 added production
lines but declares repeated-defect risk, so deterministic ChangeRail preflight
requires an exact published authorization whose machine ceiling is above the
ordinary threshold. The minimum valid ceiling is 301.

A2, A3 and A4 are immutable authorization evidence for other successors and
MUST NOT authorize R8. A5 creates no runtime behavior and uses no live target,
protocol capture, frame range, replay, Windows process or cleanup surface.

## Goals / Non-Goals

**Goals:**

- publish one exact A5 source bound only to completed R5-R2 and future R8;
- require published R7 as a reciprocal dependency before A5 can publish;
- preserve canonical ids, board paths, integer/boolean types and six fields;
- retain machine ceiling 301 while R8 independently forbids a 301st line;
- prove exact finalized acceptance and bounded mismatch rejection.

**Non-Goals:**

- implement or test R8 public routing, MCP or ScenarioRunner behavior;
- authorize OSS-04E, old R5/R6, failed stashes or another capability;
- restore historical payloads or mutate external state;
- add authority, credentials, provider settings or wire protocol.

## Decisions

### 1. Publish one exact six-field object

The tracked A5 card exposes exactly one `Investigation authorization` JSON
object:

- `investigation_card`:
  `openspec/board/4.done/oss-04d-r5-r2-resolve-positive-result-mismatch-outcome.md`;
- `investigation_id`: `oss-04d-r5-r2-resolve-positive-result-mismatch-outcome`;
- `successor_card`:
  `openspec/board/3.inprogress/oss-04d-r8-integrate-positive-operation-boundary-public-paths.md`;
- `successor_id`: `oss-04d-r8-integrate-positive-operation-boundary-public-paths`;
- `production_loc_ceiling`: exact integer `301`;
- `allow_new_authority_or_wire_protocol`: exact boolean `false`.

No alias, extension field, alternate path or reusable wildcard is allowed.

### 2. Keep relations reciprocal and sequential

Published R5-R2 blocks A5 and R8. Published R7 blocks A5. A5 depends on both
R5-R2 and R7 and blocks R8. R8 depends on R5-R2, R7 and A5 and references the
tracked completed A5 card as its one published investigation authorization.
Consumption is valid only after A5 is tracked unchanged in `4.done` and R8 is
at the exact named `3.inprogress` path.

### 3. Separate parser ceiling from delivery cap

The shared parser needs a ceiling above ordinary 300 to recognize bounded
authorization, so A5 uses 301. R8's card independently limits added production
lines to at most 300. A5 grants no 301st line and no repository-wide exception.

### 4. Prove finalization in an isolated candidate

Before publish, an isolated candidate derived from the reviewed payload SHALL
finalize A5 to `4.done`, move R8 to its declared `3.inprogress` path and run
deterministic preflight. The exact candidate must recognize the source and
ceiling. Bounded candidates with a changed authorization id/reference or
successor id/path must fail closed. Temporary candidate state is removed;
only bounded secret-free results are retained.

## Risks / Trade-offs

- **A5 is reviewed before its deterministic board move** → exercise the exact
  post-finalization relation in an isolated candidate before push.
- **Ceiling 301 can be mistaken for implementation scope** → repeat R8's hard
  300-line cap in card, spec and evidence.
- **Historical authorization could appear reusable** → require the exact six
  fields and reciprocal source/successor relations, with negative candidates.

## Migration Plan

1. Publish A5 metadata after isolated candidate proof and fresh GO.
2. Deliver R8 from clean published `main`; its preflight consumes A5.
3. Keep OSS-04E blocked until reviewed R8 publishes.
4. If A5 is reverted or altered, R8 fails closed and cannot publish.

## Open Questions

None.
