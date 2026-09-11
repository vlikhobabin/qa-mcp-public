# Make qa-mcp standalone HTTP runtime independent

## Status
4.done

## Owner
unassigned

## Series
oss-03

## Order Index
402

## OpenSpec Stage
archived

## Parent Epic
- `openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md`

## Summary
Replace the private suite base/proxy delivery with a self-contained public
Docker runtime that serves qa-mcp directly over authenticated Streamable HTTP.

## Acceptance
- A clean public checkout builds from public pinned inputs without
  `ai-suite-base`, `ai-mcp-proxy`, private package sources or build secrets.
- The image starts without a bundled-data key, license key or release-portal
  credential and exposes the documented health and MCP endpoints.
- Non-loopback serving fails closed without authentication; authorized and
  unauthorized calls are covered by focused tests.
- The runtime uses a non-root user and documented Windows Docker Desktop and
  Linux Compose examples.
- No private AI for 1C environment or endpoint is part of the standalone
  runtime contract.

## Change Set
1. `make-qa-mcp-standalone-http-runtime-independent` -
   `openspec/changes/make-qa-mcp-standalone-http-runtime-independent/`

## Change 1: `make-qa-mcp-standalone-http-runtime-independent`

### Why
The published OSS-02 baseline now ships one readable, manifest-bound package,
but its container still inherits the suite base and delegates HTTP/authentication
to `ai-mcp-proxy`.

### Goal
Make that same verified open package directly runnable as an authenticated,
self-contained public HTTP container without weakening the OSS-02 integrity
and provenance gates.

### Scope
- Add the project-owned Bearer boundary for `/mcp` and a bounded public
  `/health` liveness route.
- Replace the suite image/proxy with an immutable public Python runtime and the
  direct qa-mcp entrypoint.
- Preserve the exact open-package inventory, component-manifest and archive
  verification introduced by OSS-02.
- Update Compose, release workflows and operator documentation for the public
  standalone contract.
- Prove the container boundary on Linux and Windows; final extraction and
  qualification of the independent Windows bridge remains owned by OSS-05.

### Acceptance
- Same as the card Acceptance section and the refreshed delta specifications.
- The change does not claim or implement the OSS-05 bridge capability and does
  not change TestClient protocol mappings.

### Depends On
- `openspec/board/4.done/oss-01-establish-qa-mcp-shared-core-boundary.md`
- `openspec/board/4.done/oss-02-retire-qa-mcp-protected-delivery-stack.md`

### Related
- `openspec/changes/make-qa-mcp-standalone-http-runtime-independent/`

## Dependencies
- `openspec/board/4.done/oss-01-establish-qa-mcp-shared-core-boundary.md`
- `openspec/board/4.done/oss-02-retire-qa-mcp-protected-delivery-stack.md`

## Verify
- Focused HTTP, doctor and delivery suite: `214 passed`.
- Exact GitHub CI non-live suite: `955 passed`, total coverage `73.00%`
  (required floor `60%`).
- Windows host-agent Go suite, lock check, Python compilation, POSIX shell
  syntax, Linux Compose rendering and `git diff --check`: passed.
- Linux public-input image smoke: bounded health, unauthenticated `401`,
  authenticated MCP initialization, non-root runtime and exact container
  cleanup passed for image
  `sha256:632412a2bd54258842aa9d0ee68ff78196a1993df62e5244d3b0183d3255988c`.
- Exact 78-file readable-package inventory, component manifest, OCI revision
  and saved archive reconciliation passed; verified archive SHA-256 was
  `de76f2c35e42deac311306a5030d6e47395f3bc0277b80306c8e31b5de45383f`.
- Authoritative Windows Docker Desktop E2E passed on the policy-selected
  architect workstation `HISTORICAL-LAB-HOST\\User` (`192.0.2.203`): direct
  health, unauthenticated `401`, authenticated MCP initialization,
  container-to-host route, an owned TestClient lifecycle against a run-owned
  copy of `DemoSSL`, safe standalone doctor/status read, a bounded
  193,671-byte remote display primitive and cleanup through the public
  lifecycle handle.
- Retained pre/post Windows inventory proves that the run-created container,
  image tag, host-agent process/task, two scoped firewall rules, TestClient,
  SSH tunnel, Docker-start task and staging were removed. All 15 pre-existing
  container IDs and 32 pre-existing image IDs matched exactly before Docker
  Desktop was returned to its original stopped state; the source `DemoSSL`
  file SHA-256, size and timestamp were unchanged.
- Strict OpenSpec validation after spec sync/archive: `24 passed, 0 failed`.
- Sanitized ignored evidence:
  `.runtime/changerail/evidence/oss-03-make-qa-mcp-standalone-http-runtime-independent/`.

## Archive
- `openspec/changes/archive/2026-08-24-make-qa-mcp-standalone-http-runtime-independent/`
- Delta requirements were synchronized into
  `qa-mcp-http-transport-security`,
  `qa-mcp-independent-standalone-runtime` and
  `qa-mcp-suite-container-delivery` before archive.

## Related
- `Dockerfile.thin`
- `src/qa_mcp/mcp_server.py`

## Result
Implemented a project-owned authenticated Streamable HTTP boundary and a
standalone non-root container built from a digest-pinned public Python base.
The image now runs `qa-native-mcp` directly, exposes only bounded `/health`
without credentials, protects `/mcp` with exact Bearer authentication and
preserves the OSS-02 package/provenance gates. Linux and the authoritative
architect-workstation Windows Docker Desktop runtime proof passed without
shipping or claiming the OSS-05 independent Windows bridge.

Reviewed payload finalized through ChangeRail scoped publish; exact payload and published commit ledger is retained in the ignored delivery manifest.

## Next
- done

## Log
- 2026-08-24 child card extracted from the open-source roadmap; its OpenSpec
  change is apply-ready.
- 2026-08-24 targeted fast-forward refreshed the apply-ready change after
  published OSS-01/02: dependencies now point to `4.done`, OSS-02 package and
  provenance gates are preserved, `/health` and `/mcp` exposure are explicit,
  and the final independent Windows bridge remains bounded to OSS-05.
- 2026-08-24 ChangeRail delivery started on `main` with remote push enabled;
  implementation uses the refreshed single change and preserves unrelated
  active OSS-05 artifacts.
- 2026-08-24 implemented the standalone HTTP/authentication, image, Compose,
  bootstrap, doctor and release gates; focused and full non-live suites passed.
- 2026-08-24 Linux public-input and Windows Docker Desktop E2E passed with
  source/image/bridge identity and exact owned cleanup retained in sanitized
  ignored evidence; no raw screenshot, credential, token or archive was kept.
- 2026-08-24 synchronized the verified delta requirements, archived the change
  and passed strict validation of all 24 remaining OpenSpec objects.
- 2026-08-24 independent review cycle 1 returned `NO-GO`: its two blockers
  rejected the initial Windows proof because it ran on the COM-lab host and
  lacked retained pre-run ownership identity for cleanup.
- 2026-08-24 rescue attempt 1 reran the proof on
  `HISTORICAL-LAB-HOST\\User`, retained exact pre/post process, task, listener,
  container, image and source-infobase identity, used only a run-owned copy of
  `DemoSSL`, cleaned through the public lifecycle handle and restored Docker
  Desktop to its original stopped state without changing any pre-existing
  Docker identity.
- 2026-08-24T17:27:12Z publish finalized card into `4.done`; exact ledger retained in ignored manifest.
