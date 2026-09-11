# Card 96 / E2 — choose-from-list (ПоказатьВыборИзСписка) capture-free: decode + productize + live proof

**Date:** 2026-06-18. **Card:** 96 (capture-free interaction breadth), change 2 (reference / value selection).
**Result:** `choose_from_list(value)` is decoded, productized (MCP tool #19) and LIVE-VERIFIED capture-free, no
Vanessa. First step of card-96 change 2 (the value-list / menu pick) — the reference-field pick is the
remaining sub-flow.

## Polygon (no fixture change)

The fixture `ФикстураПротоколаTestClient` already exposes a REAL `ПоказатьВыборИзСписка` modal (Module.bsl
`PF_SHOW_CHOICE_LIST` command → list `PF_CHOICE_A/B/C` → callback `PF_ChoiceListDone` →
`Сообщить("PF_CHOICE=" + Выбранный.Значение)`). So E2's value-list pick needed NO fixture edit (unlike E1
dialogs, whose `PF_V4_*` only simulate). The menu twin `PF_SHOW_CHOICE_MENU` (`ПоказатьВыборИзМеню`) is also real.

## Vanessa steps (resolved by `search_for_steps_by_keywords`)

- Click the command that raises the list — **by NAME** (the button caption is an auto-synonym "P f SHOW CHOICE
  LIST", so the by-caption step fails): `И я нажимаю на кнопку с именем 'PF_SHOW_CHOICE_LIST'`.
- Pick from the `ПоказатьВыборИзСписка` popup: **`И я выбираю из списка "PF_CHOICE_B"`** (`ЯВыбираюИзСписка`;
  its description: "список должен быть вызван методом ПоказатьВыборИзСписка()").
- Menu twin (`ПоказатьВыборИзМеню`): `И в меню формы я выбираю 'ИмяПунктаМеню'` (`ВМенюФормыЯВыбираю`).

## Capture

`runtime/protocol-research/captures/genuine-card96-choicelist-20260618/` (gitignored). Genuine Vanessa manager
on Xvfb :77 → `tcpdump -i lo` on the client TPort → drive the form (connect+open self-contained, then the click
+ pick via `execute_step_from_text` on the open form for a clean single connection). Read-back confirmed on the
genuine side: `get_form_analysis(format=messages)` → `PF_CHOICE=PF_CHOICE_B`. Ports: client 48001, dominant
manager 54666 → `pcap_to_traffic.py cap.pcap 48001 traffic 54666` (768 chunks). Feature:
`tools/protocol-research/qa-card96-capture-choicelist.feature`.

## Decode (KEY)

- **The popup REUSES the form window.** The pick is addressed at `SecondaryFrame[S].ManagedForm[F]` — the SAME
  GUIDs as the open fixture form (learned in the handshake). `ПоказатьВыборИзСписка` does NOT create a new
  SecondaryFrame, so there is no new-window GUID to bind (simpler than a real modal dialog — that is E1).
- **The pick is the choose tag `e0 4b 53`** + a length-prefixed value at the form path:
  `…ManagedForm[F] … e0 4b 53 <0x9a><0x0b>PF_CHOICE_B<padding>`. This is the SAME `e0 4b 53` "choose" family as
  a radio `set_choice` (card 90), but addressed at the ManagedForm (no `EditField` leaf) — the picked value IS
  the item. So only the VALUE is re-targeted (`retarget_value`), no element-leaf retarget.
- **The result is a user message.** `Сообщить("PF_CHOICE=" + value)` surfaces as a client→manager frame carrying
  ASCII `PF_CHOICE=PF_CHOICE_B`. It is NOT pushed immediately after the pick — the client emits it only when the
  manager POLLS the form after the pick (the genuine `get_form_analysis` read sweep). So the commit is confirmed
  by replaying the post-pick read frames and scanning for the `PF_CHOICE=<value>` marker. (This doubles as the
  first user-message-read decode — feeds card 96 change 5 / card 97 E5.)
- **Manager-frame block** (manager_to_client only): click `Button[PF_SHOW_CHOICE_LIST]` = mgr[379,380];
  control / modal-open = mgr[381..384]; pick `e0 4b 53`+PF_CHOICE_B = mgr[385,386]; post-pick message-poll reads
  = mgr[387,388]; then trailing 4-byte control frames. `choose_block = (379, 388)`, `setup_end = 378`.

## Productize

`src/qa_mcp/protocol/native_write.py`:
- `_find_choose_from_list(mgr, base_command, captured_value)` — click run (reuses `_find_command_click`) →
  pick (`e0 4b 53` + length-prefixed captured value) → EXTENDED through the post-pick substantive reads (len>16)
  that elicit the message, stopping at the trailing control frames.
- `ChooseFromListTemplate`, `derive_choose_from_list(capture_dir, base_command="PF_SHOW_CHOICE_LIST",
  captured_value="PF_CHOICE_B")`, `choose_from_list(template, value, …)` — replay setup → choose_block with the
  value re-targeted (`retarget_value`, no element leaf) + seq bump; scan responses for the `PF_CHOICE=<value>`
  marker → `committed`.

MCP tool `choose_from_list(value, base_command, captured_value, …)` in `mcp_server.py` — the **19th** tool
(was 18). Default capture `genuine-card96-choicelist-20260618/traffic`.

Tests: `tests/test_native_write.py::test_derive_choose_from_list_locates_click_through_pick` (+ extended block),
`::test_choose_from_list_retargets_picked_value_same_length`. Full suite **225 passed** (was 223; +2).

## Live proof (no Vanessa)

`tools/protocol-research/{choose_from_list_probe.py,run_choicelist_test.sh}` — boot a fresh native TestClient on
:15381 under Xvfb (vanessa_client FREE: Vanessa down + apache stopped), replay setup → click → pick `value`
(re-targeted from the captured PF_CHOICE_B), confirm the `PF_CHOICE=<value>` marker:

- `VALUE=PF_CHOICE_A` → `accepted=True committed=True message='PF_CHOICE=PF_CHOICE_A'` — PASS.
- `VALUE=PF_CHOICE_C` → `accepted=True committed=True message='PF_CHOICE=PF_CHOICE_C'` — PASS.

Both differ from the captured value (PF_CHOICE_B), so the pick is RE-TARGETED, not a replay of the captured
choice. The server callback fired (the `Сообщить` marker reads back the requested value) on a fresh client with
no Vanessa in the loop.

## Menu twin — ПоказатьВыборИзМеню (`choose_from_menu`, 2026-06-18)

The popup MENU (`ПоказатьВыборИзМеню`) is the WIRE TWIN of the choice list. Captured the same way
(`PF_SHOW_CHOICE_MENU` command → menu `PF_MENU_1/2` → callback → `Сообщить("PF_MENU=" + value)`); Vanessa pick
step `И в меню формы я выбираю 'PF_MENU_1'` (`ВМенюФормыЯВыбираю`). Capture
`genuine-card96-menu-20260618/` (client 48001, manager 40250).

Decode: byte-for-byte the same shape as the list — click `Button[PF_SHOW_CHOICE_MENU]` (mgr[22,23]) →
control/modal-open (24,25) → pick `e0 4b 53 <0x9a><len>PF_MENU_1` at the ManagedForm path (26,27) → post-pick
message poll (28,29). `derive_choose_from_list(cap, "PF_SHOW_CHOICE_MENU", "PF_MENU_1")` finds it unchanged.
The ONLY difference is the result message prefix (`PF_MENU=` vs `PF_CHOICE=`), so the standalone
`choose_from_list` gained a `message_prefix` parameter (default `PF_CHOICE=`).

Productize: MCP tool **`choose_from_menu(value, …)`** (the **20th** tool) reuses the SAME machinery with the
menu defaults (`base_command=PF_SHOW_CHOICE_MENU`, `captured_value=PF_MENU_1`, `message_prefix=PF_MENU=`). Unit
test `test_choose_from_menu_reuses_choice_machinery_command_and_value_agnostic` (suite 226).

Live proof: `VALUE=PF_MENU_2 BASE_COMMAND=PF_SHOW_CHOICE_MENU CAPTURED_VALUE=PF_MENU_1 MSG_PREFIX='PF_MENU='
… run_choicelist_test.sh` → `accepted=True committed=True message='PF_MENU=PF_MENU_2'` — the menu pick
(re-targeted from the captured PF_MENU_1) commits on a fresh native client, no Vanessa.

## Remaining for card 96 change 2 (reference selection)

`choose_from_list` covers the value-list / menu pick. The reference-field pick (open a catalog list → select a
row → confirm the ref lands in the field) is the other E2 sub-flow — compose the shipped `open_list` +
`select_table_row` + a "confirm selection" command (to decode). Tracked under card 96 change 2.
