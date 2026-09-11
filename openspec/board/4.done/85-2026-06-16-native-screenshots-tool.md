# 85. Native screenshots tool

## Status
4.done

## Order Index
85

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-16: roadmap card 82, stage 3. vanessa-mcp exposes `get_window_screenshot_os`; qa-mcp has none (we
  captured screenshots with external `scrot` on the lab display).

## Summary
Add a screenshot capability to qa-mcp so an agent can SEE the TestClient UI (dialogs, forms, errors) as
evidence — at minimum an OS-level capture of the client's display, exposed via the MCP.

## Acceptance
- An MCP tool returns a screenshot of the TestClient's window/display (PNG path or inline), captured
  headlessly (Xvfb / xrdp display per the lab).
- Optionally: a protocol-level form render if/when feasible; OS capture is the v1.
- Works in the headless lab (the autonomous-1c-observability toolkit: scrot on the client's DISPLAY) and is
  documented for the supported displays (`:77` xvfb / `:10` xrdp).

## Decision (2026-06-16)
- Two layers exist: OS/display capture vs a protocol-level render. vanessa-mcp's own tool is
  `get_window_screenshot_os` → **OS-level capture is the parity mechanism, not a compromise.** Scope locked to
  **Linux OS-capture v1**; Windows (pywin32 PrintWindow) + protocol render deferred to later cards.
- Linux display strategy chosen: **lifecycle OWNS an Xvfb on a fixed display** (`launch_test_client(display=…)`),
  so the display persists independently of the client (post-crash screenshots possible) and we always know it.
- Capture backend: **shell out to `scrot` (fallback ImageMagick `import`)** — zero new deps (no python imaging
  lib is installed; uv is `--frozen`); window-targeting via `xdotool` (best-effort, no WM under Xvfb).

## Change Plan
1. ✅ Lifecycle owned-display mode — `TestClientTarget.display` (":N" / "auto") + `screen_geometry`; lifecycle
   starts its own `Xvfb :N`, runs the client with `DISPLAY=:N`; handle/`status()` carry `display`+`xvfb_pid`;
   teardown also kills the Xvfb (`pick_free_display`/`_start_xvfb`/`display_in_use`). DONE.
2. ✅ Screenshot module — `src/qa_mcp/protocol/screenshot.py`: `LinuxX11Backend` (scrot→import, optional
   window via xdotool), `WindowsGdiBackend` (deferred stub), platform `get_backend` + `capture_screenshot`. DONE.
3. ✅ MCP surface — `capture_screenshot(display, window?, out_path?)` (server now registers 10 tools);
   `launch_test_client` gains `display`, `stop_test_client` gains `xvfb_pid`. DONE.
4. ✅ Tests — `tests/test_screenshot.py` (7): mock-runner backend (scrot, import fallback, window/xdotool,
   all-fail→error, platform dispatch, Windows stub) + a REAL Xvfb capture asserting PNG magic (no 1C). Full
   suite 191 passed. DONE.

## Progress (2026-06-16)
- **DONE + live-verified.** `tools/protocol-research/run_screenshot_test.sh`: launch a real TestClient on an
  owned display (`auto` → :101, xvfb_pid recorded) → `capture_screenshot(":101")` in a SEPARATE process (proves
  the display outlives the launcher) → scrot PNG 78 KB → `stop_test_client(pid, xvfb_pid)` tears down client +
  Xvfb + restores apache. The PNG shows the live client UI (title «Клиент тестирования (1С:Предприятие)»,
  managed-form home page, sales charts, «Календарь Вт, 16 июня 2026») — the agent can SEE the client. Lab clean.
- Window-by-title (xdotool) is best-effort: under a bare Xvfb (no WM) the title search returned no match and it
  fell back to the full display (`matched_window_id=null`) — acceptable for v1; refine under cards 88/89.
- Acceptance met: MCP tool returns a PNG of the client's display, captured headlessly (owned Xvfb); OS capture
  is v1; documented for the supported displays.

## Change Set
- `src/qa_mcp/protocol/screenshot.py` (NEW), `src/qa_mcp/protocol/lifecycle.py` (owned-display mode),
  `src/qa_mcp/protocol/__init__.py` (exports), `src/qa_mcp/mcp_server.py` (+capture_screenshot, display/xvfb_pid),
  `tests/test_screenshot.py` (NEW, 7), `tools/protocol-research/run_screenshot_test.sh` (NEW).

## Related
- memory autonomous-1c-observability (scrot recipe), card 81, `src/qa_mcp/mcp_server.py`.

## Log
- 2026-06-16T00:00:00Z card created.
- 2026-06-16: implemented + live-verified → moved to 4.done. Lifecycle owned-display mode + screenshot.py
  (scrot/import) + capture_screenshot MCP tool (server now 10 tools) + 7 tests (full suite 191 passed). Live
  run captured the real client home page on owned display :101; agent confirmed the UI by reading the PNG.
