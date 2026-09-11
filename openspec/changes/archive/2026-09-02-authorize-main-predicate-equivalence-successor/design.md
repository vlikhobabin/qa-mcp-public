## Context

Published I10 records its decision in
`docs/protocol-research/evidence/main-predicate-equivalence-contract-2026-09-02/decision.json`.
Its `authorization_source.payload` is the sole exact source for I10a. The
machine decision distinguishes a quantitatively sufficient five-path,
301-production-LOC envelope from the separate exact authorization identity
that I11 must consume.

ChangeRail requires that authorization identity to be an unchanged tracked
`4.done` card, dependent on the published investigation and bound to one exact
successor. I10a supplies only that source. I11 remains in `2.todo` and the
S4-R1 parent remains blocked until I10a has fresh independent review and scoped
publication; the authorization object preserves I11's declared future
authorization-time `3.inprogress` path without moving or editing I11.

There are no new TestClient protocol claims, capture sources, frame ranges,
dynamic fields or replay steps. No process, endpoint, target or runtime is used,
so execution and cleanup are not applicable.

## Goals / Non-Goals

**Goals:**

- Publish the exact I10-decision six-field authorization for exact I11.
- Bind the object to one unchanged published I10 dependency and one exact
  successor id/path.
- Preserve the complete 301-production-LOC ceiling and closed authority/wire
  flag without certifying I11.
- Produce a docs/OpenSpec-only payload suitable for fresh independent review.

**Non-Goals:**

- Starting, implementing, measuring, reviewing or certifying I11.
- Editing any host-agent product/test file, I11 card byte or S4-R1 parent byte.
- Adding product/runtime behavior, public API, route, authority, wire protocol,
  retry, fallback, wait, live probe or external operation.
- Running Windows, PowerShell, 1C, endpoint, lab/live/action, S5/S7, SSH or
  other external work.

## Decisions

### 1. Preserve the machine decision's exact six-field source object

The I10a card and normative capability use the I10 machine decision's
`authorization_source.payload` unchanged:

```json
{"investigation_card":"openspec/board/4.done/oss-06-s4-r1-i10-investigate-main-predicate-equivalence-contract.md","investigation_id":"oss-06-s4-r1-i10-investigate-main-predicate-equivalence-contract","successor_card":"openspec/board/3.inprogress/oss-06-s4-r1-i11-enforce-main-predicate-equivalence-contract.md","successor_id":"oss-06-s4-r1-i11-enforce-main-predicate-equivalence-contract","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}
```

No field is optional and the object grants no reusable authority. The
`301` ceiling is a conditional future envelope, not an I11 size or acceptance
claim. Reconstructing the object from prose, a predecessor authorization or an
I11 artifact is rejected because the published machine decision is the sole
exact source.

### 2. Use one exact published investigation dependency

I10a depends only on
`oss-06-s4-r1-i10-investigate-main-predicate-equivalence-contract`. The
investigation path points to its unchanged tracked `4.done` card, whose
`Blocks` relation names exact I11. A different dependency, path, id, lane,
ceiling or authority flag invalidates the source.

### 3. Keep I11 composition and admission out of I10a

I10a does not read or edit I11 product/test content and does not move or edit
the I11 card. Exact five-path scope, initial/final blob lineage, production LOC
at or below `301`, connected RED/GREEN matrices, call/privacy invariants,
focused/full Go checks, Linux not-live suite, unexecuted cross-builds and every
other I10 proof-floor condition remain future I11 admission work.

Only after I10a is independently reviewed and published unchanged in `4.done`
may a separate I11 session move exact I11 to its authorization-time
`3.inprogress` path and compose the reciprocal reference. That future work must
validate the exact graph and all I10 conditions.

### 4. Publish only documentation under Apache-2.0

The reviewed payload is limited to this board card, OpenSpec authorization
artifacts, the synced capability and deterministic board/archive metadata.
Apache-2.0 remains unchanged. Test-first, Windows-native and live verification
are prohibited and not applicable because no product/test behavior changes.

## Risks / Trade-offs

- [The object is reconstructed or normalized differently] -> Compare every
  normative one-line JSON copy byte-for-byte with `authorization_source.payload`
  serialized in its decision key order and assert exactly six keys.
- [The ceiling is mistaken for I11 certification] -> State that path, LOC,
  blob and verification proof remains future I11 admission work.
- [The authorization is broadened or reused] -> Preserve exact paths, ids,
  six fields, sole I10 dependency, `301` ceiling and `false` authority flag.
- [I11 or the parent advances early] -> Leave both tracked cards byte-for-byte
  unchanged until I10a is reviewed and published.

## Migration Plan

1. Validate, sync and archive this docs/OpenSpec-only authorization change.
2. Obtain a fresh independent ordinary/high GO verdict for the exact payload.
3. Publish I10a unchanged in `4.done` with explicit scoped staging.
4. Leave I11 and the S4-R1 parent blocked for a separate future session.

Rollback before publication removes no runtime behavior. After publication,
any content change requires a new reviewed payload; I11 fails closed when the
source is missing, stale, mismatched or untracked.

## Open Questions

None. I10's machine decision fixes the complete object and graph.
