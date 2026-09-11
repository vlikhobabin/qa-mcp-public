# 120. Windows host-side input/screenshot agent — recover the model-B display subset (card 119 agenda #2)

## Status
4.done

## Order Index
120

## Owner
codex

## OpenSpec Stage
archived

## Source
- 2026-06-26 architecture discussion. Executes **agenda #2 of card [119]**
  (`119-2026-06-25-windows-thin-cross-machine-delivery.md`): recover the XTEST/screenshot subset that model B
  (thin cross-machine) loses on Windows, with a host-side native agent behind a "display backend" abstraction.
- Builds on the model-B productization already shipped (`docker/Dockerfile.thin`, `QA_MCP_REMOTE_CLIENT` mode,
  the `_local_only_tool` guards in `mcp_server.py`). Memory [[qa-mcp-public-delivery-prep]].
- This is the **only** remaining work for model B; everything else is closed and pushed (commit `02bf355`).

## Problem
In model B the **protocol surface (TCP) works fully** — all form reads/writes, dialogs, grids, navigation,
debug-protocol coverage/perf and the OData data-layer drive a Windows-built TestClient as-is over
`host.docker.internal:15381` (proven: 43 live fields). What is lost is the subset that depends on the **thin
container's local X server**: OS input injection (XTEST/xdotool), screenshots (scrot/ImageMagick) and on-screen
pixel location (`locate_text` / `subimage-search`). On a Windows host the render is **GDI** and lives in the
user's desktop session — there is no X display in the Linux container to drive. Today those tools return a
structured guard (`_local_only_tool`) instead of running.

## Spike result (2026-06-26) — `SendInput` PROVEN on the Windows GDI client ✅
The riskiest unknown is de-risked LIVE on the Windows lab (`historical-user@192.0.2.202`, `vanessa_client` @
8.3.27.2130). Ran the REAL `write_form_value_xtest` flow with ONLY the OS-input primitive swapped to **Win32
`SendInput` via ctypes** (`KEYEVENTF_UNICODE`) — the identical call the Go agent will make. A
`PrintWindow(PW_RENDERFULLCONTENT)` capture shows the typed value (incl. Cyrillic — `…Тест 2026`,
`WIN-SENDINPUT-OK-Кириллиц…`) landing in the **Наименование** object-attribute field of the open
**Валюта (создание)** form. → **`SendInput` delivers a genuine ASCII+Cyrillic edit into a 1C managed-form field
the pure protocol cannot commit; the agent's keyboard primitive is validated.** Evidence:
`docs/protocol-research/evidence/card120-windows-sendinput-spike-2026-06-26/` (findings.md + driver + PrintWindow
PNGs). Two findings that shape v1:
- **1C draws forms in a single `V8TopLevelFrameSDI` window with NO child HWND controls** (`GetGUIThreadInfo`
  confirmed focus on the frame, our PID, throughout the type). So `SendInput`/`PrintWindow` are load-bearing and
  **UIA is unlikely to expose form fields** — reinforces **D9** (UIA = optional spike, not v1).
- **Foreground management is a real agent responsibility** on a shared desktop (clear the foreground lock +
  minimize others + `SwitchToThisWindow` + `SetForegroundWindow`, verify via `GetForegroundWindow`/
  `GetGUIThreadInfo`; capture via window-targeted `PrintWindow`, z-order independent). The spike's `spike_win.py`
  is a working reference. (The xtest capture-replay `committed` read-back returned false — a contended-desktop /
  GUID-rebind read-back artifact, NOT an input failure; production verifies via screenshot + `assert_data`.)

## Lost tools (verified against `src/qa_mcp/mcp_server.py` 2026-06-26)
Eight tools are guarded with `@_local_only_tool`; a ninth (`open_external_processor`) uses the same display
primitives but is **NOT** guarded — in `REMOTE_CLIENT` mode it would crash instead of returning a clean guard
(a guard-consistency bug to fix here).

| Tool | Purpose | Protocol analog over TCP? | v1 Windows mechanism |
| --- | --- | --- | --- |
| `capture_screenshot` | OS PNG of the client display | None for pixels; **semantic** = `read_form_descriptor`/`read_list_grid` (form state as data) | `PrintWindow`/`BitBlt` → PNG bytes |
| `send_keys` | raw OS keys (Enter/Esc/Tab/Ctrl+S) | Partial (`answer_dialog`/`click_command`/`select_table_row` cover most intents) | `SendInput` (+`KEYEVENTF_UNICODE`) |
| `write_form_value_xtest` | commit **Объект.*** attrs (need genuine edit+blur) | Partial (`write_form_value`/`set_table_cell`/`set_reference_field` for most fields, NOT object-attr commit) | `SendInput` Unicode + Tab/Ctrl+S |
| `write_form_fields_by_label` | write fields located by on-screen label | Yes by **field name**; locate variant only when name unknown | `SendInput` + locate (server-side on returned PNG) |
| `set_table_date_cell` | grid DATE cell via calendar (masked editor) | Partial (`set_table_cell` for normal cells, NOT date cells) | `SendInput` mouse + locate calendar button |
| `get_window_list` | OS window list | **Yes, direct** (`get_window_list_testclient`) | `EnumWindows`/`GetWindowText`/`GetWindowRect` |
| `launch_test_client` | local `/TESTCLIENT` boot | None (process lifecycle; **host launches it in model B**) | optional: `CreateProcess` + Job Object |
| `stop_test_client` | local teardown | None | optional |
| `open_external_processor` *(unguarded bug)* | open `.epf`/`.erf` via main-menu→Файл→Открыть | None | `SendInput` mouse/keys + locate |

**Consolidation — 8(+1) tools reduce to ~3 host primitives** (the locate/geometry/Unicode logic STAYS in Python):

| Host primitive (Win32) | Recovers |
| --- | --- |
| **Keyboard** `SendInput`+`KEYEVENTF_UNICODE` | `send_keys`, keyboard half of `write_form_value_xtest`, `write_form_fields_by_label` |
| **Mouse** `SendInput` (mouse) | `set_table_date_cell`, clicks in `write_form_fields_by_label`, `open_external_processor` |
| **Screenshot** `PrintWindow`/`BitBlt`→PNG | `capture_screenshot` + the verification artifact of every locate tool |
| **Windows/process** `EnumWindows` / `CreateProcess` | `get_window_list`, optional `launch/stop_test_client` |

## Decisions (FIXED 2026-06-26)

**D1 — A host-side native agent is mandatory; it cannot be replaced by an in-container OS branch.** The container
is Linux and has no Win32 API. `SendInput`/`BitBlt` MUST run as a native process **on the Windows host, in the
user's interactive session**, in the same desktop where the 1C client is rendered. So the OS-awareness in our
code is "route the display op to the remote agent", NOT "call different functions in-process".

**D2 — The agent is a single static Go `.exe`.** No installer, no 1C libs, no runtime. Win32 via
`golang.org/x/sys/windows`. (PowerShell `Add-Type` P/Invoke is allowed ONLY as an optional throwaway spike to
de-risk; the shipped artifact is the Go binary.) C++ rejected: more ceremony, no benefit here.

**D3 — Thin agent / smart container split.** The agent does ONLY what must live in the Windows session — the
three Win32 primitives — and returns raw results (PNG bytes, ok/err, window rects). All the "smarts" stay in the
Python container unchanged: `locate_text` / `compare -subimage-search` (run on the returned PNG bytes — OS-
agnostic, they don't move), calendar geometry/deltas, Unicode handling, scenario orchestration. This keeps the
agent tiny and the logic in one place.

**D4 — A `DisplayBackend` abstraction selects local vs remote.** Two implementations: `LocalXTestBackend`
(current Linux xdotool/scrot/ImageMagick — model A, **unchanged**) and `RemoteAgentBackend` (HTTP to the host
agent — model B). Selected by env, same family as today's `REMOTE_CLIENT`: `QA_MCP_REMOTE_CLIENT=1` +
`QA_MCP_HOST_AGENT=host.docker.internal:8001` → the currently-guarded tools stop returning a guard and route to
the remote backend; env unset → local backend. The guard return-points become backend dispatch points.

**D5 — Transport = HTTP over a second host port** (e.g. `:8001`) reached via `host.docker.internal` — the SAME
loopback-origin mechanism already proven for the protocol port `:15381` (so networking is solved). Bind
host-only; protect with a shared token header. (Protocol stays on `:15381`; display on `:8001` — two
independent channels.)

**D6 — The agent runs in interactive session 1** (logon Scheduled Task / `schtasks /IT`), NOT a service.
Session-0-isolated processes cannot `SendInput`/`BitBlt` the visible desktop — the same reason the client itself
had to be launched in session 1 (card 119 finding).

**D7 — Version/hash handshake — v1 = detect-and-instruct, NO auto-replace.** The agent exposes `GET /version`
(version + binary hash). The container carries the expected version/hash. On every connect: match → run;
**mismatch or agent-absent → the container returns a CLEAR error naming the exact install/update command** (the
one-liner from D8). v1 deliberately does **not** auto-replace the binary on the user's machine. The
self-update path (`POST /update` + self-restart) is **deferred to v2** (auto-replacing a foreign binary is
sensitive; prove the contour first).

**D8 — First install is a one-time host-side step; it cannot be container-driven.** Two hard blockers make
"container pushes the exe onto a cold host and starts it" impossible: (a) the container has no file-write/exec
channel to the host (only the protocol/agent ports), and (b) Windows Session 0 isolation — a remotely-launched
process can't inject input into the interactive desktop anyway. So ship a tiny one-liner (`.ps1`) the user runs
ONCE: drops `qa-mcp-host-agent.exe` into a known folder, registers a logon Scheduled Task (interactive session),
opens the firewall port. After that, version convergence is automatic (D7).

**D9 — UIA is NOT in v1; it is an optional later spike.** v1 ships the Win32 `SendInput`/`BitBlt` stack — a 1:1
port of the proven Linux XTEST/scrot/ImageMagick stack (lowest risk, behaviorally identical to what is already
GREEN on Linux). UIA is deferred because (i) 1C draws managed forms with custom rendering, so UIA tree coverage
is unverified, and (ii) for the exact failing cases that these tools exist for — object-attribute commit, masked
date editor — UIA's **programmatic** `ValuePattern.SetValue` will very likely fail for the SAME root cause the
protocol's programmatic set fails: 1C commits only on a **genuine input event**. The semantic "primary path" we
already have is the **protocol** (= Vanessa's `ТестируемоеПриложение` testing tree, reimplemented at the wire),
which works in model B; the lost subset is precisely the residue that needs genuine OS input + a real
screenshot, where `SendInput`/`BitBlt` are **load-bearing, not a fallback**. A UIA spike (semantic element
location to replace pixel `locate_text`) is a separate, future investigation gated on confirming 1C UIA coverage
on a live form.

**D10 — Fix the `open_external_processor` guard inconsistency** as part of the backend work (route it through
`DisplayBackend` so it guards/routes like the other display tools instead of crashing in remote mode).

## Recommendation — v1 (minimum) vs v2 (deferred)
**v1 (this card):**
- `DisplayBackend` abstraction + `RemoteAgentBackend` + env routing; guards → dispatch; fix `open_external_processor`.
- Go `.exe` agent: `GET /version`, `GET /health`, and the primitive endpoints (`/send_keys`, `/type`, `/click`,
  `/screenshot`, `/window_list`); host-only bind + token.
- Install one-liner (`.ps1`) + logon Scheduled Task + firewall rule; the handshake error (D7) points to it.
- Port the lost tools through the backend and live-verify on the Windows lab — prioritizing the genuine-input
  proof first (`write_form_value_xtest` object-attr commit), then `capture_screenshot`, `set_table_date_cell`,
  `write_form_fields_by_label`, `send_keys`, `get_window_list`.

**v2 (deferred — separate card/changes):**
- `POST /update` self-update + self-restart (the temp-write → rename → Scheduled-Task-relaunch dance) so version
  convergence is fully automatic.
- UIA semantic-locator spike (gated on confirming 1C managed-form UIA coverage live).
- Optional `launch/stop_test_client` via `CreateProcess` + Job Object (convenience, not a display gap).

## Proposed Change Set (for `$opsx-ff` to decompose; ordered)
1. **`display-backend-abstraction`** — extract a `DisplayBackend` protocol; wrap the current
   xdotool/scrot/ImageMagick calls as `LocalXTestBackend`; add `RemoteAgentBackend` (HTTP client to
   `QA_MCP_HOST_AGENT`); convert the `_local_only_tool` guard return-points into backend dispatch; route
   `open_external_processor` through it too. Capability: display-backend routing.
2. **`host-agent-go-v1`** — the Go static `.exe`: HTTP server, `GET /version` (+hash) / `GET /health` /
   `/send_keys` / `/type` (Unicode) / `/click` / `/screenshot` (PNG) / `/window_list`; Win32 via
   `x/sys/windows`; host-only bind + shared-token auth. Capability: Windows input/screenshot agent.
3. **`host-agent-install-and-handshake`** — the one-liner `.ps1` (drop exe + logon Scheduled Task /IT + firewall
   rule); the container-side version/hash handshake that on mismatch/absence returns the exact install command
   (D7 v1, no auto-replace). Capability: agent install + version negotiation.
4. **`remote-display-e2e`** — wire the ported tools end-to-end and live-verify on `historical-user@192.0.2.202`: genuine
   object-attribute commit, screenshot, date cell, label write, window list. Capability: model-B display-subset
   verification + evidence bundle.

(Each declares ≥1 capability per the spec-driven schema. v2 items above become a follow-on card.)

## Change Set
- `openspec/changes/display-backend-abstraction/`
- `openspec/changes/host-agent-go-v1/`
- `openspec/changes/host-agent-install-and-handshake/`
- `openspec/changes/remote-display-e2e/`

## Change 1: `display-backend-abstraction`

### Why
Model-B protocol TCP works, but the display tools still assume a local Linux X server.

### Goal
Introduce a Python `DisplayBackend` abstraction that preserves local XTEST behavior and routes configured remote-client display operations to a host agent.

### Scope
- Add local and remote display backend code under `src/qa_mcp/protocol/`.
- Route guarded display MCP tools through backend dispatch where possible.
- Fix `open_external_processor` so remote-client mode returns a clean backend diagnostic instead of crashing.

### Acceptance
- Local model-A display behavior remains compatible.
- Remote-client mode with a configured host agent dispatches keyboard, mouse, screenshot and OS-window primitives.
- Remote-client mode without a usable host agent fails closed with actionable diagnostics.

### Depends On
- none

### Related
- `openspec/changes/display-backend-abstraction/`

### Notes For `$openspec-ff-change`
- Artifacts are already apply-ready; do not split unless implementation reveals a concrete contradiction.

## Change 2: `host-agent-go-v1`

### Why
Win32 `SendInput`, `PrintWindow`/`BitBlt` and `EnumWindows` must run in the Windows host's interactive desktop session.

### Goal
Ship a thin static Go host agent that exposes the display primitives over a host-scoped HTTP API.

### Scope
- Add Go source for version/health, keyboard, Unicode typing, mouse click, screenshot and window-list endpoints.
- Bind host-only by default and require a shared token for primitive endpoints.
- Retain Windows-native smoke evidence for the primitive layer.

### Acceptance
- Agent reports version and health.
- Agent can send Unicode input and capture a PNG from a target Windows window.
- Endpoint auth and error handling are covered by tests.

### Depends On
- `display-backend-abstraction`

### Related
- `openspec/changes/host-agent-go-v1/`

### Notes For `$openspec-ff-change`
- Artifacts are already apply-ready; keep the agent thin and leave orchestration in Python.

## Change 3: `host-agent-install-and-handshake`

### Why
The container cannot install or start a cold Windows desktop agent; the user needs a one-time host-side setup and the container needs fail-closed version negotiation.

### Goal
Provide a Windows install command and Python handshake that verifies host-agent version/hash before remote display calls.

### Scope
- Add host install script and model-B docs.
- Add expected version/hash metadata and handshake diagnostics.
- Preserve v1 detect-and-instruct behavior; no auto-replace.

### Acceptance
- Absent or mismatched host agent produces a clear install/update command.
- Matching host agent allows remote display primitive calls.
- Install script syntax and handshake cases are verified.

### Depends On
- `host-agent-go-v1`

### Related
- `openspec/changes/host-agent-install-and-handshake/`

### Notes For `$openspec-ff-change`
- Artifacts are already apply-ready; self-update is explicitly v2.

## Change 4: `remote-display-e2e`

### Why
Model-B is complete only when the recovered display tools work against the real Windows-rendered 1C client.

### Goal
Live-verify the remote backend and host agent with genuine input and screenshot evidence on the Windows lab.

### Scope
- Verify `capture_screenshot` and `write_form_value_xtest` through the remote backend.
- Smoke `send_keys`, `get_window_list`, `write_form_fields_by_label`, `set_table_date_cell` and `open_external_processor` where safe.
- Publish compact curated evidence and update docs/indexes.

### Acceptance
- Retained evidence proves a host screenshot and genuine Unicode input into the 1C managed form.
- Each display-bound tool has an explicit pass, blocked, deferred or N/A status.
- Raw runtime artifacts remain ignored; reviewed docs contain compact summaries only.

### Depends On
- `host-agent-install-and-handshake`

### Related
- `openspec/changes/remote-display-e2e/`

### Notes For `$openspec-ff-change`
- Artifacts are already apply-ready; runtime gaps must be recorded before live execution.

## Acceptance (v1)
- `DisplayBackend` abstraction in code; model A (Linux, `LocalXTestBackend`) unchanged and still GREEN; the 8(+1)
  display tools route through the backend; `open_external_processor` no longer crashes in `REMOTE_CLIENT` mode.
- A single Go `.exe` host agent serving `/version` + the three primitives, host-only + token, runnable in an
  interactive session via the install one-liner + Scheduled Task.
- Version/hash handshake: on mismatch/absence the container returns a clear, actionable error (the install
  command) — **no** auto-replace in v1.
- Live-verified on the Windows lab: at minimum a **genuine-input commit the protocol cannot do** (an `Объект.*`
  attribute via `write_form_value_xtest`) + one `capture_screenshot` returning a real PNG of the host client.
- Card 119 agenda #2 closed; model B has full (protocol + display) coverage on Windows.

## Verify
- OpenSpec strict validation passed for all four changes on 2026-06-26.
- Verification matrix preflight passed for all four `tasks.md` artifacts on 2026-06-26.
- Verification matrix archive gate passed for all four `tasks.md` artifacts on 2026-06-26.
- `python3 -m compileall -q src/qa_mcp` passed.
- `uv run pytest tests/test_display_backend.py tests/test_screenshot.py tests/test_native_xtest.py tests/test_mcp_server.py -q`
  passed: 56 tests.
- `go test ./...` passed in `host-agent/windows-display-agent`.
- `GOOS=windows GOARCH=amd64 go build -o /tmp/qa-mcp-host-agent.exe .` passed; final SHA256
  `1fe93f6f7e447dacdb536b1d6da3fd4e662e3b2450c045dcfe68e45f0c336d9f`.
- Windows live proof passed on `historical-user@192.0.2.202`: host-agent `/version`/`/health`, `get_window_list`,
  `capture_screenshot`, `send_keys` and `write_form_value_xtest(save=false)` through the remote backend.
  Final screenshot shows `WOK-Ж120` in `Наименование`.

## Archive
- `openspec/changes/archive/2026-06-26-display-backend-abstraction/`
- `openspec/changes/archive/2026-06-26-host-agent-go-v1/`
- `openspec/changes/archive/2026-06-26-host-agent-install-and-handshake/`
- `openspec/changes/archive/2026-06-26-remote-display-e2e/`

## Related
- `openspec/changes/archive/2026-06-26-display-backend-abstraction/`
- `openspec/changes/archive/2026-06-26-host-agent-go-v1/`
- `openspec/changes/archive/2026-06-26-host-agent-install-and-handshake/`
- `openspec/changes/archive/2026-06-26-remote-display-e2e/`
- `docs/protocol-research/evidence/card120-windows-sendinput-spike-2026-06-26/`
- `docs/protocol-research/evidence/card120-windows-host-agent-2026-06-26/`

## Result
Delivered. Model-B display-bound primitives now route through a local/remote display backend; a Windows Go
host-agent provides version/health, token-protected keyboard, mouse, screenshot and window-list endpoints; the
installer registers an interactive-user scheduled task; Docker docs include host-agent setup and verification.
Live Windows evidence proves host screenshot and genuine Unicode input into a 1C managed form. Protocol readback
remains false for this xtest replay path and is documented as a readback artifact; no DB persistence is claimed
because the live proof used `save=false`.

## Next
- Follow-on v2 items remain separate: self-update, optional UIA locator spike, optional host-side launch/stop
  process lifecycle.

## Pointers
- Display-bound code to abstract: `src/qa_mcp/protocol/native_xtest.py`, `src/qa_mcp/protocol/screenshot.py`,
  `src/qa_mcp/protocol/windows.py`.
- Guard + remote-client mode: `src/qa_mcp/mcp_server.py` (`_local_only_tool`, `REMOTE_CLIENT`,
  `DEFAULT_CLIENT_HOST/PORT`); the 8 guarded tools + the unguarded `open_external_processor`.
- Protocol-surface analogs (the TCP "semantic primary"): `write_form_value`, `set_table_cell`,
  `set_reference_field`, `answer_dialog`, `click_command`, `select_table_row`, `read_form_descriptor`,
  `read_list_grid`, `get_window_list_testclient` (same file).
- Delivery: `docker/Dockerfile.thin`, `docker-compose.thin.yml`, `docker/README.md` (model-B section).
- Windows lab: `historical-user@192.0.2.202` (cmd.exe; checkout `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp`) —
  memory [[windows-dev-machine-ssh]].
- Parent: card 119 (`119-2026-06-25-windows-thin-cross-machine-delivery.md`), agenda #2 + its evidence
  `docs/protocol-research/evidence/card119-windows-xmachine-2026-06-26/docker-on-windows-SOLVED.md`.
- Memory: [[qa-mcp-public-delivery-prep]], [[qa-mcp-8-5-platform-support]].

## Log
- 2026-06-26 created from the card-119 agenda-#2 architecture discussion. Decisions FIXED: host-side native agent
  is mandatory (Session 0 isolation + no container→host channel); single static **Go `.exe`**; thin-agent/
  smart-container split (agent = `SendInput`/`BitBlt`/`EnumWindows` only, locate/geometry/Unicode stay in
  Python); `DisplayBackend` abstraction (Local=Linux unchanged / Remote=HTTP to agent) selected by
  `QA_MCP_REMOTE_CLIENT`+`QA_MCP_HOST_AGENT`; transport = HTTP `:8001` via `host.docker.internal` (host-only +
  token); agent runs in interactive session 1; **version/hash handshake v1 = detect-and-instruct, NO
  auto-replace** (self-update `POST /update` deferred to v2); first install = one-time host-side `.ps1` +
  logon Scheduled Task (cannot be container-driven); **UIA deferred to an optional v2 spike** — v1 is a 1:1 port
  of the proven Linux XTEST/scrot stack; fix the `open_external_processor` guard inconsistency. Proposed 4-change
  set recorded for `$opsx-ff`.
- 2026-06-26 (cont.) **SendInput de-risk spike executed LIVE — GREEN.** Faithful run of `write_form_value_xtest`
  with the OS-input primitive swapped to Win32 `SendInput` (ctypes, `KEYEVENTF_UNICODE`) on the Windows lab; a
  `PrintWindow` capture proves the value (incl. Cyrillic) lands in the Валюты `Наименование` object-attribute
  field — the genuine edit the protocol can't commit. v1's riskiest assumption validated. Confirmed 1C uses a
  single `V8TopLevelFrameSDI` window (no child HWNDs → UIA unlikely to help → keep D9) and that foreground
  management is a real agent concern. Evidence + reference driver:
  `docs/protocol-research/evidence/card120-windows-sendinput-spike-2026-06-26/`.
- 2026-06-26 (OPSX ff) Decomposed into four apply-ready OpenSpec changes, moved to `2.todo`, and passed strict
  OpenSpec validation plus matrix preflight for each change.
- 2026-06-26 (OPSX do) Implemented display backend routing, Windows Go host-agent, host installer/handshake,
  Docker docs and tests. Live verification used SSH tunnel to the Windows host-agent/TestClient; after the user
  accidentally closed the first 1C session, only the card-owned `qa-mcp-testclient-120` task was restarted.
  Final proof ran against PID `12812` with agent hash
  `1fe93f6f7e447dacdb536b1d6da3fd4e662e3b2450c045dcfe68e45f0c336d9f`, screenshot
  `abcc27e5f8c491151bdaec8d9be7a6e78b94054b98fc6dd49141488496e7e97b`.
- 2026-06-26 (OPSX archive) Synced specs, passed archive matrix gates and archived all four changes.
