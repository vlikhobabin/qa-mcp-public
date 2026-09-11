## Context

OSS-05-I1 is published in `4.done` and blocks exactly the current OSS-05 card.
It permits public bridge API major `1`, a minimum ChangeRail machine ceiling of
`301` and no surface beyond the archived capability/lifecycle/display contract.
OSS-05 remains capped at `300` added production LOC.

This payload only materializes the source object and reciprocal relations that
the shared preflight parser consumes. It changes no runtime behavior and makes
no Windows or live 1C claim.

## Goals / Non-Goals

**Goals:**

- publish exactly one closed six-field source object;
- bind tracked OSS-05-I1 to exact current OSS-05 id/path;
- preserve ceiling `301`, successor gate `300` and API v1-only wire permission;
- prove exact acceptance and mismatch rejection;
- prevent reuse by another card or API surface.

**Non-Goals:**

- modify the OSS-05 implementation or evidence;
- raise its production gate above `300`;
- authorize COM, BSL, agent CLI, Team/onboarding or generic execution;
- authorize OSS-06 or another successor;
- perform runtime or external actions.

## Decisions

### 1. Use the canonical closed object

The authorization card SHALL expose exactly:

- `investigation_card` and `investigation_id` for tracked OSS-05-I1;
- `successor_card` and `successor_id` for current OSS-05;
- `production_loc_ceiling: 301`;
- `allow_new_authority_or_wire_protocol: true`.

No aliases, extensions or alternate paths are permitted.

### 2. Make relations reciprocal

OSS-05-I1 and this source SHALL block OSS-05. This source SHALL depend on
OSS-05-I1. OSS-05 SHALL depend on both cards and reference the tracked future
`4.done` authorization card through its two-field published-source object.

### 3. Keep machine and delivery ceilings separate

The shared parser requires a value above its ordinary `300` threshold, so the
source uses the minimum `301`. OSS-05 still MUST satisfy its independent
`<=300` production LOC acceptance; this source does not authorize another line.

### 4. Validate the finalized state

Before push, an isolated finalized candidate SHALL show exact OSS-05 source
acceptance and a changed successor id SHALL fail closed. Retained evidence is
bounded and secret-free.

## Risks / Trade-offs

- [Risk] Future `4.done` path is reviewed before publication. → Review exact
  finalization metadata and prove the finalized candidate before push.
- [Risk] `301` is read as implementation budget. → Repeat the independent
  `300` gate in source, successor and spec.
- [Risk] Source is reused. → Exact id/path/state and mismatch rejection are
  mandatory.

## Migration Plan

1. Review the source object and reciprocal OSS-05 metadata.
2. Finalize this card to its exact `4.done` path in the scoped publish commit.
3. Run OSS-05 deterministic preflight against the tracked published source.
4. Continue OSS-05 critical review only after exact validation.

Rollback removes only authorization metadata, returning OSS-05 to fail-closed
`investigation-required` state.

## Open Questions

- None. Any broader successor or API needs a new investigation.
