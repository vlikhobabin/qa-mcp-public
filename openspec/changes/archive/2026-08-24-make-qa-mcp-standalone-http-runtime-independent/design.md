## Context

The OSS-02 thin image installs the readable package from frozen dependencies,
checks an exact source/asset inventory and binds saved-image verification to a
component manifest, but it still inherits a suite base and delegates HTTP/auth
to `ai-mcp-proxy`. Direct FastMCP HTTP exists but intentionally refuses unsafe
non-loopback binds because it lacks the same authentication. Docker port
publishing needs an in-container wildcard listener, so independent delivery
must own authentication inside qa-mcp.

Protocol assets and TestClient behavior are unchanged. Windows Docker Desktop
continues to reach the host through `host.docker.internal`; live proof must use
the exact declared target and owned cleanup.

## Goals / Non-Goals

**Goals:**
- Build from public base images and package inputs only.
- Serve authenticated Streamable HTTP MCP and health directly.
- Preserve loopback-safe host publishing and model-B host routing.
- Provide reproducible Compose flows for Windows and Linux.

**Non-Goals:**
- Add public Internet multi-tenancy, OAuth or cloud identity.
- Include the 1C platform or license in the standalone image.
- Implement Runtime Relay/RPW.
- Remove operator authentication or mutation controls.

## Decisions

1. Use a pinned public Python slim base and install the normal wheel/source
   package. Do not inherit suite images or copy private binaries.
2. Wrap the Streamable HTTP ASGI app with project-owned constant-time Bearer
   authentication, retaining the UTF-8 gate. `/mcp` is authenticated before
   dispatch; `/health` remains an unauthenticated bounded liveness response so
   Docker healthchecks need no secret and disclose neither token nor target.
3. Require `QA_MCP_BEARER_TOKEN` for wildcard/non-loopback serving. The former
   unsafe-bind flag cannot bypass authentication. Loopback-only native use
   remains possible; Compose requires an explicit secret without committing a
   default.
4. Standardize container port 8080 and host example 127.0.0.1:8000. The direct
   entrypoint owns `/mcp` and `/health`.
5. Run as a non-root user with a writable `/work` volume. The image carries no
   platform, infobase, qa-mcp license, encryption key or release credentials.
6. Keep model-B host and port defaults, but use only public `QA_MCP_*` names.
7. Preserve the OSS-02 open-package inventory and release sequence: build the
   image, verify installed files, save it, bind the archive digest/source
   revision/tag to the component manifest, then permit publication.

## Risks / Trade-offs

- [Risk] Authentication middleware breaks Streamable HTTP receive/disconnect
  lifecycle. → Reuse ASGI channel tests and add real authorized/unauthorized
  roundtrips.
- [Risk] Docker Desktop host routing differs from Linux Docker. → Retain
  platform-specific Compose E2E and explicit `extra_hosts` where required.
- [Risk] Health checks accidentally require MCP auth or leak state. → Define a
  minimal health response and test both routes independently.
- [Risk] Public base tag drifts. → Pin digest in release builds and update it by
  reviewed dependency PR.

## Migration Plan

1. Add authenticated ASGI composition and focused tests.
2. Convert the thin Dockerfile and direct entrypoint to the public-base
   contract while retaining the OSS-02 verifier.
3. Add clean-build/start/health/auth container tests.
4. Replace Compose and docs, then remove suite-base/proxy runtime wiring.
5. Verify Linux smoke and exact Windows Docker Desktop HTTP/container flow
   against the authorized existing host boundary. Do not claim the final
   independent bridge contract delivered by OSS-05.

Rollback uses the prior private image only before public cutover. Public release
tags are immutable and roll back by selecting the preceding digest.

## Open Questions

- None for the standalone boundary; cloud identity belongs to AI for 1C.
