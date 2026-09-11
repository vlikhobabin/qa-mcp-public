# Card 97 #2 DATE grid cell — SOLVED via protocol-activate + pure-mouse calendar pick

**Date:** 2026-06-19. **Result:** the date GRID cell (PF_TABLE_DATE) IS settable capture-free — live-verified
end-to-end (row 1 date `10.01.2026 9:00:00` → `15.08.2026 0:00:00`, committed). The protocol text-SET is ruled
out and synthetic keystrokes don't reach 1C's masked date editor; the working path is **protocol-activate the
cell → drive the calendar dropdown by MOUSE**. The reusable date→click geometry is productized + unit-tested; a
fully general MCP tool needs on-screen cell localization (scoped follow-up).

## What works (live-verified)

1. **PROTOCOL** — activate the cell into edit mode: replay the `set_table_cell` `write_block` (activate+SET) for
   `PF_TABLE_DATE` on a HELD connection, WITHOUT the commit/focus-change. The value-SET is rejected (harmless);
   the activate opens the inline date editor — the value is selected and a **calendar dropdown button** appears
   (screenshot `date-hybrid-activated.png`).
2. **MOUSE** — click the calendar dropdown button → the calendar popup opens (a 2-column month list Янв..Дек + a
   Monday-first 6-week day grid; the year spinner is already on the target year). Click the **month**, then the
   **day** (`calendar_month_cell` / `calendar_day_cell` compute the coordinates from the date). The date commits
   to the cell; `Return` finalizes the row edit. Result: the cell shows `15.08.2026 0:00:00`
   (`date-calendar-committed.png`).

All via our engine (protocol) + xdotool **mouse** — no Vanessa, no keystrokes for the date.

## Why mouse, not keystrokes (the keystroke path, ruled out)

- **Protocol text-SET RULED OUT:** `set_table_cell` (raw SET, no Vanessa pre-check) returns committed=False on
  PF_TABLE_DATE even at fitting width, while the number cell commits True. The 1C client won't apply a
  `SetEditText` text value to a date cell. (The numdate «Неподходящий тип» was Vanessa's step pre-check.) A date
  rides the wire as text (`e0 41 81 81 ba 0a "17.06.2026"`) only for the standalone date FIELD (card 86c).
- **Synthetic keystrokes don't reach the masked date editor:** `xdotool type` AND per-`key` digits, in EVERY
  focus state (OS-click, protocol-activate, click-into-editor with a visible cursor), leave the value unchanged;
  BackSpace doesn't clear it. **Decisive control:** in the SAME session/window, `xdotool type` DID land in the
  plain `PF_EDIT_STRING` field (→ "ZZSTRTEST"). So keystroke delivery works — 1C's masked date editor
  specifically ignores synthetic XTEST keys (it likely reads input through a path XTEST doesn't drive). Mouse
  events, by contrast, reach every control (cell select, cursor placement, calendar clicks all land).

## Productized — the calendar geometry (pure, unit-tested)

`src/qa_mcp/protocol/native_xtest.py`:
- `calendar_month_cell(month, *, origin, col_step, row_step)` — (x,y) of a month in the 2-column list (1-6 left,
  7-12 right).
- `calendar_day_cell(year, month, day, *, origin, step)` — (x,y) of a day in the Monday-first 6-week grid:
  `index = weekday(1st) + day-1`, `row=index//7`, `col=index%7`.

Defaults match the fixture under matchbox-maximized 1280x1024 and reproduce the live-verified clicks
(`Авг`→(985,474), `15.08.2026`→(1212,534)); geometry is parameterized for other resolutions/layouts. 5 unit
tests in `tests/test_native_xtest.py`; the live driver is `tools/protocol-research/date_cell_calendar_probe.py`.

## Lab notes / gotchas

- `launch_test_client` runs **bare Xvfb (no WM)** → the 1C window has no keyboard focus and matchbox MAXIMIZES it
  (shifting coordinates). Start `matchbox-window-manager` on the display for focus; mouse clicks land by
  coordinate regardless.
- The protocol activate must send ONLY the `write_block` (activate+SET) — NOT the `commit_block` (the
  focus-change), which would move focus off the cell before the calendar interaction.

## Productization gap (follow-up)

A general `set_table_date_cell` MCP tool needs the cell's **on-screen location** (the calendar-button coords +
the calendar popup origin), which is layout/scroll/resolution-specific — the probe hardcodes them for the fixture.
Discovering the cell on screen (from the form descriptor's cell bounds, or template-matching the calendar button)
is the remaining work to make this a robust, fixture-independent tool. The mechanism + the date→click math are
proven and shipped.

## Artifacts

- Code: `src/qa_mcp/protocol/native_xtest.py` (`calendar_month_cell` / `calendar_day_cell`). Tests:
  `tests/test_native_xtest.py` (+5). Probes: `date_cell_calendar_probe.py` (the working solution),
  `date_cell_xtest_hybrid_probe.py` (keystroke path + the PF_EDIT_STRING control test), `date_cell_probe.py`
  (protocol-SET ruled out), `date_cell_render_probe.py` (grid screenshot).
- Screenshots: `date-calendar-{open,picked,committed}.png` (the working pick),
  `date-hybrid-control-string.png` (keystrokes land in a plain field), `date-form-grid.png` (the grid).
- Decode bytes: `genuine-multiaction-clean-20260617` (standalone PF_EDIT_DATE SET, text on the wire).
