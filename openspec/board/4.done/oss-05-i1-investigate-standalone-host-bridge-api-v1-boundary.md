# Investigate Standalone Host Bridge API v1 Boundary

## Status
4.done

## Owner
unassigned

## Series
oss-05-i1

## Order Index
403.98

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

## Goal
Publish the exact bounded investigation decision needed to authorize only the
already implemented OSS-05 standalone Windows host bridge API v1 payload.

## Acceptance
- The decision names only OSS-05 at its exact `3.inprogress` path and records
  public API major `1` as the bounded new wire contract.
- The allowed surface is limited to authenticated capability negotiation,
  TestClient lifecycle/relay and bounded display/UIA operations already in the
  archived OSS-05 change.
- The decision permits `allow_new_authority_or_wire_protocol: true` only for
  this successor and keeps its production gate at `300` added LOC; the
  ChangeRail machine ceiling is the minimum valid `301`.
- The payload is metadata-only and cannot authorize COM, BSL, agent CLI,
  Team/onboarding, generic execution, another successor or OSS-06.
- Strict OpenSpec, exact relation, scope/diff and fresh independent review pass.

## Scope
- Investigation/OpenSpec/board metadata only; no runtime, Windows or external
  action.

## Change Set
1. `investigate-qa-mcp-standalone-host-bridge-api-v1-boundary` -
   `openspec/changes/investigate-qa-mcp-standalone-host-bridge-api-v1-boundary/`

## Archive
- `openspec/changes/archive/2026-08-27-investigate-qa-mcp-standalone-host-bridge-api-v1-boundary/`

## Depends On
- `oss-01-establish-qa-mcp-shared-core-boundary`

## Blocks
- `oss-05-extract-independent-open-windows-host-bridge`

## Verify
- Exact successor/path/API-major/ceiling/authority decision audit.
- Strict change/capability/all OpenSpec validation.
- Delivery manifest scope and `git diff --check`.
- Test-first, Windows-native and live 1C checks are not applicable to this
  metadata-only investigation.

## Result
The exact OSS-05 API v1 investigation decision is complete: one canonical
successor, machine ceiling `301`, independent OSS-05 cap `300`, and wire flag
`true` limited to the archived standalone capability/lifecycle/display
surface. The payload changes only OpenSpec/board metadata and performs no
runtime or external action.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Change 1: `investigate-qa-mcp-standalone-host-bridge-api-v1-boundary`

### Why
ChangeRail preflight correctly classifies the versioned public bridge API v1
as a new wire contract and requires a separately published investigation.

### Goal
Constrain the authorization decision to the existing bounded OSS-05 payload.

### Scope
- Exact successor, API, route family, LOC and non-goal decision metadata.
- No implementation or runtime evidence changes.

### Acceptance
- The decision is machine-readable, exact and fail-closed.
- It cannot be reused for another card or a broader authority surface.

### Depends On
- `oss-01-establish-qa-mcp-shared-core-boundary`

### Related
- `openspec/changes/investigate-qa-mcp-standalone-host-bridge-api-v1-boundary/`

## Log
- 2026-08-27 created after OSS-05 deterministic preflight returned
  `investigation-required`; the operator authorized the bounded prerequisite
  chain. Existing OSS-05 implementation remains excluded as preexisting dirty.
- 2026-08-27 exact relation/decision audit passed; strict change validation and
  all OpenSpec validation passed `39/39`, with `git diff --check` clean.
- 2026-08-27 synced the investigation capability and archived the completed
  `6/6` metadata-only change; card remains in `3.inprogress` for review/publish.
- 2026-08-27T09:32:56Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
