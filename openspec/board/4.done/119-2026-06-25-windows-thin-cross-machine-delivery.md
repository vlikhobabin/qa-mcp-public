# 119. Windows delivery — model B: thin cross-machine (decision + next-session agenda)

## Status
4.done

## Order Index
119

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-25 architecture discussion. Continues the public-delivery prep (memory [[qa-mcp-public-delivery-prep]],
  point 4 "Windows-first delivery") and builds on the existing Docker delivery (`Dockerfile`, `docker/`).
- The 8.5 multi-platform epic (112) is delivered; this card is the **Windows packaging direction**, decided.

## Decision (FIXED 2026-06-25)
Adopt **model B — thin cross-machine** as the Windows delivery, alongside (not replacing) model A.

- **Model A (all-in-container, already built + E2E-verified on Linux):** the image carries qa-mcp + X11 toolchain
  + 1C thick-client libs; it MOUNTS a **Linux** 1C platform + infobase + **Linux license** and runs the
  TestClient under Xvfb *inside* the container. Full tool surface (incl. XTEST). **Windows pain:** a Windows 1C
  is a Windows build a Linux container can't run, and the Windows license/identity does not carry into the Linux
  container → needs a Linux 1C + a network/HASP license. That's the blocker model B removes.
- **Model B (thin cross-machine, THIS card):** the user's **installed Windows 1C** runs the TestClient on the
  Windows host; the **thin** qa-mcp container (Python only — no 1C libs, no Xvfb) connects over **TCP** and
  drives the protocol surface. MCP still served over **HTTP :8000** (agent connects like Context7).

## Architecture (model B)
```
Windows host (Codex Desktop + installed, LICENSED 1C)
  └─ launcher (.bat/.ps1/mini-service): 1cv8 ENTERPRISE /TESTCLIENT -TPort 15381 /IBConnectionString "<user base>"
        (file / server / networked base — the connection string is the user's; license already valid on Windows)
        ▲ TCP :15381
Docker Desktop (WSL2, Linux) ─ THIN qa-mcp container
  └─ qa-native-mcp (HTTP :8000)  →  connects to host.docker.internal:15381  →  drives the protocol surface
Codex/agent  →  http://localhost:8000/mcp   (type:"http", like Context7)
```
Key change vs today: qa-mcp must gain a **"remote-client" mode** — do NOT boot a local `/TESTCLIENT`; connect to
a pre-launched client at `host:port`. The tools already take `host`/`port`; the change is to skip the local
`launch_test_client`/lifecycle path and mark the display-bound tools as "local-display only".

## Tool classification (verified against the code 2026-06-25)
> ✅ **2026-06-26 (session 2) — RESOLVED.** The protocol surface **DOES** drive a Windows-built client from a
> Docker container as-is, with **no protocol change, no Windows capture, no networking workaround**. Session-1's
> "protocol blocked" was a **cross-machine-LAN transport artifact**, not a protocol/OS difference: the client
> only brushes off a *genuinely remote* peer (`66 53 b2 a6` + EOF); a **loopback-origin** peer — 127.0.0.1 OR
> Docker Desktop `host.docker.internal` (its backend originates the forwarded connection from the Windows host
> itself) — gets the full 210-byte handshake. Proven end-to-end: thin model-B image `qa-mcp-thin` (261 MB,
> no 1C libs / no X11) → MCP-HTTP :8000 → `read_form_descriptor(host="host.docker.internal", port=15381)` →
> live form fields. Full evidence: `docs/protocol-research/evidence/card119-windows-xmachine-2026-06-26/docker-on-windows-SOLVED.md`.
> The split below now holds in practice (protocol surface = served; the display/XTEST subset still needs the
> host-side agent, agenda #2).

**Works cross-machine (pure protocol / TCP):** read_form_descriptor, assert_form_value/assert_data, the scenario
runner (run_scenario/run_feature), navigation/open, and the PROTOCOL-replay writes — set_table_cell, set_choice,
toggle_checkbox, click_command, set_reference_field, open_list, search_list, write_form_value, choose_from_list,
answer_dialog, open_card, close_window/activate_window (protocol), measure (debug-protocol coverage/perf), and
the OData data-layer. → the majority of the surface, INCLUDING much data entry.

**Breaks cross-machine (needs a LOCAL X11 display matching the render):** write_form_fields_by_label
(screenshot-localize + XTEST), set_table_date_cell (calendar clicks), write_form_value_xtest, send_keys (XTEST),
capture_screenshot / safe_form_screenshot / get_window_list (X11). Reason: Windows renders to **GDI**; qa-mcp's
XTEST + screenshots are **X11** — the remote Windows render is not in the container's X server.

## Pros
- ✅ **Uses the user's existing Windows 1C + Windows license** — removes the Linux-platform AND Linux-license
  gotchas (the single biggest Windows blocker).
- ✅ **Thin container** (qa-mcp + Python only) — smaller, simpler, no 1C libs / Xvfb / font stack.
- ✅ Works with **any base** the user can point 1C at (file / server / networked).
- ✅ Same **HTTP-MCP** UX (agent config = 3 lines, like Context7); no change for the agent side.
- ✅ Protocol surface — including most data entry — works as-is over TCP.

## Cons
- ❌ **Loses the XTEST/screenshot subset** (visual writes: date-in-calendar, label-localization; screenshot
  evidence; OS window list). Partially covered by protocol analogues (set_table_cell / write_form_value), but
  the purely-visual ones are lost until a Windows agent exists (see agenda #2).
- ❌ Requires a **Windows-side launcher** to start the TestClient (a small extra component the user runs).
- ❌ **Cross-machine networking**: the container must reach the Windows host's TPort (`host.docker.internal`,
  firewall, the client must listen on a reachable interface, not just 127.0.0.1).
- ❌ **Evidence/screenshots** need a different mechanism (Windows-side) — affects the live-regression evidence
  bundle + the verification matrix artifacts.
- ❌ Two delivery models to maintain (A for Linux hosts, B for Windows).

## Cross-machine lab findings (2026-06-26) — agenda #1 executed
Full evidence: `docs/protocol-research/evidence/card119-windows-xmachine-2026-06-26/findings.md`.
Lab: `historical-user@192.0.2.202` (Windows 10.0.26200); target `C:\1C_BASES\vanessa_client` @ **8.3.27.2130**
(byte-identical config+platform to the Linux lab the bundled captures came from — the ideal control).

- ✅ **Transport PROVEN.** `1cv8 /TESTCLIENT -TPort 15381` binds **`0.0.0.0:15381`** (IPv4+IPv6), i.e.
  LAN-reachable, not 127.0.0.1-only. The client must be launched in the user's **interactive session 1**
  (a session-0/SSH launch binds then dies); a `schtasks /RU historical-user /IT` task does this. Inbound 15381 is
  firewall-**dropped** by default → one `New-NetFirewallRule` opens it. The Linux box then reaches the client
  over TCP and gets the protocol greeting. → model B's transport story holds.
- ❌ **Protocol blocked at the bootstrap.** The 3 read-only `ui` regression checks → 0/3, all error at the
  bootstrap (`Connection reset by peer`). Greeting is **identical** to the Linux client (`53 f5 c6 1a 7b`) and
  my synth manager frames match the bundled capture byte-for-byte — but the **Windows** client replies to
  manager frame 1 with a 4-byte token (`66 53 b2 a6`) + EOF, where the **Linux** client replies with a 210-byte
  JSON handshake (then 450/262 for frames 2/3). Ruled out: version mismatch (wrong version → same reset),
  session-constant GUID/token (randomize → same), inter-frame timing (back-to-back → no advance), and
  single-connection poisoning (fresh client → same). **The Linux-captured bootstrap does not drive a
  Windows-built client** — the OS-axis analogue of the epic-112 version finding.
- **Therefore the real model-B blocker** is a **genuine Windows manager↔client handshake capture** →
  platform-keyed bootstrap + manager-frame templates (the `_bundled/8.3/…` layout is already keyed, so a
  `windows` key slots in). This is a prerequisite change, ahead of/alongside the remote-client mode.

## Result
- **✅ DELIVERED + PRODUCTIZED (2026-06-26).** Model B (thin cross-machine) is PROVEN end-to-end on the Windows
  lab — the thin image drives the host TestClient via `host.docker.internal`; the session-1 "PROTOCOL BLOCKED"
  was a cross-machine LAN peer-address artifact, NOT a protocol/OS difference (loopback-origin peers like Docker
  Desktop's `host.docker.internal` get the full handshake). No Windows capture needed; the capture-runbook task
  was dropped. Shipped: `docker/Dockerfile.thin` (~260MB) + `QA_MCP_REMOTE_CLIENT` mode + `docker-compose.thin.yml`
  + README model-B section (commit `02bf355`). Agenda #2 (Windows host input/screenshot agent) became card **120**
  (4.done). Evidence: `docs/protocol-research/evidence/card119-windows-xmachine-2026-06-26/`.

## Next-session agenda (NEW SESSION — think these through)
> **Agenda #1 status (2026-06-26 session 2): DONE + GREEN.** Model B works end-to-end on the Windows lab — the
> thin image drives the host TestClient via `host.docker.internal`. The "capture the Windows handshake" task
> (`capture-runbook.md`) is **NOT needed and is dropped** — there is no Windows-specific handshake; the
> session-1 block was the LAN peer-address artifact. Remaining work is **productization + agenda #2** (below),
> not protocol. Evidence: `…/docker-on-windows-SOLVED.md`.

**1. How to stand up + test a Windows lab.** We have a Windows box over SSH: `historical-user@192.0.2.202` (cmd.exe
shell; qa-mcp checkout at `C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\qa-mcp` — memory
[[windows-dev-machine-ssh]]). Work out:
   - locate/confirm the installed Windows 1C + a test base; script a launcher that starts
     `1cv8 ENTERPRISE /TESTCLIENT -TPort <p> /IBConnectionString "<base>"` and binds the TPort to a reachable
     interface;
   - reach that TPort from a Linux box / a thin qa-mcp container over TCP (`host.docker.internal` / the LAN IP);
   - run qa-mcp's **protocol** tools against it (read_form_descriptor, assert, set_table_cell, click_command,
     run_scenario) and confirm GREEN — this validates model B's protocol surface end-to-end.

**2. How to recover the lost (XTEST/screenshot) functionality with a Windows-native agent.**
> **Broken out into card [120] (`120-2026-06-26-windows-host-input-screenshot-agent.md`), 2026-06-26.** All
> decisions fixed there: host-side **Go `.exe`** agent behind a `DisplayBackend` abstraction (thin agent =
> `SendInput`/`BitBlt`/`EnumWindows`; locate/geometry stays in Python), HTTP `:8001` via `host.docker.internal`,
> interactive session 1, **version-handshake v1 = detect-and-instruct (no auto-replace; self-update v2)**, UIA
> deferred to an optional v2 spike, + fix the unguarded `open_external_processor`. The notes below are the
> original brainstorm, superseded by card 120.

Likely Windows has
the equivalents, or we write a small agent (Go or C++) that qa-mcp calls over a tiny RPC (HTTP / named pipe /
TCP) — the Windows analogue of shelling out to xdotool/scrot on Linux:
   - **input**: Win32 `SendInput` (low-level) or **UI Automation (UIA)** (semantic — find a control by name/label
     and click/type it, the Windows analogue of locate_text+xtest_click — possibly MORE robust than OCR);
   - **screenshots**: `BitBlt`/`PrintWindow` or `Graphics.CopyFromScreen`; window enumeration via `EnumWindows`;
   - **design**: a "display backend" abstraction in qa-mcp (Linux = XTEST/scrot, Windows = the agent) so the
     same MCP tools work on both — the agent runs ON the Windows host (where the render is), qa-mcp in the
     container calls it. Pick Go (single static binary, easy to ship) vs C++ (closest to Win32/UIA).
   - decide scope: which visual tools to port first (label-localization write, screenshot evidence, date-cell).

## Acceptance (for when this card is worked)
- Model B documented (this card) + a "remote-client" mode in qa-mcp (connect to host:port, no local boot).
- Protocol surface live-verified cross-machine against the Windows lab (the regression CORE, protocol subset).
- A plan (and ideally a prototype) for the Windows input/screenshot agent that restores the visual subset.

## Pointers
- Existing delivery: `Dockerfile`, `docker/README.md` (model A + the Windows/network-license note),
  `docker/run-host-platform.sh`, `docker/mcp.json.example`, `docker/docker-compose.yml`.
- Display-bound code to abstract: `src/qa_mcp/protocol/native_xtest.py`, `src/qa_mcp/protocol/screenshot.py`.
- Lifecycle (where the local-boot vs remote-connect split lives): `src/qa_mcp/protocol/lifecycle.py`,
  `mcp_server.launch_test_client`.
- Windows lab: `historical-user@192.0.2.202` ([[windows-dev-machine-ssh]]).
- Memory: [[qa-mcp-public-delivery-prep]], [[qa-mcp-8-5-platform-support]].

## Log
- 2026-06-25 created. Decision FIXED: model B (thin cross-machine) for Windows. Pros/cons + tool classification
  recorded. Two open questions handed to the next session: (1) Windows lab on historical-user@192.0.2.202, (2) the
  Windows input/screenshot agent (Go/C++) to recover the XTEST/screenshot subset.
- 2026-06-26 agenda #1 executed against the Windows lab. **Transport PROVEN** (TPort binds 0.0.0.0:15381,
  session-1 launch via schtasks /IT, inbound firewall rule, Linux reaches it + gets the greeting). **Protocol
  BLOCKED:** the Linux-captured bootstrap does not drive the Windows-built TestClient (frame-1 reply is 4 bytes
  + EOF vs the Linux client's 210-byte JSON; not version/constant/timing/exhaustion). New real blocker = a
  genuine Windows handshake capture → platform-keyed bootstrap/templates. Evidence:
  `docs/protocol-research/evidence/card119-windows-xmachine-2026-06-26/findings.md`. Lab left clean (no client
  running; firewall rule + `C:\Users\historical-user\TEMP\qatc_launch.ps1` kept as model-B artifacts).
- 2026-06-26 (cont.) started the **genuine Windows handshake capture** (user picked the custom-`.epf`-manager
  mechanism). Resolved the 1C testing API (`ТестируемоеПриложение` + `/TESTMANAGER` + constructor host/port),
  authored the minimal manager `.epf` SOURCE (BSL connects to the proxy + reads + exits; EDT project
  `qa_xmachine_mgr`, exported to Designer XML). Build blockers hit + partly cleared: Linux Designer rebuild
  fails on a libgcc/libhwy conflict (→ build on Windows); Windows `tar` mojibake'd the Cyrillic form name
  (→ renamed to Latin `MgrForm`); remaining blocker = the hand-authored minimal form's XDTO structure (seed
  from a real `.epf` next). Full continuation steps (build + the 3-process capture run + extract + platform-keyed
  bundle + verify): `docs/protocol-research/evidence/card119-windows-xmachine-2026-06-26/capture-runbook.md`.
- 2026-06-26 (session 2) **MODEL B PROVEN END-TO-END — blocker DISSOLVED.** The session-1 "protocol blocked"
  was a cross-machine-LAN **peer-address** artifact, not a protocol/OS difference: the client brushes off a
  genuinely remote peer (`66 53 b2 a6` + EOF) but gives the full 210-byte handshake to a **loopback-origin**
  peer — 127.0.0.1 OR Docker Desktop `host.docker.internal` (its backend originates the connection from the
  Windows host). Ladder, all GREEN: (1) Windows-native loopback `winloop_probe.py 127.0.0.1 15381` → full
  bootstrap 1..10, received 2064 B; (2) container `read_form_descriptor host.docker.internal 15381` → 43 live
  fields; (3) **thin model-B image `docker/Dockerfile.thin` → `qa-mcp-thin` (261 MB, no 1C libs/X11)** serving
  MCP-HTTP :8000 → MCP client (in-container + Windows-host via `http://127.0.0.1:8000/mcp/`) → 61 tools,
  `read_form_descriptor(host="host.docker.internal", port=15381)` → live form. The Windows-handshake-capture
  task is dropped (not needed). Gotchas captured: tools→`host.docker.internal`; agent→`127.0.0.1` not
  `localhost` (IPv4 vs IPv6); client in session-1 via `schtasks /IT`; `QA_MCP_PLATFORM_VERSION` = host version.
  Full evidence: `docs/protocol-research/evidence/card119-windows-xmachine-2026-06-26/docker-on-windows-SOLVED.md`.
  New artifact: `docker/Dockerfile.thin`. Remaining: productize (compose/README + a "remote-client" lifecycle
  flag that marks display tools local-only) + agenda #2 (Windows input/screenshot agent for the XTEST subset).
- 2026-06-26 agenda #2 decomposed into its own detailed card **[120]**
  (`120-2026-06-26-windows-host-input-screenshot-agent.md`). Per-tool loss analysis (8 guarded +
  `open_external_processor` unguarded bug → ~3 Win32 primitives) + 10 fixed decisions + a 4-change set recorded
  there. Key choices: Go `.exe` host agent, `DisplayBackend` abstraction, version-handshake **v1 =
  detect-and-instruct (no auto-replace)**, self-update + UIA deferred to v2. This card's productization is done;
  the display-subset recovery now lives in card 120.
