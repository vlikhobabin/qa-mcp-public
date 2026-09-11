## Context

OSS-04D-R2 is published in `4.done` and names OSS-04D-A1 as the only
authorization step before OSS-04D-R3. R3 is a repeated-defect successor whose
typed operation-evidence boundary is intentionally capped at 500 added
production lines. ChangeRail preflight accepts that exception only from a
published, unchanged `4.done` source card with exact reciprocal relations.

This payload changes only OpenSpec workflow and board metadata. It makes no
protocol claim, uses no capture source or frame range, and requires no live 1C,
TestClient, Windows, Docker, host-agent or runtime cleanup.

## Goals / Non-Goals

**Goals:**

- materialize one exact authorization source for R3;
- bind R2, A1 and R3 through canonical ids and board paths;
- preserve the 500-line ceiling and forbid new authority or wire protocol;
- prove exact successor acceptance and mismatched reuse rejection.

**Non-Goals:**

- implement any OSS-04D-R3 runtime code or test fixture;
- restore either failed OSS-04D payload;
- raise a repository-wide complexity limit;
- authorize OSS-04E or any other successor;
- claim Windows or live-runtime verification from a metadata-only payload.

## Decisions

### 1. Use the ChangeRail closed authorization object

The published A1 card SHALL expose exactly one `Investigation authorization`
JSON object with exactly these fields:

- `investigation_card` and `investigation_id` for the published R2 card;
- `successor_card` and `successor_id` for the single R3 card;
- integer `production_loc_ceiling` equal to `500`;
- boolean `allow_new_authority_or_wire_protocol` equal to `false`.

No extension fields or alternate identifiers are allowed. This reuses the
existing ChangeRail contract instead of creating a qa-mcp-specific parser.

### 2. Require reciprocal tracked board relations

R2 SHALL contain a `Blocks` reference to R3. A1 SHALL contain a `Depends On`
reference to R2. R3 SHALL contain `Depends On` references to R2 and A1. After
A1 publish finalization, R3 SHALL expose one `Published investigation
authorization` reference to the completed A1 card.

The A1 source is usable only after it is in `4.done` and unchanged at `HEAD`.
This prevents an in-progress card or dirty local authorization from granting a
complexity exception.

### 3. Keep the exception successor-specific and capability-specific

The authorization applies only to R3 and the typed operation-evidence boundary
defined by published R2. It does not permit another card, a second capability,
more than 500 production lines, or any new authority/wire protocol.

### 4. Verify the publish candidate deterministically

Before push, the publish workflow SHALL finalize A1 to `4.done`, update the R3
reference, create the exact candidate commit and run deterministic preflight
against R3. The accepted result must report the exact authorization source and
500-line ceiling. A bounded negative candidate with a mismatched successor id
or card path must return an invalid authorization / investigation-required
outcome.

The review payload retains only sanitized command outcomes and hashes. It does
not retain repository copies, credentials or raw broad logs.

## Risks / Trade-offs

- [Risk] Review occurs before A1 is a tracked `4.done` source. → Independently
  audit the exact finalization contract, then require a deterministic R3
  preflight on the candidate commit before push.
- [Risk] Board links drift during later moves. → Use canonical paths and update
  only deterministic board metadata during finalization.
- [Risk] The 500-line allowance becomes a reusable waiver. → Require exact
  investigation/source/successor reciprocity and reject any mismatch.

## Migration Plan

1. Publish R2 reciprocal `Blocks` metadata, the A1 source and R3 dependency
   metadata as one reviewed authorization payload.
2. Finalize A1 to `4.done`, set the exact R3 published-authorization reference
   and amend the scoped commit.
3. Run R3 preflight against that exact committed tree before push.
4. If the exact chain is not accepted, do not push; return A1 to delivery and
   review rather than weakening the relation.

Rollback is board/OpenSpec-only: revert the scoped authorization commit. R3
then has no valid published authorization and deterministic preflight fails
closed.

## Open Questions

- None. Any request for a higher ceiling, another capability or new authority
  is a new investigation and authorization, not an A1 adjustment.
