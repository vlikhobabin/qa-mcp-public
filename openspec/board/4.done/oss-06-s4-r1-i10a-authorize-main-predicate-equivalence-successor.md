# Authorize Main-Predicate Equivalence Successor

## Status
4.done

## Owner
unassigned

## Series
oss-06-s4-r1-i10a

## Order Index
405.101931

## OpenSpec Stage
archived

## Parent Card
- `openspec/board/2.todo/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md`

## Source
- Published I10 decision, after I10 reaches `4.done` unchanged.

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Repeated defect class: `no`
- Credential or mutation authority: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/oss-06-s4-r1-i10-investigate-main-predicate-equivalence-contract.md","investigation_id":"oss-06-s4-r1-i10-investigate-main-predicate-equivalence-contract","successor_card":"openspec/board/3.inprogress/oss-06-s4-r1-i11-enforce-main-predicate-equivalence-contract.md","successor_id":"oss-06-s4-r1-i11-enforce-main-predicate-equivalence-contract","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}`

## Summary
Publish the separate exact machine authorization prepared by I10 for I11.
This card is documentation/OpenSpec-only and cannot certify, implement or
modify I11.

## Acceptance
- Preserve the exact six-field authorization object with no additional,
  missing or changed field.
- Depend on published unchanged I10, whose `Blocks` relation names exact I11.
- Bind only exact I11 at its authorization-time `3.inprogress` path, ceiling
  `301` and authority/wire allowance `false`.
- Add no product/test/runtime behavior, external operation, I11 byte or claim
  that I11 already passes the decision/proof floor.
- Complete fresh independent review and scoped publication in `4.done` before
  I11 may enter its review gate.
- Preserve Apache-2.0 and remain offline with no Windows, PowerShell, 1C,
  endpoint, lab/live/action, S5/S7 or SSH operation.

## Depends On
- `oss-06-s4-r1-i10-investigate-main-predicate-equivalence-contract`

## Blocks
- `oss-06-s4-r1-i11-enforce-main-predicate-equivalence-contract`

## Change Set
1. `authorize-main-predicate-equivalence-successor`

## Verify
- `bin/openspec validate authorize-main-predicate-equivalence-successor
  --strict`, capability strict validation and `bin/openspec validate --all
  --strict` passed pre-archive (`61/61`).
- Exact JSON audit passed with four byte-identical canonical one-line copies of
  I10's machine `authorization_source.payload`, exactly six keys, exact I10/I11
  ids and paths, ceiling `301` and authority/wire flag `false`.
- Exact graph audit confirmed unchanged tracked published I10 blocks exact I11;
  I11 and the S4-R1 parent remain byte-for-byte unchanged in `2.todo`.
- Changed-path inventory proved eight documentation/OpenSpec-only paths, zero
  host-agent product/test paths and zero added production LOC; the approved
  Apache-2.0 declaration surfaces remain unchanged.
- Scoped public-safety/privacy scan, `git diff --check` and explicit
  tracked-plus-untracked trailing-whitespace scan passed.
- Windows-native/test-first/live verification is prohibited and not applicable
  because the payload changes no product/test/runtime behavior.
- Fresh independent ordinary/high review remains required before scoped HTTPS
  publication.

## Archive
- `openspec/changes/archive/2026-09-02-authorize-main-predicate-equivalence-successor/`

## Related
- `docs/protocol-research/evidence/main-predicate-equivalence-contract-2026-09-02/decision.json`
- `openspec/changes/authorize-main-predicate-equivalence-successor/`

## Result
The exact documentation-only authorization capability is synchronized and
archived. It binds only unchanged published I10 to exact I11 at the
declared authorization-time `3.inprogress` path, ceiling `301` and closed
authority/wire flag. It neither implements nor certifies I11; I11 and the S4-R1
parent remain blocked and unchanged. I10a remains in `3.inprogress` for fresh
independent review and scoped publication.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-main-predicate-equivalence-successor`

### Why
ChangeRail requires a separate unchanged tracked `4.done` authorization source
for exact repeated-defect successor I11; I8 is bound to I4 and is not reusable.

### Goal
Publish only I10's exact bounded source object.

### Scope
- This card, one authorization capability and board/OpenSpec metadata only.
- No I11 product/test bytes or runtime/external operation.

### Acceptance
- Exact graph and object are independently reviewable and non-reusable.

### Depends On
- `oss-06-s4-r1-i10-investigate-main-predicate-equivalence-contract`

### Related
- `openspec/changes/authorize-main-predicate-equivalence-successor/`

## Log
- 2026-09-02 prepared by I10 as a separate future delivery; not delivered or
  published by I10.
- 2026-09-02 fast-forwarded one documentation/OpenSpec-only authorization
  change from I10's exact machine decision; no I11, parent, host-agent or
  external surface is included.
- 2026-09-02 synchronized the exact I10-to-I11 authorization capability while
  leaving I11 and the S4-R1 parent byte-for-byte unchanged.
- 2026-09-02 passed pre-archive strict OpenSpec `61/61`, exact four-copy JSON,
  graph, docs-only/zero-production-LOC, public-safety, Apache-2.0 and whitespace
  gates without any external operation; Windows/test-first/live verification
  remained prohibited and not applicable.
- 2026-09-02 archived the fully completed, already-synced authorization change
  with `--skip-specs`; post-archive strict OpenSpec passed `60/60`. I10a remains
  in `3.inprogress` for deterministic preflight and fresh independent review.
- 2026-09-02T02:13:23Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
