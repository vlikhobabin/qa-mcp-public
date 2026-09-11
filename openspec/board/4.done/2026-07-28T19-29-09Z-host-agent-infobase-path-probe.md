# Host-agent file infobase path probe

## Status
4.done

## Owner
qa-mcp host-agent

## OpenSpec Stage
archived

## Source
- Root coordination card: `../openspec/board/1.backlog/s20-live-admin-bridge-040-live-mcp-windows-path-existence-via-host-agent.md`

## Summary
Live MCP needs a narrow authenticated host-side way to verify that a configured
Windows file infobase path exists and contains its expected marker file. The
host-agent should answer only marker status for the requested configured path,
without becoming a filesystem browser.

## Acceptance
- Authenticated callers can probe one supplied file infobase directory and get
  `host_path_exists`, `database_file_exists`, and a sanitized failure reason.
- The endpoint never returns directory listings, raw file contents, or customer
  data.
- Missing or invalid tokens are rejected before request validation or path
  probing.

## Change Set
- `host-agent-infobase-path-probe`

## Change 1: `host-agent-infobase-path-probe`

### Why
Containerized providers cannot reliably stat Windows host paths; the existing
host-agent is the authenticated host-side trust boundary.

### Goal
Add a marker-only host-agent endpoint for configured file infobase paths.

### Acceptance
- `POST /path/infobase` accepts a bounded JSON request with `path` and optional
  `marker`.
- The response includes only boolean marker state, a diagnostic code, and
  marker filename metadata.
- The handler rejects empty paths, NUL bytes, absolute file requests, and marker
  names containing path separators before touching the filesystem.
- Existing host-agent auth, origin, and failed-auth limiter behavior protects
  the endpoint.

### Depends On
- none

### Related
- `openspec/changes/host-agent-infobase-path-probe/`

## Verify
- RED before implementation:
  `go test -run 'TestInfobasePathProbe' ./...` in
  `host-agent/windows-display-agent` failed with expected `404 page not found`
  for `/path/infobase`.
- Focused GREEN:
  `go test -run 'TestInfobasePathProbe' ./...` in
  `host-agent/windows-display-agent` -> passed.
- Full host-agent GREEN:
  `go test ./...` in `host-agent/windows-display-agent` -> passed.
- Windows endpoint evidence:
  cross-built the current host-agent tree, copied it to
  `historical-user@192.0.2.205`, confirmed host `HISTORICAL-LAB-HOST`, ran it on loopback
  with a temporary token file, and retained
  `.runtime/changerail/evidence/host-agent-path-demo10413-20260728T205000Z.json`.
  The probe confirmed `C:\1C_BASES\demo10413\1Cv8.1CD` exists,
  missing paths return `failure_reason: "host_path_missing"`, unauthenticated
  requests return `401 auth-failed`, invalid marker requests return
  `400 invalid-marker`, and all response bodies omit the submitted path.
- OpenSpec:
  `openspec validate host-agent-infobase-path-probe --strict` -> passed;
  `openspec validate qa-mcp-windows-host-agent-security --strict` -> passed;
  `openspec validate --all --strict` -> 17 passed, 0 failed.
- Whitespace: `git diff --check` -> passed.

## Archive
- `openspec/changes/archive/2026-07-28-host-agent-infobase-path-probe/`

## Related
- Root coordination card:
  `../openspec/board/1.backlog/s20-live-admin-bridge-040-live-mcp-windows-path-existence-via-host-agent.md`
- Delivery manifest:
  `.runtime/changerail/delivery-manifests/2026-07-28T19-29-09Z-host-agent-infobase-path-probe.json`

## Result
Implemented the authenticated marker-only `POST /path/infobase` endpoint,
documented it, synced specs, verified, archived the OpenSpec change, passed a
fresh independent `GO` review, and published locally with `--no-push`.

Commit: this local publish commit (`feat(host-agent): add file infobase path probe`).
Push: skipped by operator request (`--no-push`).

## Next
- none

## Log
- 2026-07-28T19:29:09Z card created from root coordination story.
- 2026-07-28T19:36:00Z implemented host-agent path probe, recorded RED/GREEN
  Go tests, synced `qa-mcp-windows-host-agent-security`, validated OpenSpec,
  and archived `host-agent-infobase-path-probe`.
- 2026-07-28T19:58:44Z retained Windows host-agent endpoint evidence against
  `HISTORICAL-LAB-HOST` after review cycle 1 returned `NO-GO` for missing
  Windows-native proof.
- 2026-07-28T20:00:00Z fresh independent review returned `GO`; published
  locally without push.
