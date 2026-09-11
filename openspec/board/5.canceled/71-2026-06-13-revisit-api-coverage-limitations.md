# 71. Revisit API-coverage limitations (next version)

## Status
5.canceled

## Cancellation
- 2026-06-17 (board triage): the 7 blocked `safe_ui_action` members are artifacts of the **superseded
  Vanessa-driven capture pipeline**. The project pivoted to **capture-free synthesis** (cards 80/86/90):
  actions are now built from the live form descriptor + per-element-TYPE genuine templates, not captured
  per-flow and replayed. Re-evaluate any residual coverage gaps in that model under the forward
  coverage/parity work, not in this old framing. Evidence preserved below as an audit trail.

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-13 breadth pass: Phase 1 (`mutation`) and Phase 2 (`safe_ui_action`) completed
- `docs/protocol-research/api-coverage-limitations.md`

## Summary
While completing the `mutation` (9/9 accepted) and `safe_ui_action` (22/29 accepted)
buckets, 7 `safe_ui_action` members could not be accepted through the current
Vanessa-driven capture pipeline. They are honest `candidate` rows — the protocol
members are real, but we cannot build a clean reference capture for them yet. **For a
future qa-mcp version**, not this one. (Phase 1 had one analogous case —
`TestedFormDecoration.Click`, which needed a hyperlink decoration — and it was already
resolved via the `Расширение1` fixture, so Phase 1 has zero candidates.)

Three root causes (details + evidence in `docs/protocol-research/api-coverage-limitations.md`):
- **Class A — no Vanessa step driver (5):** `GotoStartPage`, `GotoNextWindow`,
  `GotoPreviousWindow`, `ChooseUserMessage` (no step exists), and `TestedForm.Activate`
  (`я активизирую форму` drives window Activate, not the form). Config-independent.
- **Class B — platform rejects the action (1):** `TestedFormTable.Expand` — `Развернуть`
  throws on a collapsed dynamic-list group row (Collapse works; form-group Expand works).
- **Class C — no suitable element in the demo (1):** `TestedFormButton.Activate` — no
  `активизирую кнопку` step and no body-level button to target (command-bar buttons are
  not found by the finder).

## Acceptance
- A future-version plan exists to drive the 5 Class-A members via custom step wrappers
  (VAExtension / project step library) that call the methods directly.
- A static-tree (`ДеревоЗначений`) fixture form is added so `TestedFormTable.Expand`
  (Class B) can be captured.
- A body-level button fixture is added so `TestedFormButton.Activate` (Class C) can be
  captured.
- Each unblocked member goes through capture×2 → probe → probe-ordinal → promote and
  moves from `candidate` to `accepted_reviewed` in `scope-tracker.md`.

## Change Set
- none yet

## Verify
- not started

## Archive
- not started

## Related
- `docs/protocol-research/api-coverage-limitations.md`
- `docs/protocol-research/evidence/safe-ui-corpus/window-members-blocked/findings.md`
- `docs/protocol-research/evidence/safe-ui-corpus/activate-no-driver/findings.md`
- `docs/protocol-research/evidence/safe-ui-corpus/tovary-hierarchy-batch/`
- `docs/protocol-research/api-inventory/mutation-evidence-map.json` (candidate rows)
- `docs/protocol-research/breadth-roadmap.md`

## Result
not started

## Next
- triage

## Change Plan Notes
When the card moves to `2.todo/`, replace this section with ordered changes (likely:
1. author VAExtension/custom step wrappers for the 4 window-nav methods + Form.Activate;
2. add a static-tree fixture form; 3. add a body-button fixture; 4. re-run the breadth
loop for the 7 members).

## Log
- 2026-06-13T05:44:12Z card created
