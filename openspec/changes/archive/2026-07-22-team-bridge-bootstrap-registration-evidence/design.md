## Context

Root onboarding needs evidence that redeemed identity survives registration, heartbeat, restart and refresh. The component is one owning slice of the root ai for 1c team workstation onboarding roadmap.

## Goals / Non-Goals

**Goals:**
- extend bridge lifecycle smoke/evidence to prove bootstrap redemption, protected refresh, per-user/project attribution, restart recovery and exact process cleanup.
- Verify component preflight, Windows host registration/heartbeat/restart/refresh and cleanup smoke with redacted evidence.

**Non-Goals:**
- Implementing the root team-server exchange or release publisher in this repository.
- Storing or printing long-lived infrastructure secrets.

## Decisions

1. Consume a versioned root contract and validate user/project/server binding before use.
2. Keep secrets in protected local references/overlays and tracked manifests secret-free.
3. Preserve existing advanced compatibility without making it the member happy path.
4. Pin cross-repository contract versions and fail closed on unsupported versions.

## Risks / Trade-offs

- **Contract drift** -> schema version and pinned integration fixtures.
- **Secret leakage** -> permission checks, redaction tests and capture exclusion.
- **Runtime/process leak** -> component preflight, exact process ownership and cleanup proof.

## Migration Plan

Land offline contract/negative tests first, then component behavior and consumer smoke. Root integration pins the reviewed component commit. Disable the new path and retain explicit advanced mode if runtime health fails.

## Open Questions

None before apply; the root contract must be available at the declared dependency version.
