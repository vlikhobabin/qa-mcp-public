# Authorize Positive Operation Boundary Integration

## Status
4.done

## Owner
unassigned

## Series
oss-04d-a5

## Order Index
4034.868

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
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/oss-04d-r5-r2-resolve-positive-result-mismatch-outcome.md","investigation_id":"oss-04d-r5-r2-resolve-positive-result-mismatch-outcome","successor_card":"openspec/board/3.inprogress/oss-04d-r8-integrate-positive-operation-boundary-public-paths.md","successor_id":"oss-04d-r8-integrate-positive-operation-boundary-public-paths","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}`

## Goal
Authorize only R8 after reviewed R7, preserving the exact positive-result
contract and stricter 300-line integration cap.

## Acceptance
- Source binds only published R5-R2 to R8's future exact `3.inprogress` path
  after R7 publishes.
- Machine ceiling is 301, R8 cap 300, new authority/wire false.
- Metadata-only payload cannot authorize R5/R6, lifecycle or failed stashes.
- Exact relation, strict OpenSpec, scope/diff and fresh review pass.

## Scope
- Authorization/OpenSpec/roadmap metadata only; no runtime or external action.

## Change Set
1. `authorize-positive-qa-mcp-operation-boundary-integration` -
   `openspec/changes/archive/2026-08-26-authorize-positive-qa-mcp-operation-boundary-integration/`

## Depends On
- `oss-04d-r5-r2-resolve-positive-result-mismatch-outcome`
- `oss-04d-r7-implement-positive-core-operation-boundary`

## Blocks
- `oss-04d-r8-integrate-positive-operation-boundary-public-paths`

## Verify
- Exact closed six-field source and reciprocal R5-R2/R7/A5/R8 relation audit:
  passed; integer ceiling `301`, R8 cap `300`, authority/wire flag `false`.
- Non-reuse audit: passed for historical A2/A3/A4, exhausted R5/R6 and
  OSS-04E; only exact R8 is named by the authorization object.
- Isolated finalized-candidate preflight: exact R8 relation reported `valid`;
  bounded authorization-reference and successor-source mismatches each
  reported `invalid` and inherited no authorization.
- Evidence index:
  `.runtime/changerail/evidence/oss-04d-a5-authorize-positive-operation-boundary-integration/index.json`.
- Strict OpenSpec, metadata-only manifest scope and `git diff --check`: passed;
  the new capability is synced and its change archived.
- Test-first, Windows/live/runtime/protocol/external proof: not applicable to
  this metadata-only authorization.
- Fresh independent review cycle 1: `GO`; all 4 acceptance criteria passed,
  with no findings and no unbacked claims.

## Result
The exact one-to-one R5-R2/R7 → A5 → R8 authorization is materialized with
machine ceiling `301`, R8's stricter runtime cap `300` and no authority or wire
expansion. An isolated post-finalization candidate admits exact R8 and rejects
both a mismatched A5 reference and a mismatched successor source. The new
authorization capability is synced and archived.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-positive-qa-mcp-operation-boundary-integration`

### Why
R8 needs one exact published authorization source; historical A2/A3/A4 bind
other successors and cannot be reused.

### Goal
Publish the reciprocal R5-R2/R7 → A5 → R8 authorization at machine ceiling
301 without changing R8's hard 300-line cap or adding authority/wire protocol.

### Scope
- Authorization OpenSpec and board metadata only.
- No runtime implementation or external action.

### Acceptance
- Exact six-field source and reciprocal R5-R2/R7/A5/R8 relations are
  independently auditable.
- Finalized exact candidate passes and bounded source/successor mismatches
  reject.
- Strict OpenSpec and metadata-only scope pass.

### Depends On
- Published R5-R2 and R7.

### Related
- `openspec/changes/archive/2026-08-26-authorize-positive-qa-mcp-operation-boundary-integration/`

## Log
- 2026-08-26 recreated by R5-R2 with the future exact R8 review path.
- 2026-08-26 fast-forward produced one apply-ready metadata-only authorization
  change with exact candidate and mismatch proof requirements.
- 2026-08-26 moved to `3.inprogress`; started metadata-only delivery.
- 2026-08-26 retained exact relation/non-reuse and isolated finalized-candidate
  proofs: exact R8 was valid while reference/source mismatches were invalid;
  synced the capability and archived the change for fresh review.
- 2026-08-26 independent review cycle 1 returned `GO`: 4/4 acceptance passed,
  no blocker/major/minor findings and no unbacked claims.
- 2026-08-26T12:43:37Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
