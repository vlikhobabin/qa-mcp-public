# Keyboard input — decision record (card 96 change 4)

**Status:** DECISION + thin productization. **Date:** 2026-06-20. Closes card 96 change 4 (was card 95's
keyboard portion).

## The finding: 1C keyboard input is OS-level, not a protocol command

Card 96 change 4 set out to "decode the key-press command (raw key events vs the protocol activate/SET)". The
decisive result — established by the card-98 write-commit deep dive — is that **there is no manager→client
key-press frame to decode**:

- Vanessa's keyboard input is the **VanessaExt external component** performing **OS-level input inside the
  client**. The typed key/value appears in NO manager→client protocol frame (proven on the wire: a synthetic
  edit-text SET commits a FORM attribute but NOT an OBJECT attribute; the genuine commit needs the real
  client-side keystroke that the protocol does not carry — see `openspec/changes/archive/**` card-98 change-5
  notes and `docs/protocol-research/evidence/card98-xtest-hybrid-2026-06-18/`).
- So a "send a key over the protocol" command is not something the capture-free engine can replay — the
  protocol simply does not transport raw key events. Capturing a key-press would yield an empty manager stream.

This mirrors `agent_runtime` (card 98 change 4): an accepted **non-scope of protocol decoding**. Keyboard is
delivered the way Vanessa delivers it — at the OS level.

## How the keyboard INTENTS are covered

A test manager needs keyboard for a handful of intents; each already has a capture-free path:

| Intent | Keys | Capture-free coverage |
| --- | --- | --- |
| Confirm / cancel a dialog | Enter / Esc | `answer_dialog` (window-level `88 82 81` command on the dialog SecondaryFrame) |
| Commit a field edit | Tab | the focus-change commit (protocol) / `send_keys(["Tab"])` (OS) |
| Navigate rows | Up / Down | `select_table_row`, `read_list_grid` (next-row), `read_list_row(where=…)` |
| Save | Ctrl+S | `click_command` «Записать» (protocol) / `send_keys(["ctrl+s"])` (OS) |
| Raw / masked-control keys | any chord | **`send_keys`** (XTEST escape hatch) |

## The deliverable: `send_keys` (XTEST)

`send_keys(keys, display)` sends a sequence of raw OS key chords (Enter/Esc/Tab/arrows/shortcuts) to the focused
1C client window via XTEST (xdotool) — the **same `xtest_key` primitive that is DB-verified** in
`write_form_value_xtest` (Tab commits an object attribute; Ctrl+S = Записать persists to the DB, card 98).
`write_form_value_xtest` now routes its Tab/Ctrl+S through `send_keys`, so the shipped DB-verified write path
exercises this exact primitive end-to-end.

- Engine: `qa_mcp.protocol.native_xtest.send_keys` (over `xtest_key`).
- MCP tool: `send_keys(keys, display, settle_sec)`.
- PREREQ: a launched client (`run_native_test_client(display=":89", port=…)`) + a window manager (matchbox) so
  the client window is laid out and focused; keys go to the focused window.

## Scope / honesty

- `send_keys` is the raw-key escape hatch. Prefer the protocol tools (`answer_dialog`, `select_table_row`,
  `click_command`, `read_list_*`) for the common intents — they are deterministic and capture-free without an
  X display dependency.
- Keyboard remains OS-level by nature: `send_keys` needs the client's Xvfb display (like the XTEST write
  hybrid), not just the protocol socket. This is the same boundary as object-attribute writes.
