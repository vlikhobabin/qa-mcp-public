# Authorize Positive Core Operation Boundary

## Status
4.done

## Owner
unassigned

## Series
oss-04d-a4

## Order Index
4034.866

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
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/oss-04d-r5-r2-resolve-positive-result-mismatch-outcome.md","investigation_id":"oss-04d-r5-r2-resolve-positive-result-mismatch-outcome","successor_card":"openspec/board/3.inprogress/oss-04d-r7-implement-positive-core-operation-boundary.md","successor_id":"oss-04d-r7-implement-positive-core-operation-boundary","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}`

## Goal
Publish the exact one-to-one R7 authorization after R5-R2, preserving R7's
stricter 300-line cap.

## Acceptance
- Source binds only published R5-R2 to R7's future exact `3.inprogress` path.
- Machine ceiling is 301, R7 cap 300, new authority/wire false.
- Metadata-only payload cannot authorize R5, R5-R1, integration or lifecycle.
- Exact relation, strict OpenSpec, scope/diff and fresh review pass.

## Scope
- Authorization/OpenSpec/roadmap metadata only; no runtime or external action.

## Change Set
1. `authorize-positive-qa-mcp-core-operation-boundary` -
   `openspec/changes/authorize-positive-qa-mcp-core-operation-boundary/`

## Depends On
- `oss-04d-r5-r2-resolve-positive-result-mismatch-outcome`

## Blocks
- `oss-04d-r7-implement-positive-core-operation-boundary`

## Verify
- Exact six-field source and reciprocal R5-R2/A4/R7 relation audit: passed;
  integer ceiling `301`, R7 cap `300`, authority/wire flag `false`.
- Non-reuse audit: passed; A4 cannot authorize A2, R5, R5-R1, A5, R8 or
  OSS-04E.
- Isolated finalized-candidate preflight: exact R7 relation reported `valid`;
  bounded mismatched authorization id reported `invalid` and did not inherit
  the authorization.
- Evidence index:
  `.runtime/changerail/evidence/oss-04d-a4-authorize-positive-core-operation-boundary/index.json`.
- Strict OpenSpec, design-only manifest scope and `git diff --check`: passed;
  the new capability is synced and its change archived.
- Test-first, Windows/live/runtime/protocol/external proof: not applicable to
  this metadata-only authorization.
- Fresh independent review before publish.

## Result
The exact one-to-one R5-R2 → A4 → R7 authorization is materialized with the
machine ceiling `301`, R7's stricter runtime cap `300` and no authority or wire
expansion. An isolated post-finalization candidate admits the exact R7
reference and rejects a mismatched successor. The authorization capability is
synced and archived at
`openspec/changes/archive/2026-08-26-authorize-positive-qa-mcp-core-operation-boundary/`.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-positive-qa-mcp-core-operation-boundary`

### Why
R7 requires one exact published authorization source; historical A2 is bound
to exhausted R5 and cannot be reused.

### Goal
Publish the reciprocal R5-R2 → A4 → R7 authorization at machine ceiling 301
without changing R7's hard 300-line cap or adding authority/wire protocol.

### Scope
- Authorization OpenSpec and board metadata only.
- No runtime implementation or external action.

### Acceptance
- Exact six-field source and reciprocal relations are independently auditable.
- Finalized exact candidate passes and mismatched successor rejects.
- Strict OpenSpec and design-only scope pass.

### Depends On
- Published R5-R2.

### Related
- `openspec/changes/authorize-positive-qa-mcp-core-operation-boundary/`

## Log
- 2026-08-26 recreated by R5-R2 with the future exact R7 review path.
- 2026-08-26 fast-forward produced one apply-ready metadata-only authorization
  change with exact candidate/mismatch proof requirements.
- 2026-08-26 moved to `3.inprogress`; started metadata-only delivery.
- 2026-08-26 retained the exact relation/non-reuse audit and isolated
  finalized-candidate proof: exact R7 was valid, while a bounded authorization
  mismatch was invalid; synced the capability and archived the change for
  fresh review.
- 2026-08-26T08:55:00Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
