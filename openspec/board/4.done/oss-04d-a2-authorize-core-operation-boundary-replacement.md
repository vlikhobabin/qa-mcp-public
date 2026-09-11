# Authorize Core Operation Boundary Replacement

## Status
4.done

## Owner
unassigned

## Series
oss-04d-a2

## Order Index
4034.856

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
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/oss-04d-r4-r1-replace-exhausted-boundary-investigation.md","investigation_id":"oss-04d-r4-r1-replace-exhausted-boundary-investigation","successor_card":"openspec/board/3.inprogress/oss-04d-r5-implement-core-operation-boundary.md","successor_id":"oss-04d-r5-implement-core-operation-boundary","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":false}`

## Goal
Publish the exact one-to-one R5 authorization required by repeated-defect
preflight while preserving R5's stricter 300-line delivery cap.

## Acceptance
- Source is reciprocally bound to published R4-R1 and only R5's future exact
  `3.inprogress` review path.
- Machine ceiling is 301, R5 cap is 300, and new authority/wire is false.
- Metadata-only payload cannot authorize R6, restore a stash or add runtime.
- Exact relation, strict OpenSpec, scope/diff and fresh review pass.

## Scope
- Authorization/OpenSpec/roadmap metadata only; no runtime or external action.

## Change Set
1. `authorize-core-qa-mcp-operation-boundary-replacement` -
   `openspec/changes/authorize-core-qa-mcp-operation-boundary-replacement/`

## Depends On
- `oss-04d-r4-r1-replace-exhausted-boundary-investigation`

## Blocks
- `oss-04d-r5-implement-core-operation-boundary`

## Verify
- Canonical authorization/relation audit: passed (`6` exact fields; published
  R4-R1, A2 and R5 reciprocal references; machine ceiling `301`; R5 cap `300`;
  authority/wire flag `false`).
- Isolated finalized candidates: exact R5 source returned authorization
  `valid`, limit `301` and `stop_required=false` at candidate
  `0215921107afcefc9c14ba3fa226b479f004ec9e`; mismatched authorization id
  returned `invalid`, limit `300` and `stop_required=true` at candidate
  `8d31e9c9a2ec98ad345b4a2fb25dc0c11a5af763`; temporary worktree cleanup
  passed.
- Evidence index:
  `.runtime/changerail/evidence/oss-04d-a2-authorize-core-operation-boundary-replacement/index.json`.
- `bin/openspec validate qa-mcp-core-operation-boundary-authorization --strict`:
  passed.
- `bin/openspec validate --all --strict`: `35 passed, 0 failed` before archive;
  `34 passed, 0 failed` after archive.
- Delivery manifest scope and `git diff --check`: passed.
- Test-first, Windows-native, live 1C and external-action verification: not
  applicable; this payload changes metadata only and performed no external
  action.
- Fresh independent ChangeRail review cycle 1: `GO` (`4/4` acceptance, zero
  findings and zero unbacked claims).

## Result
One closed ChangeRail authorization object binds published R4-R1 to exactly one
future in-progress R5 successor. The machine ceiling is the minimum accepted
`301`, R5 independently remains capped at `300`, and new authority/wire
protocol is false. Exact and mismatched isolated candidate checks proved
fail-closed consumption. The authorization capability is synced and archived
at
`openspec/changes/archive/2026-08-26-authorize-core-qa-mcp-operation-boundary-replacement/`.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- Deliver
  [OSS-04D-R5](../2.todo/oss-04d-r5-implement-core-operation-boundary.md) as
  the next sequential card.

## Change 1: `authorize-core-qa-mcp-operation-boundary-replacement`

### Why
Repeated-defect preflight requires a separately published exact authorization
source even though R5 retains the ordinary 300-line delivery cap.

### Goal
Authorize only the bounded OSS-04D-R5 core operation-boundary payload.

### Scope
- Materialize and validate the exact R4-R1 → A2 → R5 relationship.
- No implementation, runtime proof, stash restoration or capability expansion.

### Acceptance
- The completed source is machine-readable by deterministic preflight.
- Any id, path, ceiling, source state or authority mismatch fails closed.
- The machine ceiling is 301 while R5's delivery cap remains 300.

### Depends On
- `oss-04d-r4-r1-replace-exhausted-boundary-investigation`

### Related
- `openspec/changes/authorize-core-qa-mcp-operation-boundary-replacement/`

## Log
- 2026-08-25 created by R4-R1 with the future exact R5 review path.
- 2026-08-26 fast-forward created one authorization-only apply-ready change
  with the exact R4-R1/A2/R5 relation, a 301 machine ceiling, retained R5 cap
  300 and no runtime or external-action scope.
- 2026-08-26 delivery proved exact authorization acceptance and mismatched
  rejection in isolated committed candidates, synced the authorization
  capability, passed metadata-only gates and prepared the archived payload for
  fresh review.
- 2026-08-26 independent review cycle 1 returned `GO` with `4/4` acceptance,
  zero findings and zero unbacked claims; OSS-04D-R5 is next.
- 2026-08-26T05:23:47Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
