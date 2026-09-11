# S50-160: Non-consuming remote TestClient launch readiness

## Status
4.done

## Order Index
160

## Owner
Codex

## OpenSpec Stage
reviewed; published

## Source
- Root tracker:
  `/opt/ai-dev-suite-for-1c/openspec/board/1.backlog/s50-finans-extension-e2e-010-author-own-objects-and-real-cfe-roundtrip.md`
- Runtime evidence:
  `/opt/ai-dev-suite-for-1c/admin-mcp/.runtime/changerail/evidence/s50-160-own-cfe-disposable-roundtrip/20260801T083429Z/`

## Summary
Remote `launch_test_client` re-probed the tunneled TestClient socket after the
Windows host-agent had already reported an owned, listening lifecycle. Against
the S50 disposable Windows proof this consumed the single manager connection
before the real protocol navigation could use it. Trust the lifecycle-bound
host-agent readiness result and leave the forwarded socket untouched for the
first protocol tool call.

## Acceptance Criteria
- [x] Lifecycle-owned host-agent launches with `listening=true` skip the
  thin-side TCP readiness probe.
- [x] Legacy or unowned host-agent launch results still require the existing
  container reachability probe.
- [x] The returned MCP launch status records that the local probe was skipped
  because host-agent lifecycle readiness was authoritative.
- [x] Focused regression coverage fails if the local probe is called for an
  owned ready launch.
- [x] Windows S50 evidence records the original consumed-socket failure and
  exact cleanup of temporary host resources.

## Evidence Boundary
Retain runtime logs, tokens, screenshots and staged infobases only under ignored
`.runtime/` paths. Do not commit Windows tokens, screenshots, host-agent logs or
infobase files.

## Change Set
- `s50-160-non-consuming-remote-launch-readiness`: implemented directly as a
  narrow qa-mcp runtime follow-up; no main spec delta needed for the scoped
  runtime behavior.

## Change 1: `s50-160-non-consuming-remote-launch-readiness`

### Why
A TestClient TPort behaves like a single manager socket. A generic TCP
connectivity probe through SSH/local forwarding can be destructive even though
it never sends a protocol frame.

### Goal
Make remote `launch_test_client` preserve the first TestClient socket connection
for the real qa-mcp protocol operation whenever the host-agent has already
proved an owned ready lifecycle.

### Scope
- Python MCP remote launch readiness handling in `src/qa_mcp/mcp_server.py`.
- Focused Python regression in `tests/test_mcp_server.py`.
- No host-agent wire-contract change, no 1C metadata change, no business-data
  mutation.

### Acceptance
- As in the card Acceptance Criteria.

### Depends On
- `remote-testclient-owned-lifecycle`
- `s50-120-bind-remote-ui-actions-to-lifecycle-window`

### Related
- Root S50 package tracker listed above.
- Retained Windows proof attempts under the runtime evidence path above.

## Verify
- `./.venv/bin/python -m pytest -q tests/test_mcp_server.py -k 'launch_test_client_remote'`
  -> `8 passed, 132 deselected`.
- `./.venv/bin/python -m compileall -q src/qa_mcp/mcp_server.py tests/test_mcp_server.py`
  -> passed.
- `uv run ruff check src/qa_mcp/mcp_server.py tests/test_mcp_server.py`
  -> blocked by pre-existing unused imports in `src/qa_mcp/mcp_server.py`
  (`client_screenshot`, `window_list`, `native_send_keys`); not changed by this
  follow-up.
- Windows evidence on `HISTORICAL-LAB-HOST`:
  - source-bound host-agent build
    `sha256=78f93de9c4654e390c25ac7a5576a315b85497fad3df13ea6793f57b57b2510a`;
  - consumed-socket/stale-target attempts retained under
    `windows/ui-proof-host-agent-highest/` and
    `windows/ui-proof-direct-host-agent/`;
  - final cleanup inventory shows the exact S50 stage directory absent and
    ports `18160`/`15661` closed.

## Archive
- not applicable; no OpenSpec delta spec was created for this scoped runtime
  follow-up.

## Related
- Root tracker:
  `/opt/ai-dev-suite-for-1c/openspec/board/1.backlog/s50-finans-extension-e2e-010-author-own-objects-and-real-cfe-roundtrip.md`

## Result
Implementation, focused verification and independent review are complete. The
review verdict is `go` in
`.runtime/changerail/reviews/s50-160-non-consuming-remote-launch-readiness.json`.
Published on qa-mcp `main`.
The root S50 tracker is not closed yet because the broader UI catalog
create/read proof still requires a fresh Windows rerun after this qa-mcp fix is
published, plus the admin/config target-bound staging gap needs an owning
decision.

## Next
- rerun the root S50 Windows UI proof after the qa-mcp fix is available

## Log
- 2026-08-01T09:30:00Z card created from root S50 runtime proof.
- 2026-08-01T09:35:00Z implemented non-consuming readiness skip for
  lifecycle-owned host-agent launches and added focused regression coverage.
- 2026-08-01T09:29:34Z independent review returned `go` with no blocking
  findings.
- 2026-08-01T09:45:00Z published scoped qa-mcp change to `main`.
