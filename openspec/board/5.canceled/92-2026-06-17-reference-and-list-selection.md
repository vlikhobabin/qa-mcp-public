# 92. Reference selection / choice-from-list (pick a value & commit, capture-free)

## Status
5.canceled

## Merged
- 2026-06-17 (board triage): folded into **card 96** (Capture-free interaction breadth) as **change 2**
  (reference / value selection). The full plan below is preserved as working detail; card 96 is the active surface.

## Order Index
92

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-17 (next-epic roadmap E2): "select a Контрагент / Номенклатура / Склад" is the single MOST FREQUENT
  action in 1C business forms, and it is NOT productized. `open_list` only OPENS a list window — we cannot yet
  PICK a value and have it land in a field.
- Fixture polygon is PARTLY real: `PF_SHOW_CHOICE_LIST` IS a real modal
  (`ПоказатьВыборИзСписка(Оповещение, СписокЗначений[A,B,C])` → pick → `PF_ChoiceListDone` →
  `Сообщить("PF_CHOICE=" + value)`). ⚠ the result surfaces as a **user message** (`Сообщить`) → this card also
  needs message-reading (card 95) OR a clean marker field. `Контрагент` field type is UNVERIFIED (may be a plain
  String, not a true `СправочникСсылка`).

## Summary
Productize value/reference selection capture-free: `choose_from_list(value)` (value-list / menu) and
`set_reference_field(field, value)` (compose `open_list` + `select_table_row` + a confirm). Reuse the shipped
open_list + select-row-by-value + click_command.

## Acceptance
- Verify `Контрагент` / `ПолеСоСпискомВыбораСтрока` types; if no true reference field exists, add a form attribute
  `СправочникСсылка.Товары` with a choice button + a readable result marker (PF_CHOICE_RESULT / PF_REF_RESULT).
  Deploy via manual `ibcmd`.
- Genuine captures: (a) `PF_SHOW_CHOICE_LIST` → pick an item; (b) reference-field choice → open the Товары
  catalog → select a row → confirm → the ref lands in the field.
- Decode documented: the value-list/menu pick (likely an `e0 4b 5x` activate / row-select-by-value on the dialog
  list) and the reference "confirm selection" (double-click / Выбрать / Enter that returns the ref to the field).
- MCP tools `choose_from_list` + `set_reference_field`, unit tests, evidence note.
- Live-verified (no Vanessa): the target field reads back the chosen presentation (read_form_value) or the marker.

## Notes / constraints
- Reference value is a GUID shown as a presentation string; read-back gives the presentation.
- Multi-step sub-window flow (open choice → list → select → confirm) — compose existing primitives where possible.
- Depends on / pairs with card 95 (reading `Сообщить` user messages) for the PF_SHOW_CHOICE_LIST result, unless a
  marker field is added.

## Plan for the new session (start here)
Read `docs/protocol-research/capture-free-epic-next-roadmap.md` **§E2**.
1. Inspect `Контрагент`/`ПолеСоСпискомВыбораСтрока` types in the fixture form; decide whether to add a real
   reference field + a result marker; deploy if needed.
2. Capture PF_SHOW_CHOICE_LIST pick + reference selection under tcpdump (genuine manager).
3. Decode the pick + confirm; productize (reuse open_list + select_table_row + click_command); live-verify.
