## Context

Deterministic review preflight for the complete unpublished successor
`oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity` reported
approximately 313 added production lines against ChangeRail's default limit of
300. That report is retained lineage, not a new measurement or certification:
the successor implementation is deliberately absent from this isolated
metadata worktree and no bytes from it may be imported here.

The guard exists to force a bounded investigation or simplification when a
payload crosses 300 production lines. Deleting blank lines, changing which
files are classified as production, or excluding owned scope can lower a
counter without reducing the capability's real review complexity. Those
techniques therefore cannot support the decision.

The effective ChangeRail authorization graph requires a later exact successor
to reference a separate unchanged tracked authorization card in `4.done`.
That source carries an exact six-field `Investigation authorization` object,
depends on this published investigation, and binds this investigation plus the
successor by path and id. This change prepares the six-field data but does not
create that source or modify the successor.

There are no new TestClient protocol claims, captures, frame ranges, dynamic
fields, replay steps, or runtime cleanup obligations. All are not applicable
because this is an offline board/OpenSpec decision with no execution.

## Goals / Non-Goals

**Goals:**

- Bind one exact OSS-07-R1 successor id and authorization-time path.
- Set one maximum production envelope of 350 lines for that exact successor.
- Keep new authority and wire-protocol permission closed.
- Preserve the complete successor accounting boundary and the published
  Apache-2.0/OSS-07-I2 lineage.
- Prepare an independently checkable future authorization handoff.

**Non-Goals:**

- Reading, importing, editing, reclassifying, excluding, reviewing, testing,
  certifying, committing, or publishing the successor implementation payload.
- Restoring or reconstructing OSS-07-I1, or changing OSS-07-I2.
- Creating the later authorization card or changing the successor's dependency
  or review metadata.
- Changing the global 300-line guard or granting a reusable complexity waiver.
- Adding a capability, authority, public/wire protocol, live check, credential
  operation, mutation, release action, OSS-08 implementation, or OSS-09
  implementation.
- Running Windows, SSH, 1C, TestClient, live endpoint, Apache service, or
  network operations.

## Decisions

### 1. Bind only the exact OSS-07-R1 successor

The only eligible successor is
`oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity` at
authorization-time path
`openspec/board/3.inprogress/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md`.
The investigation's `Blocks` relation and the future six-field object use that
exact identity. Any changed id/path or another payload requires a new
investigation.

The alternative of importing the successor for direct inspection is rejected:
it would violate the isolated metadata scope and risk changing or
reclassifying the implementation under review.

### 2. Use a hard maximum ceiling of 350 without treating it as a target

The future source data sets `production_loc_ceiling` to `350`. The retained
approximately 313-line result establishes why 300 is insufficient; 350 is a
small bounded envelope that tolerates honest counter normalization and any
mandatory integrity correction while remaining far below the machine maximum
of 500. It is a maximum, not permission to add lines. A later fresh session
must count the complete exact payload and prove it is at or below 350 before
review.

A ceiling at or below 300 cannot clear the typed stop. A broad 500-line ceiling
is rejected as unnecessary authority. Choosing a raw value from whitespace
deletion, source reclassification, or scope exclusion is also rejected because
those operations obscure complexity instead of reducing it.

### 3. Preserve complete and stable complexity accounting

Future admission must count all successor-owned production paths under the
same classification and scope that produced the complete payload. Whitespace
may change only for a substantive, independently reviewed reason; it may not be
deleted to fit the limit. Production files may not be relabeled as tests,
fixtures, docs, generated content, or metadata to change the count. Owned
source may not be omitted from the manifest or authorization measurement.

If the complete payload exceeds 350, changes successor identity, or cannot
pass without one of those workarounds, this decision does not apply. Delivery
must split or investigate again rather than widen or evade the ceiling.

### 4. Keep authority, wire protocol, and external execution closed

The future source data sets
`allow_new_authority_or_wire_protocol` to `false`. The decision covers only
the current disclosure/provenance implementation already owned by OSS-07-R1.
It grants no live, SSH, Windows, 1C, TestClient, Apache, release, credential,
mutation, network, or other external authority. A new public or wire contract,
new authority, or runtime action invalidates this decision and requires new
scope.

### 5. Prepare one exact, non-reusable future source object

After this investigation is independently reviewed and published unchanged in
`4.done`, a later separate metadata-only authorization card may carry exactly:

```json
{"investigation_card":"openspec/board/4.done/oss-07-r1-i1-investigate-public-readiness-payload-complexity.md","investigation_id":"oss-07-r1-i1-investigate-public-readiness-payload-complexity","successor_card":"openspec/board/3.inprogress/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md","successor_id":"oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity","production_loc_ceiling":350,"allow_new_authority_or_wire_protocol":false}
```

That source must depend on this investigation. The successor must depend on
this investigation, this investigation must block the successor, and the
successor must later reference only the exact separate published authorization
source. This change neither creates that source nor supplies the successor
reference. Missing, additional, stale, untracked, or mismatched data remains
fail-closed.

### 6. Preserve published safety and license lineage

OSS-07-I2 remains byte-identical and OSS-07-I1 remains absent. Exact SPDX
`Apache-2.0` is preserved; no license file or license choice changes. OSS-08
and OSS-09 remain outside the payload.

## Risks / Trade-offs

- [The 350 ceiling is read as an implementation budget] -> State that it is a
  hard maximum for an already-owned exact payload and require a fresh complete
  count before authorization/admission.
- [Accounting changes create a false pass] -> Reject whitespace deletion,
  source reclassification, and scope exclusion as gate workarounds and require
  stable complete-scope measurement.
- [The investigation is mistaken for direct authorization] -> Require a later
  separate unchanged tracked `4.done` authorization source and keep the
  successor reference absent here.
- [The exception is reused] -> Bind exact investigation and successor paths/ids
  and require reciprocal links.
- [Offline metadata overclaims implementation facts] -> Treat approximately
  313 lines as retained trigger lineage only and make exact size, blob, scope,
  and verification proof future admission conditions.

## Migration Plan

1. Publish this metadata-only investigation unchanged in `4.done` after strict
   validation, scope/whitespace checks, and fresh independent review.
2. In a separate future delivery, create and publish one metadata-only
   authorization source with the exact six-field object and dependency on this
   investigation.
3. In the successor's isolated workspace, establish its complete production
   scope, exact count at or below 350, stable classification, and required
   verification evidence before adding reciprocal metadata.
4. Prove the successor implementation payload did not change during metadata
   composition, rerun deterministic preflight, and obtain a fresh independent
   review before publication.

Rollback changes no product behavior. Without the later exact authorization
source and reciprocal metadata, the successor remains safely blocked.

## Open Questions

None. The later authorization card's identity and the successor's exact
measurement/evidence remain intentionally outside this investigation.
