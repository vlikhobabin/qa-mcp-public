# 91. Dialogs: open + ANSWER Да/Нет/ОК/Отмена (capture-free)

## Status
5.canceled

## Merged
- 2026-06-17 (board triage): folded into **card 96** (Capture-free interaction breadth) as **change 1**
  (dialogs). The full plan below is preserved as working detail; card 96 is the active surface.

## Order Index
91

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-17 (next-epic roadmap E1): card 90 shipped 18 capture-free MCP tools, but **answering 1C dialogs is
  not productized**. Confirmations (delete/post/overwrite), warnings and questions block almost every real
  business flow. Today only an xdotool **auto-allow hack** (`vanessa_auto_allow_dialogs.sh`) exists for the
  platform *security* modals — not a targeted, protocol-level "answer dialog" action.
- ⚠ Fixture polygon is INCOMPLETE: `PF_V4_QUESTION_YES`/`PF_V4_WARNING` only **simulate** dialog state via
  markers (`PFV4_RegisterDialogScenario`); they do NOT call a real `ПоказатьВопрос`/`ПоказатьПредупреждение`.

## Summary
Productize answering 1C dialogs capture-free — `answer_dialog(button="Yes"|"No"|"OK"|"Cancel")` /
`click_dialog_button(title)` — so scenarios with confirmations/questions/warnings run with NO Vanessa. First add
real-dialog commands to the fixture; then capture→decode→productize the dialog-answer command.

## Acceptance
- Fixture: a `PF_ASK_YESNO` command (`ПоказатьВопрос(Оповещение, …, РежимДиалогаВопрос.ДаНет)`) + `PF_WARN_OK`
  (`ПоказатьПредупреждение`) whose callbacks record the answer into a readable marker (PF_V4_DIALOG_RESULT /
  PF_LAST_ACTION). Deployed via the manual `ibcmd` procedure. (Verify whether `PF_V4_MODAL_OPEN/CLOSE` already
  opens a real modal *form* — if so, also a polygon.)
- A genuine capture of opening a real Да/Нет dialog and clicking «Да» (and «ОК» on a warning).
- Decode documented: how the dialog's new SecondaryFrame GUID is bound, and the answer command (expected: the
  `click_command` pattern — `Button[Да]`/`Button[Нет]`/`Button[ОК]` activate `88 81 81 e1` — on the dialog frame).
- MCP tool(s) `answer_dialog` / `click_dialog_button`, unit tests, an evidence note.
- Live-verified on a fresh native client (no Vanessa): the recorded answer reads back via PF_V4_DIALOG_RESULT /
  PF_LAST_ACTION.

## Notes / constraints
- Dialog opens a new top-level window (fresh SecondaryFrame GUID → GuidRebinder must pick it up from the
  dialog-open response). Async `ОписаниеОповещения` callbacks → may need a read/poll between open and answer.
- Keyboard-only dialogs (Enter = default button, Esc = cancel) may need card 95 (keyboard input).
- Modal windows may block the protocol read loop — handle timing.

## Plan for the new session (start here)
Read `docs/protocol-research/capture-free-epic-next-roadmap.md` **§E1** (full detail) + `capture-free-epic-state.md`.
1. Add `PF_ASK_YESNO` / `PF_WARN_OK` to the fixture (Module.bsl handlers + form command buttons), deploy (manual
   ibcmd; apache STOP + Vanessa DOWN + SIGTERM EDT daemon → export/import/apply).
2. Boot the genuine manager; find the Vanessa dialog-answer step (e.g. «я нажимаю на кнопку 'Да'» on the dialog,
   or a dedicated dialog step); capture open+answer under tcpdump.
3. Decode the answer command; productize mirroring `click_command`; live-verify via the marker read-back.
