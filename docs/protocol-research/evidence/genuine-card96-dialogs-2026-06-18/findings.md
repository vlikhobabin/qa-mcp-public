# Card 96 / E1 — real dialogs (ПоказатьВопрос/ПоказатьПредупреждение): fixture + deploy + answer_dialog DONE

**Date:** 2026-06-18. **Card:** 96 (interaction breadth), change 1 (dialogs Да/Нет/ОК). **Status:** DONE for the
default-action (ОК/Да) answer — the fixture raises REAL dialogs (deployed + verified) AND `answer_dialog` is
productized + live-verified capture-free (MCP tool #21, 227 tests). A dialog is a deeper case than the
choice-list (it opens a NEW window + the answer is a window-level command), but it solves cleanly via a faithful
full-stream replay with GuidRebinder learning the live dialog GUID. The Нет/Cancel variants + a confirmed
QUESTION(Да) capture are the remaining follow-ups.

## ✅ RESOLVED (2026-06-18) — answer_dialog productized + live-verified

A truly CLEAN capture (auto-allow off during the answer — `DisableUnsafeActionProtection=.*` means the
embedded-processor client needs no auto-allow at all) confirmed the genuine answer: click `PF_V4_WARNING` →
dialog opens as a NEW `SecondaryFrame[14b38366…]` "Предупреждение" (client→manager `g52`) → manager→client
**`…SecondaryFrame[14b38366] 88 82 81`** (`g53`, the window default-action = ОК) + `…81 81 81` (`g55`, read).
This is byte-identical to the earlier (contaminated) `g48`/`g50` — so the window-level command IS the genuine
answer, not an auto-allow artifact.

Productized in `src/qa_mcp/protocol/native_write.py`: `_find_dialog_close` (the dialog SF = the SecondaryFrame
that is NOT the form's most-referenced one, targeted by an `88 82 81` manager frame), `AnswerDialogTemplate`,
`derive_answer_dialog(capture_dir, raise_command, result_marker)`, `answer_dialog(template, …)` — a FAITHFUL
full-stream replay (open form → raise → window-level answer → read-back). The dialog's fresh per-open SF is
rebound by `GuidRebinder` automatically (it learns the live dialog GUID from the live open response by
first-appearance, exactly like the form window). MCP tool `answer_dialog(raise_command, result_marker)` (the
**21st** tool). Unit test `test_derive_answer_dialog_locates_dialog_window_and_close`.

**Live proof** (`tools/protocol-research/{answer_dialog_probe.py,run_answer_dialog_test.sh}`, fresh native
client): `committed=true` — `PF_V4_WARNING_ACK` reads back after the replayed answer, no Vanessa. Capture
`genuine-card96-dialog-warn-20260618`.

----
(below: the original investigation that led here, including the auto-allow contamination diagnosis.)

## DONE — fixture real-dialog edit + deploy (live-verified)

The fixture's `PF_V4_QUESTION_YES` / `PF_V4_WARNING` commands previously only SIMULATED a dialog via markers
(`PFV4_RegisterDialogScenario`). Edited the embedded-config DataProcessor `Module.bsl` (HAND edit, CRLF/tab
preserved; backup `Module.bsl.bak-card96-dialogs`) to raise REAL dialogs + record the answer:
- `PF_V4_QUESTION_YES` → `ПоказатьВопрос(Новый ОписаниеОповещения("PF_QuestionDone", …), …, РежимДиалогаВопрос.ДаНет)`;
  callback `PF_QuestionDone(Результат, …)` sets `PF_V4_DIALOG_RESULT` = `PF_V4_QUESTION_YES/_NO/_CANCEL`.
- `PF_V4_WARNING` → `ПоказатьПредупреждение(Новый ОписаниеОповещения("PF_WarnDone", …), …)`; callback `PF_WarnDone`
  sets `PF_V4_DIALOG_RESULT` = `PF_V4_WARNING_ACK`, `PF_V4_DIALOG_LIFECYCLE` = `PF_V4_WARNING_CLOSED`.
- Module-only change (the command buttons already exist) → Form.form untouched (low risk).

**Deploy (manual ibcmd, state-doc §7) — DONE + reusable script.** New `tools/protocol-research/deploy_fixture.sh`
encodes the procedure: stop apache + free the EDT workspace → `generation-id` (before) → backup `.1CD` →
`1cedtcli export --configuration-files` → `ibcmd config … import` → `ibcmd config … apply --dynamic=disable
--session-terminate=force --force` → `generation-id` (after). It aborts before import/apply if the export
produced too few files, and backs up the `.1CD`. Result: 852 files exported, import+apply OK, generation
`98fc8582…` → **`c8983d19…`** (the BSL compiled — apply would fail on a syntax error). Backup
`1Cv8.1CD.bak-card96-dialogs-predeploy`.

**Verified live (genuine manager):** open the form → click `PF_V4_WARNING` → real ПоказатьПредупреждение opens
→ Vanessa step **«И я закрываю окно предупреждения»** (`ЯЗакрываюОкноПредупреждения`, category UI.Всплывающие
окна) closes it (= ОК) → read-back `PF_V4_DIALOG_RESULT` = **"PF_V4_WARNING_ACK"**, `PF_V4_DIALOG_LIFECYCLE` =
"PF_V4_WARNING_CLOSED". The QUESTION (Да/Нет) raised + was answered Да (marker `PF_V4_QUESTION_YES`).

## PARTIAL — the capture-free ANSWER decode (the deeper problem)

Capture: `genuine-card96-dialog-clean-20260618/` (client 48002, manager 51088). Trace of a WARNING flow:
- click `Button[PF_V4_WARNING]` (man) → **the dialog OPENS as a NEW window**: client→manager `g47` (len 702)
  lists the hierarchy incl. a FRESH `SecondaryFrame[22f75d41-…]` titled "Предупреждение" alongside the form
  window `SecondaryFrame[6a3b0f24-…]`. So unlike the choice-list popup (which reuses the form window), a
  ПоказатьВопрос/ПоказатьПредупреждение dialog is a **new top-level SecondaryFrame** (as the roadmap predicted).
  The dialog SF FIRST appears in the open response → `GuidRebinder` can learn it for rebinding.
- manager→client frames on the dialog SF: `g48` = `…SecondaryFrame[22f75d41] 88 82 81 <pad>`, `g50` =
  `…SecondaryFrame[22f75d41] 81 81 81 <pad>`. There is **NO `Button[ОК]`/`Button[Да]` path and NO `88 81 81 e1`
  command-execute / `e0 4b` activate** on the dialog window — i.e. the answer is **NOT a button-activate** like a
  form command; it is a WINDOW-LEVEL command addressed at the dialog `SecondaryFrame`. After `g50` the dialog SF
  disappears (closed). **Leading hypothesis:** `g48` (`88 82 81` on the dialog SF) is the default-action/close
  (the warning's only action = ОК); `g50` (`81 81 81`) is a read. Unconfirmed.

### ⚠ Auto-allow contamination (important for the next session)

`vanessa_auto_allow_dialogs.sh` (XTEST clicks `[Да]`@(right-133) / `[OK]`@(right-55)) is needed to clear the
client's launch security modal, but it ALSO clicks 1C in-app dialogs (ПоказатьВопрос/Предупреждение) — so the
answer becomes a client-side XTEST click and the wire shows only a client→manager notification, NO replayable
manager→client command. A FIRST capture (`genuine-card96-dialog-20260618`) was contaminated this way (the «Да»
step ERRORED — the auto-allow had already answered). The QUESTION (Да/Нет) needs a genuine manager-driven answer
step that works with the auto-allow OFF — and the generic «я нажимаю на кнопку 'Да'» did not bind the dialog
button. ⇒ For a clean answer capture: keep auto-allow ON only during connect, then KILL it (all children +
xdotool — kill by PID, not `pkill -f`, which self-matches the agent shell) before clicking the dialog command.

## NEXT (productize answer_dialog) — the clear path

1. Take a TRULY clean capture (auto-allow fully off during the answer) of BOTH a WARNING (ОК) and a QUESTION
   (Да) — confirm whether `g48`-style `88 82 81` on the dialog SF is the genuine close, and find the Да/Нет
   answer (a Да/Нет question may expose explicit `Button[Да]`/`Button[Нет]` on the dialog SF — cleaner than the
   warning's window-default).
2. `derive_answer_dialog`: setup (form open) → click the dialog-raising command → the answer block (the
   window-level command on the dialog SF). On replay, `GuidRebinder` learns the live dialog SF from the open
   response and rebinds the answer's `SecondaryFrame[…]` (same mechanism as the form SF, but a per-open fresh
   GUID). MCP tool `answer_dialog(button="Yes"|"No"|"OK")`; verify via `PF_V4_DIALOG_RESULT` read-back.
3. Resolve the Да/Нет answer step (search the genuine step library beyond «Всплывающие окна», or drive via
   keyboard — card 96 change 4 / E5 — Enter=default, which would also answer ОК).

## Artifacts
- `tools/protocol-research/deploy_fixture.sh` (reusable manual-ibcmd deploy), `qa-card96-capture-dialog.feature`.
- Fixture source (NOT git-tracked): `…/ФикстураПротоколаTestClient/Forms/Форма/Module.bsl` (+ `.bak-card96-dialogs`).
- Captures (gitignored): `genuine-card96-dialog-clean-20260618` (clean-ish WARNING), `genuine-card96-dialog-diag`
  (no-auto-allow diagnostic showing the new dialog SF), `genuine-card96-dialog-20260618` (auto-allow-contaminated).
- IB backup: `/opt/1c-dev/vanessa_client/1Cv8.1CD.bak-card96-dialogs-predeploy`.
