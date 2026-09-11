## Context

Published I7 decided that exact I4 is the only conditionally eligible bounded
successor for the repeated private inventory-classifier defect. I7 prepared the
machine authorization data but intentionally did not create I8, modify I4 or
certify any retained I4 implementation, size, blob or verification claim.

ChangeRail requires the separate authorization source to be an unchanged
tracked `4.done` card, to depend on the published investigation, and to expose
exactly six machine fields. This change supplies only that source. It does not
compose I4's future dependency/reference metadata.

There are no new TestClient protocol claims, capture sources, frame ranges,
dynamic fields or replay steps. No process, endpoint or target is used, so
runtime execution and cleanup are not applicable.

## Goals / Non-Goals

**Goals:**

- Publish the exact I7-prepared six-field authorization for exact I4.
- Bind the authorization to one unchanged published I7 dependency and one
  exact successor id/path.
- Preserve all I7 conditions as future I4 admission work, not I8 evidence.
- Produce a docs/OpenSpec-only payload suitable for fresh independent review.

**Non-Goals:**

- Accessing, copying, changing, measuring, reviewing, staging or publishing any
  retained I4 workspace, file, card or metadata byte.
- Establishing I4's path/LOC/blob identities or hostile verification results.
- Adding product/test implementation, runtime behavior, authority, wire
  protocol, retry, fallback, wait, live probe or external operation.
- Running Windows, PowerShell, 1C, endpoint, target, SSH, live or historical-user
  operations.

## Decisions

### 1. Preserve the exact six-field source object

The card and normative capability use the I7-prepared object unchanged:

```json
{"investigation_card":"openspec/board/4.done/oss-06-s4-r1-i7-investigate-private-inventory-classifier-contract.md","investigation_id":"oss-06-s4-r1-i7-investigate-private-inventory-classifier-contract","successor_card":"openspec/board/3.inprogress/oss-06-s4-r1-i4-classify-hidden-desktop-inventory-refusal-cause.md","successor_id":"oss-06-s4-r1-i4-classify-hidden-desktop-inventory-refusal-cause","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}
```

The object contains no optional field and grants no reusable authority. The
minimum valid `301` ceiling is a conditional deterministic envelope, not a
measurement or certification of retained I4.

### 2. Use one exact published investigation dependency

I8 depends only on
`oss-06-s4-r1-i7-investigate-private-inventory-classifier-contract`. The
source path points to its unchanged tracked `4.done` card, whose `Blocks`
relation names exact I4. Another dependency, investigation path/id, successor
path/id, ceiling or authority flag invalidates the source.

### 3. Keep I4 admission and composition out of I8

I8 neither reads nor edits I4. The at-most-five-path set, production LOC not
exceeding `301`, exact blob identities, complete 15-row hostile RED/GREEN
matrix, privacy/cause/count checks, focused/full Go tests and vet, Linux tests,
non-executed amd64/386 Windows cross-builds, strict OpenSpec, scope and
whitespace checks remain future admission conditions. No retained local claim
is accepted as proof.

Only after I8 is independently reviewed and published unchanged in `4.done`
may a later authorized I4 session add its exact I7 dependency and exact
two-field I8 reference. That later work must prove all I7 conditions without
changing the admitted product/test blobs.

### 4. Publish only documentation under Apache-2.0

The reviewed payload is limited to this board card, OpenSpec authorization
artifacts, the synced capability and deterministic board/archive metadata.
Apache-2.0 remains unchanged. Windows-native, test-first and live execution are
not applicable to a payload with no product/test behavior.

## Risks / Trade-offs

- [The ceiling is mistaken for a retained-I4 size claim] -> State consistently
  that path/LOC/blob verification is future admission work.
- [The source is reused or broadened] -> Preserve exact paths, ids, six fields,
  dependency, `301` ceiling and `false` authority flag.
- [I8 is treated as product authority] -> Keep every product, test, runtime and
  external surface out of scope and review the exact docs-only payload.
- [I4 references unpublished or changed I8] -> Require fresh independent GO and
  publication unchanged in `4.done` before any later I4 composition.

## Migration Plan

1. Validate, sync and archive this docs/OpenSpec-only authorization change.
2. Obtain a fresh independent ordinary-risk GO verdict for the exact payload.
3. Publish I8 unchanged in `4.done` with explicit scoped staging.
4. Hand off exact I4 to a separate fresh session for its still-unproven
   path/LOC/blob/hostile admission checks and metadata composition.

Rollback before publication removes no runtime behavior. After publication,
any content change requires a new reviewed payload; I4 fails closed when the
source is missing, stale, mismatched or untracked.

## Open Questions

None. I7 fixes the complete authorization object, dependency, successor and
future admission floor.
