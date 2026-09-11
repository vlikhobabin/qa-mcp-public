# Authorize Standalone Host Bridge API v1

## Status
4.done

## Owner
unassigned

## Series
oss-05-a1

## Order Index
403.99

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

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
- Investigation authorization: `{"investigation_card":"openspec/board/4.done/oss-05-i1-investigate-standalone-host-bridge-api-v1-boundary.md","investigation_id":"oss-05-i1-investigate-standalone-host-bridge-api-v1-boundary","successor_card":"openspec/board/3.inprogress/oss-05-extract-independent-open-windows-host-bridge.md","successor_id":"oss-05-extract-independent-open-windows-host-bridge","production_loc_ceiling":301,"allow_new_authority_or_wire_protocol":true}`

## Goal
Publish the exact closed authorization source that lets deterministic preflight
admit only the existing bounded OSS-05 public bridge API v1 payload.

## Acceptance
- The authorization contains exactly six canonical fields binding published
  OSS-05-I1 to the exact current OSS-05 successor id/path.
- Machine ceiling is the minimum valid `301`; OSS-05 independently retains its
  `<=300` added production LOC gate.
- `allow_new_authority_or_wire_protocol: true` applies only to public bridge API
  major `1` and cannot authorize another successor or broader route family.
- Investigation, authorization and successor relations are reciprocal and any
  id/path/state/field mismatch fails closed.
- The payload is metadata-only; strict OpenSpec, relation/scope/diff and fresh
  independent review pass.

## Scope
- Authorization/OpenSpec/board metadata only; no runtime or external action.

## Change Set
1. `authorize-qa-mcp-standalone-host-bridge-api-v1` -
   `openspec/changes/authorize-qa-mcp-standalone-host-bridge-api-v1/`

## Archive
- `openspec/changes/archive/2026-08-27-authorize-qa-mcp-standalone-host-bridge-api-v1/`

## Depends On
- `oss-05-i1-investigate-standalone-host-bridge-api-v1-boundary`

## Blocks
- `oss-05-extract-independent-open-windows-host-bridge`

## Verify
- Canonical six-field authorization and reciprocal relation audit.
- Exact finalized-candidate acceptance and mismatched-successor rejection.
- Strict change/capability/all OpenSpec validation, manifest scope and diff.
- Test-first, Windows-native and live 1C checks are not applicable to this
  metadata-only source.

## Result
The exact closed six-field OSS-05-I1 → OSS-05 authorization source is complete.
An isolated finalized candidate accepted the exact source with ceiling `301`
and API v1 wire permission, while a changed `successor_id` failed closed as
`investigation-required`. The payload is metadata-only and changes no runtime.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `authorize-qa-mcp-standalone-host-bridge-api-v1`

### Why
Published OSS-05-I1 authorizes one bounded public API v1 successor; ChangeRail
requires a separate exact source object before OSS-05 can enter review.

### Goal
Materialize the closed OSS-05-I1 → OSS-05-A1 → OSS-05 chain.

### Scope
- Exact source object and reciprocal board/OpenSpec metadata.
- No implementation, runtime proof or capability expansion.

### Acceptance
- Exact current OSS-05 preflight accepts the source after publication.
- Any changed field, path, id, source state or successor fails closed.

### Depends On
- `oss-05-i1-investigate-standalone-host-bridge-api-v1-boundary`

### Related
- `openspec/changes/authorize-qa-mcp-standalone-host-bridge-api-v1/`

## Log
- 2026-08-27 created after published investigation commit `abfaff2`; existing
  OSS-05 implementation and `.codex/config.toml` remain preexisting dirty.
- 2026-08-27 canonical object/relation audit and strict OpenSpec `40/40`
  passed. Exact finalized candidate returned valid/ready; mismatched successor
  returned invalid/investigation-required. Sanitized evidence is indexed under
  `.runtime/changerail/evidence/oss-05-a1-authorize-standalone-host-bridge-api-v1/`.
- 2026-08-27 synced the authorization capability and archived the completed
  `6/6` metadata-only change; card remains in `3.inprogress` for review/publish.
- 2026-08-27T10:14:44Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
