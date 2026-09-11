# Card 98 #2 (remainder) — window enumeration: OS list ≠ 1C-internal window list (investigation)

**Date:** 2026-06-20. **Result:** a decisive lab finding that scopes the protocol-level
`get_window_list_testclient` parity item. The OS-level `get_window_list` (shipped, card 98 #2) and the
protocol-level 1C-internal window list are **genuinely distinct** — not redundant. Building the protocol-level
list needs a new multi-window capture + decode (characterized below); the decode primitive is already in hand.

## Experiment (`tools/protocol-research/testclient_windows_probe.py`, fresh /TESTCLIENT)

1. Boot the native client; `get_window_list(display)` → **3 OS windows** (the main app window
   «Демонстрационное приложение» + a full-screen root + a 1×1 IME helper).
2. `open_list()` → opens `Справочник.Товары` (accepted=True).
3. `get_window_list(display)` again → **still 3 windows, no new title** (count delta 0).
4. Screenshot confirms WHY: the «Товары» list opened as an **MDI tab inside the main window** — the tab bar
   reads «Начальная страница | QA MCP Protocol Fixture V1 | **Товары ×**», with the catalog rows rendered in the
   same X window. No new X11 top-level was created.

## Conclusion

**1C opens lists / cards / forms as MDI tabs — each a 1C-internal window = a `SecondaryFrame` — inside the single
main X11 window.** Therefore:

- **OS-level `get_window_list`** (xdotool) enumerates the client's OS top-level windows (the main app window +
  helpers). It does **NOT** see the open 1C forms/tabs. Correct and useful for "is the client window up / where
  is it", but it is *not* the 1C window list.
- **Protocol-level `get_window_list_testclient`** (the 1C-internal window/tab set — what Vanessa returns) is a
  **genuine, distinct capability**, not covered by the OS list. The visible tabs (Начальная страница / QA MCP
  Protocol Fixture V1 / Товары) are the SecondaryFrames the protocol tracks and that `activate_window` /
  `close_window` already address by ref.

## Path to build it (characterized — primitive in hand, capture missing)

- **In hand:** `native_write._all_secondary_frames(chunks)` already extracts every distinct `SecondaryFrame[<guid>]`
  from a chunk stream (used by the dialog/close/activate decode, card 96). A window list = the set of
  SecondaryFrames currently open, with the active one flagged (the `read_active_window` read already resolves the
  active window's ref).
- **Missing:** the existing read-only capture (`tm-v1-ro-batchQ3`) has only **1 SecondaryFrame** (one tab), so it
  cannot exercise enumeration. Need (a) a session with **several tabs open at once** and (b) the frame/response
  that carries the full SecondaryFrame (window) set — either a dedicated window-list query the manager issues, or
  a UI read whose response enumerates every open SF. The current MCP tools are one-shot (open→act→close on a
  fresh connection — `open_list` opens its own connection and the tab persists in the client after it closes), so
  there is no held multi-tab session that accumulates the SF set; the raw-chunk replay (`open_list`) and the
  template replay (`read_form_descriptor` / the value-read) do not yet compose into one held session.
- **Recipe (next session):** boot the genuine Vanessa manager ([[vanessa-mcp-linux-genuine-manager]]), tcpdump
  the manager↔client port, drive a flow that opens 2–3 tabs then calls Vanessa's window-list step, and decode
  which frame enumerates the SecondaryFrame set ([[genuine-action-capture-recipe]]). Then productize as
  `get_window_list_testclient` reusing `_all_secondary_frames` + the active-window resolve.

## `ui_read_tree` (the other change-2 remainder)

Folds into the **change-1 ANY-form generalization**: `read_form_descriptor` already produces the element
name→value surface (the descriptor); a full element *tree* (types/captions/enabled/readonly hierarchy) is the
same data the no-capture generalization must model (the descriptor re-render frames). Tracked there, not as a
separate decode.

## Artifacts

- Probe: `tools/protocol-research/testclient_windows_probe.py` (+ the MDI-tab screenshot under `runtime/…`,
  not tracked). Parity doc updated (`docs/vanessa-mcp-parity.md`). No code change — investigation + characterization.
