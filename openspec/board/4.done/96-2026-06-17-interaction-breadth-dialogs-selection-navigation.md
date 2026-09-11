# 96. Capture-free interaction breadth — dialogs, selection, navigation, keyboard, messages

## Status
4.done

## Order Index
96

## Owner
unassigned

## OpenSpec Stage
story

## Result
Done. All 5 changes delivered capture-free, no Vanessa, live-verified: dialogs (`answer_dialog`), value/menu/
reference selection (`choose_from_list` / `choose_from_menu` / `set_reference_field`), object navigation
(`open_card` / `close_window` / `activate_window`), user messages (`read_user_messages`), and keyboard
(change 4). Change 4's finding: 1C keyboard input is OS-LEVEL (VanessaExt; no manager→client key frame to
decode — the card-98 write-commit root-cause), so it is delivered as `send_keys` over XTEST (the same
xdotool-key primitive DB-verified in `write_form_value_xtest`, which now routes its Tab/Ctrl+S through it);
live-verified ZZKBD51 committed+saved on the demo. Decision record: `docs/keyboard-input-decision.md`.

## Next
None. Optional refinements (not blockers): dialog Нет/Отмена variants + a confirmed QUESTION(Да) capture
(same window-level mechanism as `answer_dialog`).

## Source
- 2026-06-17 (board triage): consolidates the next-epic interaction work (roadmap §E1–E3 + the E5
  prerequisites) into one story with a 5-item change set. Folds cards 91, 92, 93 and the keyboard /
  user-message prerequisites of card 95 (all now in `5.canceled`, full plans preserved there).
- Epic: card 82. Full per-item detail: `docs/protocol-research/capture-free-epic-next-roadmap.md` §E1–E3, §E5.

## Summary
The high-frequency action verbs a Test Manager needs, all capture-free (no Vanessa): answer dialogs, pick a
value/reference, navigate between objects/windows, send raw keys, and read user messages. Built on the proven
decode→productize loop (state doc §6) and the shipped 18-tool surface.

## Changes (5)
1. **Dialogs — `answer_dialog(Да/Нет/ОК/Отмена)` / `click_dialog_button(title)`** (was card 91 / §E1).
   Add real `ПоказатьВопрос`/`ПоказатьПредупреждение` commands to the fixture (current `PF_V4_*` only
   simulate dialog state); capture open+answer; decode the dialog SecondaryFrame GUID bind + the answer
   command (expected `Button[Да]` activate `88 81 81 e1`); MCP tool + live read-back via PF_V4_DIALOG_RESULT.
2. **Reference / value selection — `choose_from_list(value)` + `set_reference_field(field, value)`**
   (was card 92 / §E2). The single most frequent 1C action. Verify the Контрагент field type; compose
   `open_list` + `select_table_row` + a confirm; decode the "confirm selection" (double-click / Выбрать /
   Enter); live read-back of the chosen presentation. Pairs with change 5 (PF_SHOW_CHOICE_LIST → `Сообщить`).
3. **Object navigation — `open_card` / `close_window` / `activate_window(title)`** (was card 93 / §E3).
   Drill into a list row (open the record card), close forms, switch windows. `render_open_card_command` is
   already decoded (cards 74/78) but not live-verified capture-free; verify against the embedded
   `ДенамическийСписокИерархия` (Catalog.Товары); decode close + activate; verify via the active-window caption.
4. **Keyboard input — Enter / Esc / Tab / arrows / shortcuts** (was card 95 / §E5; prereq for changes 1 & 2).
   Decode the key-press command (raw key events vs the protocol activate/SET); needed to confirm/cancel
   dialogs and some navigation.
5. **Read user messages — the `Сообщить`/`ПоказатьПредупреждение` message area** (was card 95 / §E5; prereq
   for change 2). Vanessa asserts «нет сообщений пользователю»; decode the message area in the read sweep (or
   add a fixture marker). Required by change 2 (PF_ChoiceListDone surfaces its result via `Сообщить`).

## Progress
- **Change 2 — value-list + menu pick DONE (2026-06-18), live-verified capture-free.** `choose_from_list(value)`
  (ПоказатьВыборИзСписка) and its wire-twin `choose_from_menu(value)` (ПоказатьВыборИзМеню) pick an item from a
  popup with NO Vanessa — MCP tools #19/#20, 3 unit tests (suite 226). Decode: the popup reuses the form window
  (no new SecondaryFrame); the pick is the `e0 4b 53` choose tag + a length-prefixed value at the ManagedForm
  path (the `set_choice` family, addressed at the form); the result is a user message `Сообщить(<prefix> +
  value)` confirmed on the wire (`PF_CHOICE=` for the list, `PF_MENU=` for the menu — the standalone takes a
  `message_prefix`). Live: PF_CHOICE_A/C and PF_MENU_2 (re-targeted from the captured values) all committed on
  fresh native clients. Evidence:
  `docs/protocol-research/evidence/genuine-card96-choicelist-2026-06-18/findings.md`.
  - This also lands the **first user-message read** (change 5): `PF_CHOICE=…` is the `Сообщить` text scraped off
    the wire post-pick.
  - **Change 2 — reference selection `set_reference_field` DONE (2026-06-18), live-verified capture-free.** The
    fixture form ALREADY has a `Контрагент` ref field (CatalogRef.Контрагенты) — NO Form.form edit/deploy needed.
    Set a CatalogRef field to a catalog element by NAME with NO Vanessa — MCP tool #22, suite 229. Decode: a ref
    InputField resolves a TYPED name to a ref (выбор по строке); the name rides the wire as the value-SET family
    `e0 41 81 81 b7 <char-count><utf-16le name><pad>` (tag `b7` + a UTF-16 char-count value), committed by the
    ordinary focus-change. Productized as a faithful full-stream replay + a UTF-16 name retarget
    (`retarget_ref_value`). Live: Контрагент="Пантера АО" (re-targeted from the captured "Корнет ЗАО") commits +
    reads back. ⚠ CONSTRAINT: `value` must be the SAME char-length as the captured name (length-fixed edit
    buffer — same as the card-80 fixed-width string write; variable-length is a documented refinement).
    ⚠ CORRECTION: an earlier note wrongly said "Контрагенты has only groups" — it has many leaf elements nested
    in the groups (the selection form opens hierarchical; I had confirmed a GROUP). Evidence:
    `docs/protocol-research/evidence/genuine-card96-ref-2026-06-18/findings.md`.
- **Change 1 — dialogs: fixture + deploy + `answer_dialog` DONE (2026-06-18), live-verified capture-free.** The
  fixture raises REAL `ПоказатьВопрос`/`ПоказатьПредупреждение` (Module.bsl edit + answer markers; DEPLOYED via
  the new reusable `tools/protocol-research/deploy_fixture.sh`, manual ibcmd, gen `98fc8582…`→`c8983d19…`), and
  **`answer_dialog`** answers them with NO Vanessa — MCP tool #21, suite 227. Decode: a dialog opens a **NEW
  SecondaryFrame** window; the answer is a **window-level command** on the dialog SF (`…SecondaryFrame[dlg]
  88 82 81` = the window default-action = ОК/Да), NOT a `Button` activate. Productized as a FAITHFUL full-stream
  replay — `GuidRebinder` learns the live dialog GUID from the open response (first-appearance, like the form
  window) and rebinds the close command. Live: replay → `PF_V4_WARNING_ACK` reads back on a fresh client.
  ⚠ the xdotool auto-allow CONTAMINATES dialog captures (XTEST-clicks the in-app dialog) — it is NOT needed
  (`DisableUnsafeActionProtection=.*`), keep it off for a clean answer capture. Remaining: Нет/Cancel variants +
  a confirmed QUESTION(Да) capture (same window-level mechanism). Evidence:
  `docs/protocol-research/evidence/genuine-card96-dialogs-2026-06-18/findings.md`.
- **Change 3 — object navigation: `open_card` DONE (2026-06-18), live-verified capture-free.** Drill into a
  catalog list row to open the record CARD with NO Vanessa — MCP tool #23, suite 230. Decode: drilling into a
  list row opens a NEW window (the record form) — the same new-window shape as a dialog (open form → open the
  Контрагенты list → «Изменить» → the card opens; 3 SecondaryFrame windows). Productized as a faithful
  full-stream replay (`derive_open_card`/`open_card`); `GuidRebinder` rebinds the form/list/card window GUIDs as
  they appear — the answer_dialog new-window machinery transferred directly. Live: replay → the card marker
  "ФормаГруппы" reads back. `close_window` + `activate_window` are DECODED (window-level `88 82 81` commands —
  the SAME family as the dialog-close — + `e0 4b` activate; Vanessa steps «закрываю текущее окно» / «активизирую
  окно "X"» proven on the genuine manager) but their capture-free PRODUCTIZATION is blocked on an INCOMPLETE
  capture — investigated 2026-06-18: the "multi-connection" framing was partly WRONG (the extra TCP connections
  are the AGENT's own forward-proxy traffic to `127.0.0.1:1081`, NOT 1C; the real 1C link is one connection).
  Real cause = client-side form-descriptor CACHING — open_card was the first/clean open (descriptors sent +
  captured); later windows captures reuse the cached compiled forms (`~/.1cv8/.../<ib-guid>/`), so the
  descriptor frames aren't re-sent → an incomplete stream (~31 vs ~79 chunks). NEXT: capture from a COLD client
  (clear the form cache) as one clean single-shot flow, then the existing full-replay pattern. Evidence:
  `docs/protocol-research/evidence/genuine-card96-opencard-2026-06-18/findings.md`.

- **Change 5 — read user messages: DONE (2026-06-18).** `read_user_messages` (MCP #26) + the reusable
  `extract_user_messages` decoder (the `cb 53 9a <byte-len> <UTF-8>` `Сообщить`/assertion envelope), live-verified;
  first landed via the `choose_from_list` `PF_CHOICE=…` wire marker (change 2). Vanessa's «нет сообщений
  пользователю» assertion is now readable capture-free.
- **Change 4 — keyboard: DONE (2026-06-20), live-verified.** FINDING: 1C keyboard input is OS-LEVEL — Vanessa
  injects keys with the VanessaExt external component INSIDE the client; the key is in NO manager→client protocol
  frame (the card-98 write-commit root-cause), so there is no key-press command to decode/replay (a capture would
  be empty). Delivered as `send_keys(keys, display)` (MCP #49) over XTEST (xdotool) — the SAME `xtest_key`
  primitive DB-verified in `write_form_value_xtest`, which now routes its Tab/Ctrl+S through `send_keys`.
  Live (demo, `run_xtest_write_test.sh`): "ZZKBD51" committed+saved (`committed:true, saved:true`) — i.e.
  `send_keys(["Tab"])` commits the object attribute and `send_keys(["ctrl+s"])` persists to DB. High-level
  keyboard intents already have protocol tools (confirm/cancel → `answer_dialog`; row nav → `select_table_row`/
  `read_list_grid`; save → `click_command` «Записать»); `send_keys` is the raw-key escape hatch. Decision
  record: `docs/keyboard-input-decision.md`. 342 tests (+2). Evidence: the decision record + the live run above.

## Notes / constraints
- Dialogs/cards open a NEW top-level window → fresh SecondaryFrame GUID; `GuidRebinder` must pick it up from
  the open response. Modal windows may block the read loop — handle timing.
- Keyboard + user-message reading are the highest-leverage (they unblock changes 1 & 2) — do them first.
- Fixture work is 1C via edt-mcp (manual `ibcmd` deploy); keep `PF_*` naming so 86a addressing stays valid.

## Plan for the new session (start here)
Read `docs/protocol-research/capture-free-epic-next-roadmap.md` §E1–E3 + §E5, and `capture-free-epic-state.md`
(§5 capture recipe, §6 decode→productize loop). Suggested order: change 4 (keyboard) + change 5 (messages)
first (prerequisites), then change 1 (dialogs), change 2 (selection), change 3 (navigation).

## Merged from (full plans preserved as audit trail in 5.canceled)
- card 91 (dialogs) → change 1
- card 92 (reference/list selection) → change 2
- card 93 (object navigation) → change 3
- card 95 (keyboard + user-messages portion) → changes 4, 5 (its table/report/list-ops portion → card 97)

## Related
- Epic 82. State doc `capture-free-epic-state.md`; roadmap `capture-free-epic-next-roadmap.md`.
- Shipped primitives reused: `open_list`, `select_table_row`, `click_command`, `read_form_value`.
- Memories: genuine-action-capture-recipe, vanessa-mcp-linux-genuine-manager.

## Log
- 2026-06-17 card created by board triage — consolidates 91/92/93 + the 95 prerequisites (5-item change set).
- 2026-06-18 change 2 — value-list pick (`choose_from_list`) decoded + productized (MCP tool #19, suite 225) +
  live-verified capture-free (PF_CHOICE_A/C committed via the `Сообщить` wire marker, no Vanessa). Also lands the
  first user-message read (change 5). Remaining: the reference-field pick (`set_reference_field`). Evidence:
  `genuine-card96-choicelist-2026-06-18`.
- 2026-06-18 change 2 — menu pick (`choose_from_menu`, ПоказатьВыборИзМеню) — the wire twin of the list; same
  `e0 4b 53` decode, MCP tool #20 reusing the machinery (`message_prefix=PF_MENU=`), suite 226, live-verified
  (PF_MENU_2 re-targeted from PF_MENU_1 committed). Value-list/menu selection is now fully capture-free; the
  reference-field pick is the only remaining E2 sub-flow (needs a fixture reference field → deploy).
- 2026-06-18 change 1 — dialogs: made the fixture raise REAL ПоказатьВопрос/ПоказатьПредупреждение (Module.bsl)
  + DEPLOYED via the new `deploy_fixture.sh` (manual ibcmd; gen `98fc8582…`→`c8983d19…`); live-verified the
  warning answer (PF_V4_DIALOG_RESULT=PF_V4_WARNING_ACK). Answer decode PARTIAL: a dialog is a NEW SecondaryFrame
  + the answer is a window-level command (`88 82 81` on the dialog SF), not a button-activate; the xdotool
  auto-allow contaminates the capture (must be off during the answer). Productization (answer_dialog with
  new-window rebind) is the clear next step. Evidence: `genuine-card96-dialogs-2026-06-18`.
- 2026-06-18 change 1 — `answer_dialog` PRODUCTIZED + live-verified capture-free (MCP tool #21, suite 227). A
  truly clean capture (auto-allow off; not needed — `DisableUnsafeActionProtection=.*`) confirmed the genuine
  answer = the window-level `88 82 81` on the dialog SF (byte-identical to the contaminated capture, so genuine,
  not an XTEST artifact). `derive_answer_dialog`/`answer_dialog` faithfully replay the dialog session; GuidRebinder
  rebinds the per-open dialog GUID automatically (first-appearance, like the form window). Live: replay →
  PF_V4_WARNING_ACK reads back on a fresh client, no Vanessa. Remaining: Нет/Cancel + a confirmed QUESTION(Да).
- 2026-06-18 change 2 — `set_reference_field` INVESTIGATED, BLOCKED on catalog data. Discovered the fixture
  ALREADY has the `Контрагент` ref field (CatalogRef.Контрагенты) → NO Form.form edit/deploy needed. Vanessa
  drive proven (choice opens `Контрагенты.Форма.ФормаВыбора`, «Выбрать» confirms). Blocker: Контрагенты has
  only GROUPS, no leaf elements; creating one cascades into mandatory ref fields (Вид цен). Checkpointed —
  needs a seeded valid element, then the clean capture→decode→productize of the new-window selection-confirm.
  See the change-2 "Remaining" note above. (Generation unchanged `c8983d19…` — no data committed.)
- 2026-06-18 change 2 — `set_reference_field` DONE + live-verified (CORRECTS the previous line: the operator's
  screenshots showed the Контрагенты catalog DOES have leaf elements, nested in the groups — my earlier "groups
  only" was wrong, I had confirmed a GROUP). The ref set works via type-resolve (выбор по строке): the typed
  name rides the value-SET family `e0 41 81 81 b7 <char-count><utf-16le name><pad>`, committed by focus-change.
  `retarget_ref_value` (UTF-16 fixed-width) + `derive_set_reference_field` + `set_reference_field` (full replay +
  retarget) + MCP tool #22, suite 229. Live: Контрагент="Пантера АО" (re-targeted from "Корнет ЗАО") commits.
  Constraint: same char-length as the captured name (variable-length is a documented refinement). Evidence
  `genuine-card96-ref-2026-06-18`. **Change 2 (list + menu + reference) is now fully capture-free.**
- 2026-06-18 change 3 — `open_card` DONE + live-verified. Drilling into a catalog list row opens the record CARD
  in a NEW window (3 windows: form + list + card); productized as a faithful full-stream replay reusing the
  answer_dialog GuidRebinder new-window machinery (`derive_open_card`/`open_card`, MCP tool #23, suite 230).
  Live: replay → card marker "ФормаГруппы" reads back, no Vanessa. Remaining in change 3: close_window +
  activate_window. Evidence `genuine-card96-opencard-2026-06-18`.
- 2026-06-18 change 3 — close_window + activate_window DECODED + Vanessa-verified (window-level `88 82 81`
  commands, same family as the productized dialog-close; «закрываю текущее окно» / «активизирую окно "X"» proven).
  Productization BLOCKED on a capture-tooling limit: the multi-window flow spans several manager↔client
  connections, `pcap_to_traffic` assembles only one → incomplete stream (open_card was single-connection by
  luck). NEXT: multi-connection capture assembly, then the same full-replay pattern. open_card (the high-value
  navigation core) remains productized; this is the honest change-3 boundary.
- 2026-06-18 change 3 — investigated the close/activate capture blocker (the "multi-connection assembly"). Finding
  CORRECTS the earlier note: the extra connections are the AGENT's own proxy traffic to 127.0.0.1:1081 (CONNECT
  chatgpt.com/api.openai.com), NOT 1C — the real 1C link is one connection, so merging isn't the fix. Real cause
  = client-side form-descriptor CACHING: open_card was the first/clean open (descriptors on the wire); later
  windows captures reuse the cached compiled forms → incomplete stream (no PF_* fields / ФормаГруппы, ~31 vs ~79
  chunks). Fix identified (cold-client capture: clear `~/.1cv8/.../<ib-guid>/`), not executed (risk/time). close/
  activate stay decoded + Vanessa-verified; productization awaits the cold capture. See the evidence note.
- 2026-06-18 (Task 1) close_window + activate_window PRODUCTIZED + live-verified (MCP #24/#25). The cold-cache
  "blocker" was a false alarm — the windows captures replay as-is (the replay client shares the on-disk form
  cache). close + activate are the SAME window-level `…SecondaryFrame[w] 88 82 81` command (contextual on
  z-order: topmost → close, background → activate). Change 3 (object navigation) COMPLETE.
- 2026-06-20 change 4 (keyboard) DONE + change 5 (user messages) confirmed DONE — card CLOSED → `4.done`.
  Change 4: 1C keyboard is OS-level (VanessaExt; no manager→client key frame), delivered as `send_keys` (MCP
  #49) over XTEST — `write_form_value_xtest` now routes Tab/Ctrl+S through it; live-verified ZZKBD51
  committed+saved on the demo. Decision record `docs/keyboard-input-decision.md`. README + parity doc updated
  (49 tools). 342 tests (+2). All 5 changes delivered.
- 2026-06-20 `$opsx-pub` — docs updated (README count + keyboard action; parity doc keyboard row + count;
  decision record). Verified: `git diff --check` clean, `openspec validate --all` ✓, 342 tests pass. Scoped
  commit + push to `origin/main`.
