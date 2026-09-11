# 93. Object navigation: open_card + close form + activate/switch window (capture-free)

## Status
5.canceled

## Merged
- 2026-06-17 (board triage): folded into **card 96** (Capture-free interaction breadth) as **change 3**
  (object navigation). The full plan below is preserved as working detail; card 96 is the active surface.

## Order Index
93

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-17 (next-epic roadmap E3): drilling into list items (open a record card), closing forms, and switching
  between open windows are basic navigation primitives a test manager needs — none are productized.
- Low-hanging: `navigation.render_open_card_command` and `render_select_row_command` are DECODED (card 74/78
  captured-command path) but NOT live-verified capture-free against the fixture. The read path has a window list
  (`get_window_list_testclient`-equivalent) but no ACTIVATE/CLOSE.

## Summary
Productize object navigation capture-free: `open_card` (open the selected row's record form), `close_window`
(close the active window or by title), `activate_window(title)` (bring a window to front / make it active).

## Acceptance
- `open_card`: from the embedded dynamic list `ДенамическийСписокИерархия` (Catalog.Товары), live-verify opening
  a Товары item CARD (double-click / «Изменить» a row → the data form opens). Decode the open-card command
  (likely a list command + row ref → a DATA form `e1cib/data/Справочник.Товары?ref=…` or a form-open; new
  SecondaryFrame). MCP tool `open_card`.
- `close_window`: capture closing a window (× / «Закрыть» / Esc) → decode → MCP tool `close_window`.
- `activate_window`: capture switching between two open windows → decode the activate command → MCP tool
  `activate_window(title)`.
- Each verified (no Vanessa) via the active-window caption / nav-link read-back (we already read
  `get_active_window_data`-style). Unit tests + evidence note.

## Notes / constraints
- `open_card` opens a new data form (ref = GUID); the row's ref must be addressable from the open list.
- Window identity/handle on the wire (close/activate by which window); close on the ACTIVE vs a NAMED window.
- Polygon is ready (the embedded dynamic list + multiple windows after open_list/open_card).

## Plan for the new session (start here)
Read `docs/protocol-research/capture-free-epic-next-roadmap.md` **§E3**.
1. Live-verify `open_card`: replay/synthesize the open-card command from a Товары-list capture (reuse
   `render_open_card_command` or capture fresh); screenshot/caption read-back the opened card.
2. Capture close + activate-window under tcpdump; decode; productize `close_window` / `activate_window`.
