# 88. Element-type & interaction coverage

## Status
5.canceled

## Merged
- 2026-06-17 (board triage): most of this card's scope (number/date/checkbox/choice/table-cell read+act+
  read-back) is ALREADY DONE via card 90. The residue (waits/asserts) folded into **card 97** (change 5).
  The full plan below is preserved as working detail; card 97 is the active surface.

## Order Index
88

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-16: roadmap card 82, stage 6. The fixture proved string input/commit + basic nav/click; a real test
  manager must drive the full UI surface.

## Summary
Extend native read+act coverage across the element/interaction types real configs use, on top of the
capture-free synthesis (86) and introspection (87): numbers, dates, checkboxes/flags, choice lists & dropdowns,
catalog/reference pickers, tables (row add/edit/select), command-interface navigation, modal dialogs, and
waits/asserts.

## Acceptance
- For each type, a native (no-Vanessa) read + act + read-back-assert works live: edit-number, edit-date,
  toggle-checkbox, pick-from-choice-list, pick-catalog-ref, table row add/edit/select, open a section/command,
  answer a modal dialog, wait-for-condition, assert element value/state.
- Variable-length and field-declared-length limits respected (extends the card-80 fixed-width retarget).
- Driven by the V1-V4 fixture surface where possible (`PF_*` controls) + at least one real-config example per
  type.

## Change Set
- none yet

## Related
- card 80 (string write), card 86 (synthesis), client fixtures V1-V4 (board 4.done),
  `tools/protocol-research/action-manifests/`, `src/qa_mcp/scenario/actions.py`.

## Log
- 2026-06-16T00:00:00Z card created.
