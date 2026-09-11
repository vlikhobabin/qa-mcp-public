## Context

The shared core already owns `TargetIdentity`, but it has no public contract for
provider observations, evidence policy or the ignored profile that later
lifecycle integration needs. The complete prototype is preserved in a
recoverable stash; this change replays only its data-model/schema seam.

## Goals / Non-Goals

**Goals:**
- Add immutable, provider-neutral runtime-target value objects.
- Package a closed schema and keep production additions below 300 lines.

**Non-Goals:**
- Parse the suite handoff or local profile.
- Compose MCP/doctor state or start/attach/clean a TestClient.
- Change protocol frames, captures, templates or runtime lab state.

## Decisions

1. Keep `TargetIdentity` as the canonical logical identity and layer binding,
   observation and profile values around it. A second target hierarchy was
   rejected because it would fork the OSS-01 executor contract.
2. Use frozen dataclasses/enums and a packaged closed JSON schema. Mutable dict
   state was rejected because later application instances must not rebind.
3. Export only completed public types in this payload; parsing and readiness
   arrive in OSS-04B/C so this diff remains independently reviewable.

## Risks / Trade-offs

- [Contract types exist before a resolver] → Tests cover construction and
  schema semantics; no readiness claim is made until OSS-04B.
- [Schema asset omitted from distributions] → Wheel/sdist/archive inventory
  tests fail if the packaged file is absent.

## Migration Plan

Additive public contract only. Rollback removes the exports and schema asset.
No process or runtime cleanup is applicable.

## Open Questions

- None. No protocol capture source, frame range, dynamic field or replay change
  exists in this payload.
