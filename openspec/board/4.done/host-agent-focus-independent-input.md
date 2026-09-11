# Host-agent focus-independent input (F5/Escape without SetForegroundWindow)

## Status
4.done

## Owner
Codex

## OpenSpec Stage
archived

## Source
- v0.2.4 Phase-4 E2E on historical-user (2026-07-06, `demo10413`, model B / host-agent).
  `read_list_grid` on `Справочник.Валюты` returned `row_count:0` until the operator
  manually clicked the 1C window; once foregrounded it returned 10 real rows.
- Root cause captured live: host-agent `/send_keys` → HTTP 500
  `SetForegroundWindow(0xD1588) failed: The operation completed successfully.` =
  Windows foreground-lock. The window was found correctly (by title AND by class);
  only the foreground steal was denied because the operator's desktop foreground was
  held by other apps (active/connected session). Tried direct, session-2
  `AttachThreadInput`, and `SPI_SETFOREGROUNDLOCKTIMEOUT=0` — none let the background
  host-agent take foreground on a busy desktop. See [[qa-mcp-v0-2-4-release]].

## Summary
The host-agent display bridge sends keystrokes with `SendInput`, which requires the
target window to be the **foreground** window — so it calls `SetForegroundWindow`
first. On a busy interactive desktop Windows denies that call (foreground-lock), so
the `F5` refresh and the Escape clean-state sweep silently fail and dynamic-list reads
(`read_list_grid` / `read_list_column` / `read_list_row`) return an honest but
unhelpful `0 rows — no display backend reachable to send «Обновить»/F5`.

The v0.2.4 read_list_grid fix (descriptor table resolution + honest diagnostics) is
correct and unaffected — this card is strictly about the **display bridge** so list
reads self-refresh even when the 1C window is not the foreground window. `window_list`
already works without foreground (it enumerates), proving the transport/handshake are
fine; only the keystroke primitive is foreground-coupled.

## Scope
1. **Focus-independent keystroke primitive.** In the Go host-agent, deliver `F5`
   (VK_F5) and `Escape` (VK_ESCAPE) to the resolved 1C window via `PostMessage` /
   `SendMessage` (`WM_KEYDOWN`/`WM_KEYUP`) instead of `SendInput`, so no foreground
   steal is needed. Keep the resolved-window targeting (title + `V8TopLevelFrame*`
   class) already in place.
2. **Foreground fallback, hardened.** When a real foreground is required (rare),
   attempt an `AttachThreadInput` + `SetForegroundWindow` sequence and treat a denied
   foreground as a soft-degrade, not a hard 500 — return a structured
   `foreground-denied` result the Python side can surface honestly.
3. **Honest, actionable diagnostic.** The Python `_force_list_refresh` /
   `_cold_state_sweep` swallow the real host-agent error into a generic
   "no reachable display backend" (`mcp_server.py:3905`). Propagate the real cause
   (e.g. `foreground-denied`) so the reason names the actual blocker and the fix
   ("bring the 1C window to the foreground, or the agent should not contend for
   foreground") rather than implying the agent is unreachable.
4. **Non-goal:** no change to the protocol read/replay path, the table-resolution
   fix, model-A X11 behavior, or the COM bridge.

## Acceptance
- With the 1C window NOT foreground on a busy desktop, `read_list_grid` on a populated
  list returns the rows (F5 lands via PostMessage) — the manual-click workaround is no
  longer required.
- When a genuine foreground denial still occurs, the tool result names
  `foreground-denied` (not a generic "no display backend") and the run does not 500.
- `window_list` / `screenshot` behavior unchanged; model-A X11 path unchanged.
- Go host-agent tests cover the PostMessage keystroke path; a Windows E2E retains a
  transcript of a non-foreground `read_list_grid` returning rows.

## Dependencies
- Host-agent version bump (`display_backend.HOST_AGENT_VERSION`) + compatibility set,
  since the keystroke contract changes. Ship the new `.exe` in the next release and
  keep the version handshake honest.

## Change Set
- `host-agent-postmessage-keys` - host-agent target-window `F5`/`Escape`,
  structured `foreground-denied`, and version handshake bump.
- `read-list-refresh-diagnostics` - Python list-refresh diagnostics preserve
  host-agent causes at the MCP boundary.

## Change 1: `host-agent-postmessage-keys`

### Why
The Windows host-agent currently uses foreground-coupled `SendInput` for
`F5`/`Escape`, so Windows foreground-lock can block list refresh and clean-state
sweeps even when the 1C window was resolved correctly.

### Goal
Deliver the refresh/clean-state key subset to the resolved 1C top-level window
without stealing foreground, and make genuine foreground denial a structured
host-agent result.

### Scope
- Add a target-window Win32 message path for `F5` and `Escape`.
- Preserve existing targeting and authentication boundaries.
- Keep other key/chord requests on the foreground-coupled path.
- Return structured `foreground-denied` instead of generic HTTP 500 when real
  foreground is denied.
- Bump host-agent and Python compatibility versions.

### Acceptance
- Authenticated `/send_keys` for `F5` or `Escape` can target a non-foreground
  `V8TopLevelFrame*` 1C window without calling `SetForegroundWindow`.
- Foreground-required primitives report `foreground-denied` with a non-500
  structured result when Windows denies foreground activation.
- Go tests cover no-focus key routing and foreground-denied mapping.
- Python handshake tests accept the bumped host-agent version by default.

### Depends On
- none

### Related
- `openspec/changes/host-agent-postmessage-keys/`

### Notes For `$openspec-ff-change`
- 1C verification matrix is in `design.md`.
- Windows E2E proof is required when an operator-owned Windows GUI desktop is
  available; otherwise retain a runtime gap under `.artifacts/openspec/`.

## Change 2: `read-list-refresh-diagnostics`

### Why
The Python list-refresh helpers collapse host-agent primitive failures into
generic "no display backend" text, hiding the difference between an unreachable
agent and a busy-desktop foreground denial.

### Goal
Preserve structured display-backend error causes in refresh metadata and zero-row
list diagnostics.

### Scope
- Preserve `DisplayBackendError` code/detail/install guidance from
  `_force_list_refresh`.
- Preserve clean-state sweep failure details in polling metadata.
- Update zero-row list reasons to name `foreground-denied` and other host-agent
  primitive causes separately from reachability failures.
- Add focused Python tests without requiring live Windows or 1C runtime.

### Acceptance
- A fake host-agent `foreground-denied` refresh failure is visible in list-read
  metadata or zero-row reason.
- Host-agent unreachable/configuration failures still retain install guidance.
- Refresh/sweep failures do not raise raw exceptions through the MCP boundary.
- Windows E2E transcript is retained when a suitable desktop is available, or a
  runtime gap is recorded.

### Depends On
- `host-agent-postmessage-keys` for real Windows E2E proof; offline diagnostic
  tests may be implemented independently.

### Related
- `openspec/changes/read-list-refresh-diagnostics/`

### Notes For `$openspec-ff-change`
- 1C verification matrix is in `design.md`.
- Keep list table-resolution and protocol replay behavior unchanged.

## Verify
- `openspec validate host-agent-postmessage-keys --strict` passed during planning.
- `openspec validate read-list-refresh-diagnostics --strict` passed during planning.
- `git diff --check -- openspec/changes openspec/board` passed during planning.
- Delivery checks passed:
  - `go test ./...` under `host-agent/windows-display-agent`
  - `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-postmessage-keys.test.exe .`
  - `uv run --with pytest --with pyyaml pytest tests/test_display_backend.py -q`
  - `uv run --with pytest --with pyyaml pytest tests/test_form_descriptor.py tests/test_display_backend.py -q`
  - matrix checker preflight/archive for both changes
  - `openspec validate --all`
  - `git diff --check`
  - `uv run --with pytest --with pyyaml pytest` (`714 passed`)
  - `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/check_suite_source_of_truth_drift.py`
  - `uv run --with pytest --with pyyaml pytest -m smoke` (`2 passed`)
- Windows E2E (model B): runtime gap recorded under `.artifacts/openspec/...`
  because no operator-owned Windows GUI desktop/host-agent/TestClient is attached
  to this Linux workspace.

## Archive
- `openspec/changes/archive/2026-07-06-host-agent-postmessage-keys/`
- `openspec/changes/archive/2026-07-06-read-list-refresh-diagnostics/`

## Related
- `openspec/changes/host-agent-postmessage-keys/`
- `openspec/changes/read-list-refresh-diagnostics/`
- publish commit: `feat(host-agent): make refresh keys foreground-independent`

## Result
Delivered: host-agent `F5`/`Escape` refresh keys use a target-window path,
foreground denial is structured, Python list refresh diagnostics preserve the
real host-agent cause, specs are synced, and both changes are archived.
Published: docs, board state, archived changes and implementation are in the
publish commit.

## Next
- none for Linux publish; run Windows model-B E2E when an operator-owned
  Windows GUI desktop/host-agent/TestClient is available.

## Log
- 2026-07-06 created from the v0.2.4 historical-user E2E foreground-lock finding.
- 2026-07-06T14:06:52Z planned via `$opsx-ff`: created
  `host-agent-postmessage-keys` and `read-list-refresh-diagnostics`, validated
  both changes, and moved card to `2.todo`.
- 2026-07-06T14:10:00Z `$opsx-do` started; moved card to `3.inprogress`.
- 2026-07-06T14:18:00Z archived `host-agent-postmessage-keys`; post-archive
  `openspec validate --all` and `git diff --check` passed.
- 2026-07-06T14:24:32Z archived `read-list-refresh-diagnostics`; full suite
  regression gate passed and card moved to `4.done`.
- 2026-07-06T14:27:00Z `$opsx-pub` docs pass updated host-agent, Docker and
  tool-reference docs for focus-independent `F5`/`Escape` and
  `foreground-denied`.
- 2026-07-06T14:30:03Z `$opsx-pub` committed the scoped delivery as
  `feat(host-agent): make refresh keys foreground-independent`; final commit
  hash is reported by git after card-sync amend and push.
