# S50-110: Live open_list must not depend on development captures

## Status
4.done

## Order Index
110

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Root tracker: `/opt/ai-dev-suite-for-1c/openspec/board/1.backlog/s50-finans-extension-e2e-110-remove-live-open-list-capture-fixture-dependency.md`
- Prerequisite: `openspec/board/4.done/remote-testclient-owned-lifecycle.md`
- Follow-up from S50 Finans extension E2E.

## Summary
Remove the released-runtime dependency on historical development capture names
from the public `open_list` path. In remote/live TestClient mode, omitting
`capture` must select a supported bundled/navigation-template path or fail
closed with a typed capability diagnostic before any protocol write. It must
not resolve to `/work/traffic.jsonl` or to a missing dev-run capture.

## Acceptance Criteria
- [x] `open_list` has no public default that names a historical development
  capture directory.
- [x] Omitting `capture` selects a supported live navigation path and does not
  resolve to `/work/traffic.jsonl`.
- [x] Missing optional navigation assets return a typed diagnostic before any
  TestClient protocol write.
- [x] Unit or black-box MCP tests cover omitted capture, explicit bundled
  template and missing-asset cases.
- [x] Windows/live evidence is retained when the implementation changes real
  remote TestClient behavior; otherwise the card records why Linux/offline
  coverage is sufficient for the changed surface.

## Change Set
- `live-open-list-capture-free-navigation`:
  `openspec/changes/archive/2026-07-31-live-open-list-capture-free-navigation/`

## Change 1: `live-open-list-capture-free-navigation`

### Why
The released `open_list` endpoint must not depend on an ignored development
capture when the runtime already ships a versioned, live-proven navigation
template path.

### Goal
Make omitted or blank `capture` use template-backed live navigation, preserve
explicit bundled-capture compatibility, and fail closed before protocol I/O
when navigation assets are unavailable.

### Scope
- Public `open_list` dispatch and schema documentation.
- Preflighted bundled bootstrap/value-read navigation templates.
- Focused endpoint tests and bounded Windows/live evidence.

### Acceptance
- As in the card Acceptance Criteria.

### Depends On
- `openspec/board/4.done/remote-testclient-owned-lifecycle.md`

### Related
- `openspec/changes/archive/2026-07-31-live-open-list-capture-free-navigation/`

## Verify
- RED: focused endpoint tests failed before implementation (`31 failed, 1
  passed`) because the template-backed helper and capture-free public signature
  did not exist and omitted capture still followed the old validation path.
- GREEN: focused endpoint and registry coverage passed (`40 passed in 2.54s`)
  for omitted/blank capture, explicit bundled capture, missing assets,
  incomplete frames 8–10/218, malformed splice structure, preflight ordering,
  public signature and attached endpoint routing. Stale-attachment regressions
  prove invalid assets return before liveness opens a socket, and the success
  branch proves `asset preflight -> attachment liveness -> live open`.
- Full verification: `uv run --with pytest --with pyyaml pytest -q` passed
  (`892 passed in 75.93s` after review-rescue cycle 3);
  `python3 -m compileall -q src/qa_mcp` passed.
- Specification and hygiene: `openspec validate --all --strict` passed (`19
  passed, 0 failed`) after archival; `git diff --check` passed.
- Live proof: the current working-tree `open_list(catalog="Справочник.Валюты")`
  opened `Валюты` through the template-backed path on the authorized Windows
  TestClient (`ok: true`, `accepted: true`). Provider-owned cleanup stopped the
  client and the proof port, host-agent port, scheduled task, staging directory,
  transient script and local SSH tunnel were verified absent afterward.
- Review-rescue cycle 3 reran that proof using only the opaque provider-owned
  lifecycle handle for TestClient cleanup. Exact sanitized preflight, staging,
  tunnel, current-tree call, lifecycle-stop and cleanup-audit commands are in
  `.runtime/changerail/evidence/live-open-list-capture-free-navigation/commands-cycle3.md`;
  no port-wide process cleanup fallback remains.
- The local Linux doctor recorded the pre-execution runtime gap
  `bearer-token-env-missing` / `testclient-tport-unreachable`; no local live
  execution began. Sanitized live evidence remains ignored under
  `.runtime/changerail/evidence/live-open-list-capture-free-navigation/`.

## Archive
- `openspec/changes/archive/2026-07-31-live-open-list-capture-free-navigation/`

## Related
- Root tracker:
  `/opt/ai-dev-suite-for-1c/openspec/board/1.backlog/s50-finans-extension-e2e-110-remove-live-open-list-capture-fixture-dependency.md`
- Prerequisite: `openspec/board/4.done/remote-testclient-owned-lifecycle.md`
- Change:
  `openspec/changes/archive/2026-07-31-live-open-list-capture-free-navigation/`

## Result
Implementation, specification sync, verification, independent review and
archival are complete.

Published reviewed payload as `23ae18c109a6f8cd968763fd5f9909b32d5faa3a`; push status `pending` on `main`/`origin`.

## Evidence Boundary
Retain only sanitized path classes, reason codes and test outcomes. Do not
commit raw traffic, screenshots, infobase files, credentials or host-agent logs.

## Next
- done

## Log
- 2026-07-31T21:24:35Z `$changerail-ff` accepted the story as one coherent
  change, created complete apply-ready artifacts, and prepared the card for
  delivery.
- 2026-07-31T21:41:40Z `$changerail-do` implemented capture-free template-backed
  `open_list`, retained explicit capture compatibility, proved missing-asset
  fail-closed ordering, passed focused/full/strict verification, retained
  sanitized Windows live evidence, synced the capability spec, and archived
  the completed change.
- 2026-07-31T21:51:30Z independent review cycle 1 returned NO-GO because
  loadable templates missing frames 8–10 could fail after earlier writes, the
  regression covered only a missing file, and the live evidence lacked exact
  command provenance and ownership-safe cleanup.
- 2026-07-31T21:58:13Z review-rescue cycle 2 preflighted every bootstrap/splice
  frame, added incomplete-template and malformed-marker regressions, passed the
  expanded focused/full suites, and reran the Windows proof with exact command
  provenance and lifecycle-handle-only cleanup.
- 2026-07-31T22:10:55Z independent review cycle 2 returned NO-GO because the
  public endpoint wrapper still probed attached-endpoint liveness before asset
  preflight, so a stale attachment could mask the required asset diagnostic.
- 2026-07-31T22:17:43Z review-rescue cycle 3 moved reusable asset preparation
  ahead of attachment resolution, added stale/successful ordering regressions,
  passed the focused/full suites, and reran the current-tree Windows proof with
  owned cleanup and a clean post-run audit.
- 2026-07-31T22:28:59Z publish finalized card into `4.done` with commit `23ae18c109a6f8cd968763fd5f9909b32d5faa3a` and push status `pending`.
