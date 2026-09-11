## 1. Own the HTTP security boundary

- [x] 1.1 Add a project-owned Bearer authentication configuration and constant-time ASGI middleware around Streamable HTTP MCP while retaining the UTF-8 gate.
- [x] 1.2 Add authorized, missing-token, wrong-token, bounded public-health and ASGI disconnect-lifecycle tests.
- [x] 1.3 Fail startup for wildcard/non-loopback serving without authentication, ensure the former unsafe-bind flag cannot bypass it and preserve loopback-only native defaults.

## 2. Build an independent image

- [x] 2.1 Replace `ai-suite-base` with a digest-pinned public Python base and install the normal qa-mcp package as a non-root user.
- [x] 2.2 Replace `ai-mcp-proxy` with the direct project entrypoint serving `/mcp` and `/health` on internal port 8080.
- [x] 2.3 Remove private portal, private credential and AI for 1C runtime environment names from the image and entrypoint.
- [x] 2.4 Preserve model-B TestClient defaults and public bridge routing without embedding the 1C platform, infobase or license.
- [x] 2.5 Preserve OSS-02 installed inventory, component-manifest, OCI revision, image-tag and saved-archive digest verification before publication.

## 3. Normalize standalone operation

- [x] 3.1 Replace Windows Docker Desktop and Linux Compose/examples with loopback host publishing, explicit token generation and consistent port mapping.
- [x] 3.2 Update doctor/health output to report only public standalone route and capability checks with no platform/COM worker dependency.
- [x] 3.3 Add clean-checkout Docker build, non-root, health, authenticated MCP initialization and source/asset smoke tests.

## 4. Verify cross-platform delivery

- [x] 4.1 Run the full non-live Python suite, HTTP security tests, container contract tests and strict OpenSpec validation.
- [x] 4.2 Run a Linux container start/authentication smoke from public inputs only.
- [x] 4.3 Run Windows Docker Desktop E2E against the authorized host: direct HTTP health/authentication, existing host-boundary reachability, safe TestClient status/read, bounded display and exact owned cleanup; do not claim OSS-05 bridge delivery.
- [x] 4.4 Retain image digest, bridge identity and target-bound evidence without raw customer/runtime data.
