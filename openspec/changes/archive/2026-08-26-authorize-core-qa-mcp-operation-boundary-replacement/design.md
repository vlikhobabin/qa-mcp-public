## Context

OSS-04D-R4-R1 is published in `4.done` and defines the replacement operation
boundary plus the ordered A2 → R5 → A3 → R6 handoff. R5 is a repeated-defect
successor capped by its own card at 300 added production lines. ChangeRail
preflight requires a separate published authorization source because its
machine ceiling must be greater than the ordinary 300-line threshold; the
narrowest valid ceiling is therefore 301.

This payload changes only OpenSpec workflow and board metadata. It makes no
protocol claim, uses no capture source or frame range, and requires no live 1C,
TestClient, Windows, Docker, host-agent or runtime cleanup.

## Goals / Non-Goals

**Goals:**

- materialize one exact authorization source for R5;
- bind published R4-R1, A2 and future in-progress R5 through canonical ids and
  board paths;
- preserve the machine ceiling of 301 and R5's stricter delivery cap of 300;
- forbid new authority or wire protocol;
- prove exact successor acceptance and bounded mismatched reuse rejection.

**Non-Goals:**

- implement any OSS-04D-R5 runtime code or tests;
- authorize A3, R6, OSS-04E or another successor;
- restore or publish an exhausted R3/R4 payload;
- raise a repository-wide complexity limit;
- claim Windows or live-runtime verification from metadata-only work.

## Decisions

### 1. Use one closed six-field ChangeRail authorization object

The published A2 card SHALL expose exactly one `Investigation authorization`
JSON object containing:

- `investigation_card` and `investigation_id` for published R4-R1;
- `successor_card` and `successor_id` for R5 at its exact future
  `3.inprogress` review path;
- integer `production_loc_ceiling` equal to `301`;
- boolean `allow_new_authority_or_wire_protocol` equal to `false`.

No extension fields, aliases or alternate successor paths are allowed. This
reuses the shared ChangeRail parser and creates no qa-mcp-specific authority.

### 2. Keep reciprocal relations independently inspectable

R4-R1 SHALL block R5. A2 SHALL depend on R4-R1 and block R5. R5 SHALL depend
on both R4-R1 and A2. After A2 publish, R5 SHALL retain one `Published
investigation authorization` reference to the completed A2 card.

The source is usable only after A2 is tracked unchanged in `4.done`. R5 must be
at the exact `3.inprogress` path named by A2 when its deterministic preflight
consumes the source.

### 3. Separate the machine ceiling from the implementation cap

The shared parser accepts bounded authorization only above the ordinary
300-line threshold, so A2 uses the minimum accepted value, 301. R5's own
acceptance continues to impose an at-most-300 added production-line cap. A2
does not authorize a 301st production line; it only allows deterministic
preflight to recognize the separately published investigation relationship.

### 4. Prove the finalized candidate before push

The publish workflow SHALL finalize A2 to `4.done`, advance R5 to its declared
`3.inprogress` path in an isolated candidate, and run deterministic preflight
against R5. The exact candidate must report a valid source with ceiling 301. A
bounded candidate that changes the successor id or source reference must fail
closed.

Only sanitized outcomes and hashes are retained. No temporary candidate tree,
credentials or broad raw logs are committed.

## Risks / Trade-offs

- [Risk] Review happens before A2 is a tracked `4.done` source. → Audit the
  exact finalization contract, then prove the isolated finalized candidate
  before push.
- [Risk] A 301 machine ceiling is mistaken for R5's implementation budget. →
  Repeat the independent R5 cap of 300 in the authorization spec, card and
  evidence.
- [Risk] A2 is reused for R6 or another payload. → Require exact successor
  path/id, reciprocal relations and a mismatch-negative preflight control.

## Migration Plan

1. Publish R4-R1 reciprocal `Blocks` metadata, the A2 source and R5 dependency
   metadata as one reviewed authorization payload.
2. Finalize A2 to `4.done` and verify the exact R5 published-source reference.
3. In an isolated candidate, move R5 to its exact `3.inprogress` path and run
   positive plus mismatched deterministic preflight checks.
4. Push only when the candidate is accepted without weakening the R5 cap.

Rollback is board/OpenSpec-only: revert the scoped authorization commit. R5
then has no valid published authorization and preflight fails closed.

## Open Questions

- None. A higher R5 cap, another successor or new authority/wire protocol
  requires a new investigation and authorization.
