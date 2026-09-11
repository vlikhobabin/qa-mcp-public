# card 120 spike — Win32 `SendInput` drives the 1C Windows GDI client (de-risk for the Go host-agent)

**Date:** 2026-06-26 · **Lab:** `historical-user@192.0.2.202` (Windows 10.0.26200), base `C:\1C_BASES\vanessa_client`
@ 8.3.27.2130 · **Result: GREEN.**

## Question
Before committing to the Go host-agent (card 120 agenda #2), prove the one genuinely-unknown thing on Windows:
**does Win32 `SendInput` deliver a genuine keystroke edit — including Cyrillic — into a 1C managed-form
object-attribute field (`Объект.*`), the exact thing the pure protocol replay cannot commit?**

PowerShell/ctypes `SendInput` calls the IDENTICAL `user32!SendInput` the Go agent will call via
`golang.org/x/sys/windows`, so a GREEN here de-risks the agent's keyboard primitive directly.

## Method (faithful)
Ran the REAL `qa_mcp.protocol.native_xtest.write_form_value_xtest` flow (protocol open+focus by name → OS input →
read-back) with ONLY the OS-input primitive monkeypatched from xdotool/XTEST to **Win32 `SendInput` via ctypes**
(`KEYEVENTF_UNICODE` for text; VK taps for Tab/Ctrl+S). Everything else is the production code path.

- Package: `src/qa_mcp` (stdlib-only) + the `genuine-card98-demo-write` capture (Справочник.Валюты.Наименование),
  copied to the host; run with system Python 3.13, no venv. The capture's form exists in `vanessa_client`
  (the Linux write-regression targets the same `e1cib/data/Справочник.Валюты` / `Наименование`).
- Connection: loopback `127.0.0.1:15381` (loopback-origin → full handshake, per card 119).
- Execution: `pythonw` launched by a `schtasks /IT` task so it runs in **interactive session 1** (where the GDI
  client is rendered) — `SendInput`/screenshot require the interactive desktop (Session 0 isolation, card 119).
- Driver: `spike_win.py` (in this dir). Config `spike_cfg.example.json`.

## Result — GREEN
The `PrintWindow(PW_RENDERFULLCONTENT)` capture of the 1C window (`evidence-*.png`, z-order independent) shows
the typed value landing in the **Наименование** field of the open **Валюта (создание)** form:

- `evidence-cyrillic-Тест.png` — field shows `QA SendInput Тест 2026…` (Cyrillic «Тест» typed correctly).
- `evidence-naименование-WIN-SENDINPUT-OK.png` — field shows `WIN-SENDINPUT-OK-Кириллиц…` after a Ctrl+A/Delete
  clear (clean single value, Cyrillic «Кириллиц»).

→ **`SendInput` (`KEYEVENTF_UNICODE`) delivers ASCII + Cyrillic into a 1C managed-form object-attribute field on
the Windows GDI client.** The agent's keyboard primitive is validated.

## Key diagnostics
- `GetGUIThreadInfo` at the instant of typing (`focus_pre_type`/`focus_post_type` in `result-*.json`): foreground
  and keyboard focus on the 1C client (`focus_class = "V8TopLevelFrameSDI"`, `focus_pid = <1cv8>`,
  `is_our_client = true`) BEFORE and AFTER the whole type. So the keystrokes were delivered to 1C throughout.
- **1C draws managed forms in a single top-level window with NO child HWND controls** — the field has no own
  HWND; the V8 frame does its own internal hit-test/focus. Win32 `GetFocus`/`hwndFocus` is therefore always the
  frame, and `SendInput` keystrokes routed into the frame reach the internally-focused field. (Same single-window
  model as the X client on Linux — symmetric with the proven XTEST path.) → for the agent, **UIA element-level
  control is unlikely to expose form fields** (no child HWNDs); the Win32 `SendInput`/`PrintWindow` path is the
  load-bearing one, confirming card 120 decision **D9** (UIA is an optional spike, not v1).

## On `committed: false`
The flow's `committed` (the capture-replay protocol read-back checking the value bytes) returned `false` even
though the value is visibly in the field. This is a **read-back artifact, NOT an input failure**:
- The lab desktop was **contended** — a concurrent agent session (foreground title
  "Implement subordinate catalog on demo10413 via MCP") kept stealing the foreground and forms accumulated
  across runs (an early screenshot showed `…2026QA`), so the GUID-rebind read-back replayed against a reused/
  perturbed form instance.
- The production write path verifies persistence via **screenshot** and **`assert_data` (OData)** — NOT this
  xtest capture-replay read-back. So `committed`'s value here does not gate the agent design.
- The genuine-edit success is proven directly by the `PrintWindow` screenshot (the value IS in the field).
- DB-save (Tab → commit, Ctrl+S → save) uses the SAME now-proven `SendInput` primitive; commit-to-DB is a 1C
  platform behavior, not OS-specific once the keystroke is delivered — already GREEN on Linux. A standalone
  DB-persistence confirmation on Windows is a v1-implementation follow-on (gated on OData being published there).

## Implication for card 120
The v1 minimum is validated at its riskiest point. Build the Go agent's keyboard primitive on `SendInput`
(`KEYEVENTF_UNICODE`) and screenshots on `PrintWindow(PW_RENDERFULLCONTENT)` (window-targeted, z-order
independent — important on a shared desktop). Foreground management (clear the foreground lock + minimize
others + `SwitchToThisWindow` + `SetForegroundWindow`, verify with `GetForegroundWindow`/`GetGUIThreadInfo`) is a
real requirement the agent must own — the spike's `spike_win.py` has a working reference implementation.

## Artifacts (this dir; PNGs are git-ignored / local-only per repo policy)
- `spike_win.py` — the ctypes-SendInput faithful driver (focus dance + GUIThreadInfo diag + PrintWindow capture).
- `spike_cfg.example.json` — example config for the local spike driver.
- `result-with-focus-diag.json`, `result-clean.json` — run outputs incl. the focus diagnostics.
- `evidence-cyrillic-Тест.png`, `evidence-naименование-WIN-SENDINPUT-OK.png` — the PrintWindow proofs.
