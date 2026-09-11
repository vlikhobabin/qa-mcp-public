# Authorize Bounded Operation Evidence Boundary Payload

## Status
4.done

## Owner
unassigned

## Series
oss-04d-a1

## Order Index
4034.78

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-04-bind-testclient-to-declared-project-runtime-target.md`

## Review
- Risk tier: `ordinary`
- Milestone audit: `no`
- New authority or wire protocol: `no`
- Credential or mutation authority: `no`
- Repeated defect class: `no`
- Live admission: `no`
- Final certification: `no`
- Published investigation authorization: `none`

## Authorization
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/oss-04d-r2-investigate-operation-evidence-sanitization-boundary.md","investigation_id":"oss-04d-r2-investigate-operation-evidence-sanitization-boundary","successor_card":"openspec/board/3.inprogress/oss-04d-r3-implement-typed-operation-evidence-boundary.md","successor_id":"oss-04d-r3-implement-typed-operation-evidence-boundary","production_loc_ceiling":500,"allow_new_authority_or_wire_protocol":false}`

## Goal
Publish one exact bounded authorization source for the typed operation-evidence
implementation successor after OSS-04D-R2 is independently reviewed and done.

## Acceptance
- The authorization is reciprocally bound to the completed OSS-04D-R2
  investigation and exactly one named OSS-04D-R3 successor.
- The production ceiling is `500`; new authority and wire protocol are false.
- The authorization payload changes no production code and cannot authorize
  another card, another capability or an unreviewed failed stash.
- Strict OpenSpec, exact relation/fingerprint checks and independent review pass.

## Scope
- Exact authorization card, OpenSpec artifacts and roadmap metadata only.
- No operation-identity implementation and no failed-stash restoration.

## Change Set
1. `authorize-bounded-qa-mcp-operation-evidence-boundary-payload` -
   `openspec/changes/authorize-bounded-qa-mcp-operation-evidence-boundary-payload/`

## Depends On
- [OSS-04D-R2](../4.done/oss-04d-r2-investigate-operation-evidence-sanitization-boundary.md)
  is published.
- `oss-04d-r2-investigate-operation-evidence-sanitization-boundary`

## Verify
- Canonical authorization JSON/relation audit: passed (`6` exact fields, `4`
  reciprocal relations, ceiling `500`, authority/wire flag `false`).
- Isolated finalized candidate: exact R3 source returned `valid`; mismatched
  authorization id returned `invalid`; temporary worktree cleanup passed.
- Evidence index:
  `.runtime/changerail/evidence/oss-04d-a1-authorize-bounded-operation-evidence-boundary-payload/index.json`.
- `bin/openspec validate qa-mcp-operation-evidence-boundary-authorization --strict`:
  passed.
- `bin/openspec validate --all --strict`: `33 passed, 0 failed` before archive.
- `git diff --check`: passed.
- Windows-native, live 1C and test-first runtime verification: not applicable;
  the payload changes metadata only and performed no external action.
- Fresh independent ChangeRail review cycle 1: `GO`, `4/4` acceptance,
  `0` findings and `0` unbacked claims; exact tree/fingerprint freshness passed.

## Result
One closed ChangeRail authorization object now binds published OSS-04D-R2 to
exactly one OSS-04D-R3 successor, with a `500` production-LOC ceiling and no
new authority or wire protocol. R2 `Blocks`, A1 `Depends On`, and R3
`Depends On` relations are machine-readable. The reviewed payload retained an
unset R3 reference until deterministic publish finalization moved A1 to
`4.done`; finalization now binds R3 to this exact tracked source. An isolated
committed candidate proved that the exact relation is accepted and a
mismatched source is rejected. The
authorization capability is synced and the change is archived at
`openspec/changes/archive/2026-08-25-authorize-bounded-qa-mcp-operation-evidence-boundary-payload/`.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-bounded-qa-mcp-operation-evidence-boundary-payload`

### Why
Repeated-defect and complexity policy requires a separate published source,
not an implicit allowance inside the investigation or implementation card.

### Goal
Authorize only the bounded OSS-04D-R3 payload described above.

### Scope
- Materialize and validate the exact authorization relationship.
- No implementation, runtime proof or capability expansion.

### Acceptance
- The completed source is machine-readable by deterministic preflight.
- Any id, path, ceiling or authority mismatch fails closed.

### Depends On
- `oss-04d-r2-investigate-operation-evidence-sanitization-boundary`

### Related
- `openspec/changes/authorize-bounded-qa-mcp-operation-evidence-boundary-payload/`

## Log
- 2026-08-25 created by OSS-04D-R2 as the required exact authorization source.
- 2026-08-25 fast-forward created one authorization-only apply-ready change
  with exact reciprocal relations, candidate preflight proof and no-runtime
  verification requirements.
- 2026-08-25 delivery materialized the exact six-field source and reciprocal
  chain, proved exact acceptance plus mismatched rejection in an isolated
  finalized candidate, synced the capability and archived the change. No
  runtime or external action was performed.
- 2026-08-25T16:59:05Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
- 2026-08-25 successor board-path metadata advanced from `2.todo` to
  `3.inprogress`; authorization id, ceiling and capability scope are unchanged.
