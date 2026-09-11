# 95. The rest (by demand): keyboard, table ops, user messages, reports, async

## Status
5.canceled

## Merged
- 2026-06-17 (board triage): SPLIT — the keyboard + user-message prerequisites folded into **card 96**
  (changes 4, 5); the table-ops / number-date cells / reports / dynamic-list portion folded into **card 97**
  (changes 1–4). The full bucket below is preserved as working detail; cards 96/97 are the active surface.

## Order Index
95

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-17 (next-epic roadmap E5): remaining, lower-frequency (but sometimes prerequisite) actions a full Test
  Manager replacement needs. This is a BUCKET card — split into focused sub-cards when an item is picked up.

## Summary
Capture→decode→productize the remaining native actions as real scenarios demand them. Some are prerequisites for
cards 91/92 (keyboard for dialog confirm/cancel; message-reading for the ПоказатьВыборИзСписка result).

## Acceptance (per sub-item, as pulled in)
- **Keyboard input** — Enter / Esc / Tab / arrows / shortcuts (raw key events vs our protocol activate/SET).
  Decode the key-press command. Needed to confirm/cancel dialogs (card 91) and some navigation.
- **Read user messages** — the messages-to-user window (`Сообщить` / `ПоказатьПредупреждение` text). Vanessa
  asserts «нет сообщений пользователю»; decode the message area in the read sweep (or add a fixture marker).
  Needed by card 92 (PF_ChoiceListDone uses `Сообщить`).
- **Table ops** — delete row (Delete command on PF_TABLE_ITEMS), move up/down, copy, multi-select; and
  **number/date cells** in the grid (only the STRING cell is proven — number/date use a different per-type value
  buffer, like the plain fields).
- **Reports / print / spreadsheet document** (ТабличныйДокумент) — run + read.
- **Dynamic-list ops** — filter, search-string, period, grouping on `ДенамическийСписокИерархия`.

## Notes / constraints
- Each sub-item is an independent capture→decode→productize cycle (methodology: roadmap §"Methodology").
- Keyboard + user-message reading are the highest-leverage (they unblock cards 91/92).
- Split this card into per-item cards (95a/95b/…) when scheduled.

## Plan for the new session (start here)
Read `docs/protocol-research/capture-free-epic-next-roadmap.md` **§E5**. Pull the specific sub-item a real
scenario needs; for keyboard / user-messages, do them alongside cards 91/92 (they are prerequisites).
