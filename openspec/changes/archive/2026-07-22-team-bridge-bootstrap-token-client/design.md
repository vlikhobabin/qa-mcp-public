## Context

Manual bridge tokens violate the ordinary-member flow and expose long-lived secrets to prompts. The component is one owning slice of the root ai for 1c team workstation onboarding roadmap.

## Goals / Non-Goals

**Goals:**
- redeem a short-lived server/project/user-bound onboarding grant once and store only protected bridge refresh/registration state while retaining explicit-token advanced compatibility.
- Verify offline parser/exchange/replay/expiry/revoke/permission/redaction tests with redacted evidence.

**Non-Goals:**
- Implementing the root team-server exchange or release publisher in this repository.
- Storing or printing long-lived infrastructure secrets.

## Decisions

1. Consume a versioned root contract and validate user/project/server binding before use.
2. Keep secrets in protected local references/overlays and tracked manifests secret-free.
3. Preserve existing advanced compatibility without making it the member happy path.
4. Pin cross-repository contract versions and fail closed on unsupported versions.
5. Require HTTPS for the onboarding exchange, except for an owned loopback
   tunnel, and reject URL user-info, redirects, queries and fragments.
6. Space grant refreshes against both the registration lease and the root
   contract's eight-active-grant bound, retaining one slot of headroom.
7. Enforce protected-file permissions inside the client on both POSIX and
   Windows, independent of installer enforcement, and preserve the root
   contract's case-insensitive Basic/Bearer/token authorization schemes.

## Risks / Trade-offs

- **Contract drift** -> schema version and pinned integration fixtures.
- **Secret leakage** -> permission checks, redaction tests and capture exclusion.
- **Runtime/process leak** -> component preflight, exact process ownership and cleanup proof.

## Migration Plan

Land offline contract/negative tests first, then component behavior and consumer smoke. Root integration pins the reviewed component commit. Disable the new path and retain explicit advanced mode if runtime health fails.

## Open Questions

None before apply; the root contract must be available at the declared dependency version.
