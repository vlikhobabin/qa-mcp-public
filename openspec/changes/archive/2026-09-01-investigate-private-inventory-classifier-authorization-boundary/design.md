## Context

I3 published one behavior-neutral classifier direction for the unresolved
hidden-desktop inventory boundary, and I6 later published the private fenced
seam needed to implement it. The operator handoff designates exact I4 as the
successor that declares `Repeated defect class: yes`, but its local
implementation size, blob identity, tests and prior preflight are not present
as immutable evidence in I7 and are not certified by this decision.

The effective ChangeRail parser accepts a repeated-defect exception only when:

1. the successor references a separate unchanged tracked authorization card
   in `4.done` with exactly `authorization_card` and `authorization_id`;
2. that authorization card has `Investigation authorization` JSON containing
   exactly the investigation path/id, successor path/id, a numeric ceiling in
   `301..500`, and a boolean authority/wire flag;
3. the authorization card depends on the published investigation;
4. the published investigation blocks the exact successor; and
5. the successor depends on the exact investigation.

I3 and I6 supply reviewable product/design lineage but do not implement this
graph. This change publishes only the missing investigation decision. No
source, test, fixture, runtime evidence or OpenSpec artifact is copied from the
operator-retained I4 workspace, and its reported results are future admission
conditions rather than I7 evidence.

There are no new TestClient protocol claims, captures, frame ranges, dynamic
protocol fields or replay steps. Inputs are tracked I3/I6 documents and the
offline machine-contract source. Nothing runs, connects or allocates at
runtime, so runtime cleanup is not applicable.

## Goals / Non-Goals

**Goals:**

- Decide whether exact I4 may be the conditionally eligible bounded
  simplification after the repeated defect signal.
- Bind only exact I4 id/path, private seam, production ceiling, closed
  authority flag and hostile verification floor.
- Prepare the exact source data and reciprocal links for one later, separate
  authorization card.
- Leave a deterministic handoff that cannot authorize another payload.

**Non-Goals:**

- Copying, implementing, changing, reviewing, committing or publishing I4.
- Creating the authorization card or editing I4's dependency/reference fields.
- Authorizing new Windows calls, retry/fallback/wait/action behavior, public or
  wire fields, marker derivation, live confirmation, target access or S7.
- Running Windows, 1C, live, endpoint, target, SSH or historical-user operations.
- Raising the global 300/500 ChangeRail limits or granting a reusable waiver.

## Decisions

### 1. Exact I4 is the only conditionally eligible bounded successor

The decision selects the existing successor
`oss-06-s4-r1-i4-classify-hidden-desktop-inventory-refusal-cause`, with
authorization-time path
`openspec/board/3.inprogress/oss-06-s4-r1-i4-classify-hidden-desktop-inventory-refusal-cause.md`.
It is eligible only if a later authorization/composition session proves that
the exact payload projects existing terminal branches into one closed private
cause at two already-published I6 fences, preserves runtime results and call
counts, and adds no new operation or authority.

The alternative of marking `Repeated defect class: no` is rejected: that would
erase the true delivery lineage instead of satisfying the guard. A runtime
redesign is not selected while the published I3/I6 shape remains provable by a
future hostile matrix; redesign becomes mandatory if exact I4 cannot prove that
invariant or the at-most-five-path ceiling.

### 2. Use the minimum machine ceiling and keep authority closed

The future authorization uses `production_loc_ceiling: 301`, the minimum value
accepted by the machine contract. This is a conditional authorization
envelope, not a certification of current size or permission to expand I4. A
later fresh session must measure the exact payload at no more than 301 and no
product change is allowed while composing the graph.

`allow_new_authority_or_wire_protocol` is `false`. The classifier is private,
retains only a closed cause code, and must not add a route, wire field, public
marker or Windows action. A higher ceiling or `true` flag would grant unused
authority and is rejected.

### 3. Prepare one exact non-reusable authorization object

After this investigation is reviewed and published in `4.done`, the only
eligible next card is
`oss-06-s4-r1-i8-authorize-private-inventory-classifier-payload`. Its future
`Investigation authorization` field must be exactly:

```json
{"investigation_card":"openspec/board/4.done/oss-06-s4-r1-i7-investigate-private-inventory-classifier-contract.md","investigation_id":"oss-06-s4-r1-i7-investigate-private-inventory-classifier-contract","successor_card":"openspec/board/3.inprogress/oss-06-s4-r1-i4-classify-hidden-desktop-inventory-refusal-cause.md","successor_id":"oss-06-s4-r1-i4-classify-hidden-desktop-inventory-refusal-cause","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}
```

That authorization card must have exact `Depends On` relation
`oss-06-s4-r1-i7-investigate-private-inventory-classifier-contract`. It remains
a separate docs/OpenSpec-only delivery and does not exist in this change.

Only after that card is published may I4 add exact `Depends On` relation to
this investigation and the following review reference:

```json
{"authorization_card":"openspec/board/4.done/oss-06-s4-r1-i8-authorize-private-inventory-classifier-payload.md","authorization_id":"oss-06-s4-r1-i8-authorize-private-inventory-classifier-payload"}
```

The exact ids/paths and reciprocal relations prevent reuse by another card.

### 4. Require I4's future verification floor

The later authorization cannot substitute for I4 acceptance. Resume requires
the identical 15-row hostile RED/GREEN matrix, cause/privacy/exclusivity
checks, unchanged inventory/fence/admission/action counts, focused and full Go
tests/vet, Linux repository tests, deterministic amd64/386 Windows cross-builds
without execution, strict OpenSpec, explicit five-path scope, privacy and
untracked-aware whitespace checks.

Before composition, a fresh session must establish the exact at-most-five
product/test path set, blob identities and all required test outcomes; after
metadata edits it must prove those blobs unchanged. If I4 changes product scope
or behavior, exceeds five paths or the 301 ceiling, adds authority/wire
protocol, or needs live evidence, this decision no longer applies and a new
split/investigation is required.

## Risks / Trade-offs

- [The investigation is mistaken for authorization] -> Keep I4's reference
  absent and require the separate I8 published source before resume.
- [The numeric ceiling is mistaken for size certification] -> Choose minimum
  valid 301, require a fresh exact measurement and prohibit product/test blob
  changes during graph composition.
- [The exception is reused] -> Bind exact investigation and successor paths/ids
  plus all reciprocal relations checked by preflight.
- [Prose drifts from the executable contract] -> Preserve the exact six-field
  object and two-field reference emitted from current parser requirements.
- [Runtime claims exceed offline evidence] -> Make no Windows causal claim and
  grant no live or external authority.

## Migration Plan

1. Publish this docs/OpenSpec-only investigation in `4.done`.
2. In a fresh delivery session, create and publish only the exact I8
   authorization card with the prepared object and `Depends On` relation.
3. Before updating I4 metadata, establish its exact path/LOC/blob identities
   and run the complete hostile/offline floor; then add the dependency and I8
   reference, prove product/test blobs unchanged, and resume at deterministic
   preflight and fresh independent review.
4. Publish I4 only after a fresh valid GO verdict.

Rollback of this investigation removes no runtime behavior. Before I8 exists,
I4 remains safely blocked. After publication, any mismatch or missing tracked
artifact makes preflight fail closed.

## Open Questions

None. The next authorization card and its exact machine data are intentionally
separate from this decision.
