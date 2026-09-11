## Context

Published R5-R2 replaces exhausted R5/R5-R1 and creates the ordered
A4 → R7 → A5 → R8 handoff. R7 is intentionally capped at 300 added production
lines but declares repeated-defect risk, so shared ChangeRail preflight requires
an exact published authorization whose machine ceiling is greater than the
ordinary threshold. The minimum valid ceiling is 301.

Historical A2 is immutable evidence for R5 and MUST NOT authorize R7. This A4
payload creates no runtime behavior and uses no live target.

## Goals / Non-Goals

**Goals:**

- publish one exact A4 source bound only to completed R5-R2 and future R7;
- preserve canonical ids, board paths, integer/boolean types and six fields;
- make R5-R2/A4/R7 relations reciprocal and fail closed;
- retain machine ceiling 301 while R7 independently forbids a 301st line;
- prove exact finalized acceptance and mismatched rejection.

**Non-Goals:**

- implement or test R7 runtime behavior;
- authorize A5, R8, OSS-04E, old R5/R6 or another capability;
- restore failed stashes or mutate external state;
- add authority, credentials, provider settings or wire protocol.

## Decisions

### 1. Publish one exact six-field object

The tracked A4 card exposes exactly one `Investigation authorization` JSON
object:

- `investigation_card`:
  `openspec/board/4.done/oss-04d-r5-r2-resolve-positive-result-mismatch-outcome.md`;
- `investigation_id`: `oss-04d-r5-r2-resolve-positive-result-mismatch-outcome`;
- `successor_card`:
  `openspec/board/3.inprogress/oss-04d-r7-implement-positive-core-operation-boundary.md`;
- `successor_id`: `oss-04d-r7-implement-positive-core-operation-boundary`;
- `production_loc_ceiling`: exact integer `301`;
- `allow_new_authority_or_wire_protocol`: exact boolean `false`.

No aliases, extension fields, alternate paths or reusable wildcard are allowed.

### 2. Keep relations reciprocal

Published R5-R2 blocks A4 and R7. A4 depends only on R5-R2 and blocks R7. R7
depends on R5-R2 and A4 and references the tracked completed A4 card as its one
published investigation authorization. Consumption is valid only after A4 is
tracked unchanged in `4.done` and R7 is at the exact named `3.inprogress` path.

### 3. Separate parser ceiling from delivery cap

The shared parser needs a ceiling above ordinary 300 to recognize bounded
authorization, so A4 uses 301. R7's card independently limits added production
lines to at most 300. A4 grants no 301st line and no repository-wide exception.

### 4. Prove finalization in an isolated candidate

Before publish, an isolated candidate derived from the reviewed payload SHALL
finalize A4 to `4.done`, move R7 to its declared `3.inprogress` path and run
deterministic preflight. The exact candidate must recognize the source and
ceiling. A bounded candidate with a changed successor id/path or authorization
reference must fail closed. Temporary candidate state is removed afterward;
only bounded secret-free outcomes are retained.

## Risks / Trade-offs

- A4 is reviewed before its deterministic card move. Candidate proof exercises
  the exact post-finalization relation before push.
- Ceiling 301 can be misread as implementation scope. Repeating R7 cap 300 in
  spec/card/evidence prevents that ambiguity.
- A future successor cannot reuse A4; it requires its own exact published
  authorization.

## Migration Plan

1. Publish A4 metadata after candidate proof and fresh GO.
2. Deliver R7 from clean published `main`; its preflight consumes A4.
3. If A4 is reverted, R7 fails closed and cannot publish.

## Open Questions

None.
