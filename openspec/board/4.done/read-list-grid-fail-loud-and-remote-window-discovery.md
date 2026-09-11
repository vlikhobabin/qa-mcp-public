# read_list_grid returns a misleading row_count:0 when remote-client window discovery/refresh fails

## Status
4.done

## Owner
codex

## OpenSpec Stage
archived. **P0 correctness** (qa-mcp reports wrong data). Under epic 111.

## Source
- `docs/qa-mcp-connection-issues-2.md` findings **#10, #11, #12** — real-base
  test on `File="C:\Users\User\Documents\private-lab-infobase"` ([redacted third-party configuration]), 8.3.27.2130,
  remote-client mode (Windows host TestClient + thin container), 2026-07-07.

## Problem
`read_list_grid` opened `e1cib/list/Справочник.Валюты`, resolved the form
descriptor (`opened: "Валюты"`), but returned:
```json
{ "row_count": 0, "rows": [] }
```
while the **live** 1C window had a visible row (`Российский рубль / 643 / руб. / 1`,
confirmed by Windows UI Automation). The 0 came from a swallowed failure:
```json
{ "error": "window-not-found", "tool": "force_list_refresh", "mode": "remote-client", "status": 422 }
```
(`refresh=false` still returned 0 with a `cold_state_sweep` failure). Two defects:

1. **Silent wrong data (P0):** a refresh/sweep failure is reported inside the
   payload but the top level still looks like a valid empty read (`row_count:0`).
   A test agent consumes "0 currencies" as fact — a false negative that can pass
   or fail assertions on fabricated emptiness.
2. **Remote-client window discovery is broken:** protocol attach works and the
   form descriptor resolves, but the window-level refresh/read cannot find the
   host window, even though it exists as `V8TopLevelFrameSDI` (title
   "Бухгалтерия предприятия, редакция 3.0", form "Валюты") — which the
   host-agent's own `driver_windows.go find1CWindow` is designed to locate.

## Scope
1. **Fail loud** — when refresh / `cold_state_sweep` / window discovery fails,
   `read_list_grid` (and siblings) must NOT return a plausible `row_count:0`.
   Return `ok:false` (or `data_confidence:"unknown"`) with the underlying
   `window-not-found`/refresh error surfaced at the top level.
2. **Fix remote-client window discovery** — route the refresh/read window lookup
   through the host-agent's window discovery (`find1CWindow`, class
   `V8TopLevelFrame*`) + UIA so the visible form is found; add a diagnostic that
   lists discovered Windows-side 1C windows (handle/class/title/PID) and the
   exact identity being searched for (#11).
3. **UIA-visible fallback read** (#12) — an official fallback that reads visible
   list cells through the host-agent/UIA bridge when the protocol grid read
   can't confirm it read the intended live window; attach screenshot/UIA
   evidence when a list read returns 0 after a refresh failure.

## Acceptance
- On [redacted third-party configuration] `Справочник.Валюты` with the live client open, `read_list_grid`
  returns the visible row(s) OR a top-level `ok:false`/`data_confidence:unknown`
  with the real error — it never returns `row_count:0` while a sweep/refresh
  failed and a row is visible.
- A window-discovery diagnostic lists the host-side 1C windows and shows the
  target identity; on this case it matches `V8TopLevelFrameSDI` / form "Валюты".
- Regression: normal (all-in-one/Linux Xvfb) list reads unchanged.

## Change Set
- `read-list-grid-fail-loud-and-remote-window-discovery`

## Verify
- OpenSpec validation.
- Focused Python list-read tests.
- Host-agent Go tests and Windows build/compile check.
- 1C verification matrix preflight/archive-gate evidence, with Windows
  [redacted third-party configuration] runtime smoke recorded or explicitly gapped.

## Archive
- `openspec/changes/archive/2026-07-07-read-list-grid-fail-loud-and-remote-window-discovery/`

## Result
implemented, verified, specs synced, archived

## Next
- resolve or explicitly accept the isolated full-pytest release-bootstrap
  failure, then run
  `$opsx-pub openspec/board/4.done/read-list-grid-fail-loud-and-remote-window-discovery.md`

## Change 1: `read-list-grid-fail-loud-and-remote-window-discovery`

### Why
`read_list_grid` must not let callers mistake a failed remote-client refresh or
window lookup for an empty catalog.

### Goal
Fail loud for uncertain zero-row list reads, surface remote Windows window
discovery, and provide bounded UIA-visible fallback evidence from the
authenticated host-agent.

### Scope
- Python MCP list-read result classification for grid, column and row reads.
- Remote-client diagnostic attachment in the Python display backend.
- Windows host-agent window class metadata and visible-cell diagnostic endpoint.
- Focused Python/Go tests and retained verification evidence.

### Acceptance
- Zero-row reads after refresh/sweep/window discovery failure return `ok:false`
  or `data_confidence:"unknown"` with the underlying error at top level.
- Remote-client diagnostics list searched target identity and discovered 1C
  windows including class/title/PID/handle.
- UIA-visible cell diagnostics are attached when available, or an explicit
  diagnostic gap is attached.
- Confirmed refreshed-empty and normal Linux/Xvfb list reads remain valid.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-07-read-list-grid-fail-loud-and-remote-window-discovery/`

### Notes For `$openspec-ff-change`
- Use `qa-mcp-tool-endpoint-contract` and `qa-mcp-windows-host-agent-security`
  as modified capabilities.
- Treat the Windows [redacted third-party configuration] live smoke as runtime evidence when available;
  otherwise record a runtime gap with owner `/opt/ai-dev-suite-for-1c/qa-mcp`.

## Related
- `docs/qa-mcp-connection-issues-2.md` (#10/#11/#12), epic 111.
- `mcp_server.py` (read_list_grid / force_list_refresh / cold_state_sweep);
  host-agent `driver_windows.go` (`find1CWindow`, `V8TopLevelFrame*`).
- `openspec/changes/archive/2026-07-07-read-list-grid-fail-loud-and-remote-window-discovery/`

## Log
- 2026-07-07 filed from the .205 real-base ([redacted third-party configuration]) connection-issues report.
- 2026-07-07T18:24:17Z `$opsx-ff` created apply-ready artifacts and moved card
  to `2.todo`.
- 2026-07-07T18:29:50Z `$opsx-do` implemented fail-loud list reads, host-agent
  window/class and visible-cell diagnostics, synced specs, and archived the
  change.
- 2026-07-07T18:29:50Z publish blocked by pre-existing full-pytest failure in
  `tests/test_self_hosted_release_scripts.py::test_bootstrap_cleans_sensitive_launch_helper_and_blocks_stale_listener`;
  `delivery/bootstrap.ps1` and that test are untouched by this card.
