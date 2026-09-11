# Capture-free epic — NEXT roadmap: toward 100% replacement of the standard 1C Test Manager

**Date:** 2026-06-17. **Purpose:** the planned next epic after card 90. Goal: close the remaining gaps so qa-mcp
can drive ARBITRARY 1C forms over the native TestClient protocol **capture-free, with NO Vanessa Automation /
standard Test Manager** in the loop — for real projects, not just the lab fixture. Read
[`capture-free-epic-state.md`](capture-free-epic-state.md) first (it has the decoded protocol model §3, the code
map §4, the capture recipe §5, the decode→productize loop §6, and the 18 shipped tools). This doc is the
"what's left + how we'll do it" handoff for the next session.

## Where we are (card 90 done)

Capture-free + live-verified (18 MCP tools): read (any field by name) · input+commit **string/number/date** ·
checkbox · choice/radio · page-switch · table-cell (+ row-select by value, add_table_row, grid read-back) ·
page-field · open_list · click_command (form command button). Methodology is proven and reusable (below).

## Methodology (reuse for EVERY item below)

1. **Capture** a genuine action via the Vanessa manager + tcpdump on the client TPort (recipe: state doc §5;
   [[genuine-action-capture-recipe]]). Self-contained `.feature` (connect+open+action) → replayable.
2. **Decode** by diff / by anchor. The decode laws (state doc §3): element path
   `…Group[…].<Kind>[NAME]` (latin1); value-SET `e0 41 81 81 ba <varint-len><value>`; activate-with-action
   `e0 4b <op>` (`55`=toggle, `53`=choose); command-execute `88 81 81 e1` on `Button[NAME]`; nav-link
   `e1cib/<kind>/<path>` = `f7<char-count><utf-16le>`; row-select = "find row where COLUMN=VALUE" (length-prefixed
   column+value); cell read-back = the SET-response echo (`read_table_cell_value`). Markers/side-effects in the
   fixture (PF_LAST_ACTION, PF_SELECTED_ROW_MARKER, PF_V4_*) make effects observable.
3. **Productize** mirroring the shipped pattern: `derive_<action>` (locate the genuine command block) +
   standalone fn + (optional) `NativeWriteSession` method + MCP tool; reuse `GuidRebinder` +
   `retarget_element_leaf`/`retarget_value`/`build_write_frame`. Unit tests offline + an evidence note.
4. **Live-verify** on a fresh native client (`launch_test_client` port 15381; vanessa_client FREE → Vanessa +
   apache DOWN) by read-back of a side-effect/marker (preferred) or screenshot.
5. **Fixture edits** (when a polygon is missing) are HAND edits of the EDT source
   (`/opt/1c-dev/vanessa_qa/vanessa_client/src/DataProcessors/ФикстураПротоколаTestClient/`), deployed by the
   MANUAL `ibcmd` export/import/apply (state doc §7 Step 1 — `run_dev_infobase_apply` is structurally
   workspace-locked in-session). The EDT source is NOT git-tracked; record exact edits + generations in the
   evidence note. ⚠ apache2 STOP + Vanessa DOWN + SIGTERM the EDT daemon before the export.

The 5 items below would become board cards (next free ids 91+). Priority order = the list order.

---

## E1 — Dialogs: open + ANSWER Да/Нет/ОК/Отмена  ⭐ highest value

**Why:** confirmations (delete, post, overwrite), warnings and questions block almost every real business flow.
Without answering them, scenarios stall. Today we only have an xdotool **auto-allow hack** for the platform
*security* modals (`vanessa_auto_allow_dialogs.sh`) — not a protocol-level, targeted "answer dialog" action.

**Fixture polygon — PARTIAL, needs a small addition.** ⚠ `PF_V4_QUESTION_YES` / `PF_V4_WARNING` only
*simulate* dialog state via markers (`PFV4_RegisterDialogScenario` sets PF_V4_DIALOG_FAMILY/RESULT/LIFECYCLE) —
they do NOT call a real `ПоказатьВопрос`/`ПоказатьПредупреждение`. So FIRST add real-dialog commands to the
fixture, e.g. `PF_ASK_YESNO` (`ПоказатьВопрос(Оповещение, "…", РежимДиалогаВопрос.ДаНет)`) and `PF_WARN_OK`
(`ПоказатьПредупреждение(Оповещение, "…")`), whose callbacks record the answer into PF_V4_DIALOG_RESULT /
PF_LAST_ACTION (observable). `PF_V4_MODAL_OPEN/CLOSE` may already open a real modal *form* — verify; if so it is
also a polygon. Deploy via manual ibcmd.

**Decode approach.** A 1C dialog (`ПоказатьВопрос`/`ПоказатьПредупреждение`) opens a new top-level window with a
fresh SecondaryFrame GUID (learned via GuidRebinder). Answering = a command-execute on that frame's button
(expect `…Button[Да]`/`Button[Нет]`/`Button[ОК]` or the standard dialog command). So it should reduce to the
**`click_command` pattern on the dialog's frame** — capture clicking «Да» on a genuine `ПоказатьВопрос`, find the
`Button[…]` click block, retarget the button. Open question to settle in the decode: how the new dialog frame's
GUID is bound (is it in the dialog-open response so GuidRebinder picks it up?), and whether async callback timing
needs a read/poll between open and answer.

**Productize.** `answer_dialog(button="Yes"|"No"|"OK"|"Cancel")` / `click_dialog_button(title)` — derive +
standalone + MCP tool. Possibly a combined "click a command that raises a dialog, then answer it" helper.

**Verify.** Read PF_V4_DIALOG_RESULT / PF_LAST_ACTION back (fixture records the answer) — no screenshot needed.

**Risks.** New SecondaryFrame for the dialog; async `ОписаниеОповещения` callbacks; keyboard-only dialogs (Enter
= default button) may need E5 keyboard input. Modal windows may block the protocol read loop — handle timing.

---

## E2 — Reference selection / choice-from-list (pick a value & commit)  ⭐ most common business action

**Why:** "select a Контрагент / Номенклатура / Склад" is the single most frequent action in 1C business forms.
`open_list` only OPENS a list window; we cannot yet PICK a value and have it land in a field.

**Fixture polygon — PARTLY real.**
- `PF_SHOW_CHOICE_LIST` IS a real modal: `ПоказатьВыборИзСписка(Оповещение, СписокЗначений[A,B,C])` → pick →
  `PF_ChoiceListDone` → `Сообщить("PF_CHOICE=" + Выбранный.Значение)`. Real selection dialog + result. ⚠ the
  result surfaces as a **user message** (`Сообщить`) — so this item also needs **reading the message window**
  (see C/E5; or add a marker field PF_CHOICE_LIST_RESULT in the fixture for a clean read-back).
- `PF_SHOW_CHOICE_MENU` = `ПоказатьВыборИзМеню` (popup menu pick) — similar.
- **Reference field** `Контрагент` + `ПолеСоСпискомВыбораСтрока`: VERIFY their types — `Контрагент` may be a
  plain String choice, not a true `СправочникСсылка`. For a real reference-selection polygon, add a form
  attribute of type `СправочникСсылка.Товары` with a choice button (opens the Товары catalog → pick a row → the
  ref + its presentation land in the field). Deploy via manual ibcmd.

**Decode approach.** Two sub-flows:
1. **Value-list / menu pick** (PF_SHOW_CHOICE_LIST/MENU): click the command (opens the dialog) → the dialog is a
   selection list → pick an item. The pick is likely a row-select/activate on the dialog's list + confirm — reuse
   the `e0 4b 5x` activate / the row-select-by-value decode. Retarget the picked value.
2. **Reference field choice**: click the field's choice button → opens the catalog selection list (the
   `e1cib/list/…` open_list we already do) → row-select (we have select-by-value) → confirm/double-click puts the
   ref into the field. So this composes open_list + select_table_row + a confirm. Decode the "confirm selection"
   (the OK/double-click that returns the chosen ref to the field). The committed field reads back as the
   presentation string (read_form_value).

**Productize.** `choose_from_list(value)` (value-list/menu) + `set_reference_field(field, value)` (compose
open-choice → select-by-value → confirm). Reuse open_list + select_table_row + click_command.

**Verify.** read_form_value on the target field (presentation) / a marker.

**Risks.** Reference value is a GUID shown as a presentation; multi-step sub-window flow; the "confirm" step
encoding (double-click vs Выбрать button vs Enter).

---

## E3 — Object navigation: open_card + close form + window management

**Why:** drilling into list items (open a record card), closing forms, and switching between open windows are
basic navigation primitives a test manager needs.

**Decoded-but-not-live (low-hanging).** `navigation.render_open_card_command` and `render_select_row_command`
are decoded (card 74/78 captured-command path) but NOT live-verified capture-free against the fixture. First
step: live-verify `open_card` capture-free.

**Fixture polygon — ready.** The embedded dynamic list `ДенамическийСписокИерархия` (Catalog.Товары) — open it
(we do `open_list`), then double-click a row / «Изменить» → the Товары item CARD opens (open_card). Closing: the
fixture form itself, or the opened list/card. Window management: after open_list/open_card there are multiple
windows.

**Decode approach.**
- `open_card`: from an open list, the "open current row's form" command (likely a command on the list +
  the row ref → opens a DATA form `e1cib/data/Справочник.Товары?ref=…` or a form-open command). Capture
  double-click/«Изменить» on a Товары row → decode. New SecondaryFrame for the card (GuidRebinder).
- `close_window`: capture closing a window (the «×» / «Закрыть» command / Esc) → decode the close command
  (addresses the window/form). Productize `close_window` (close the active window).
- `activate_window` / window switching: the read path already has a window list
  (`get_window_list_testclient`-equivalent); add the protocol command to ACTIVATE a specific window by
  title/handle. Capture switching between two open windows → decode.

**Productize.** `open_card` (from a selected row), `close_window` (active or by title), `activate_window(title)`.

**Verify.** read the active window caption / nav-link after each (we already read `get_active_window_data`-style).

**Risks.** open_card opens a new data form (ref = GUID); window identity/handle on the wire; close on the active
vs a named window.

---

## E4 — 🚩 GENERALIZATION: validate capture-free synthesis on ANOTHER config

**Why — this is the boundary between "lab demo" and "product".** EVERYTHING above is proven on ONE config
(`ФикстураПротоколаTestClient` in `vanessa_client`). To truly replace the test manager we must drive forms in
REAL projects. Element addressing is by-NAME (generic), but three things are unproven:
1. **`bootstrap_synth` (handshake)** — is it config-agnostic, or does it encode fixture/infobase specifics?
2. **per-type genuine templates (captures)** — do they replay against ARBITRARY forms/configs, or is a per-config
   capture needed? (The SET/activate tags are type-identical across configs; session GUIDs are rebound — so in
   principle it generalizes, but the open-form / descriptor differs.)
3. **arbitrary form descriptor** — do we read a foreign form well enough to know field NAMES + TYPES to drive it?
   (Card 87 "form introspection" is the independent piece here.)

**Plan.**
1. Pick a 2nd config available in the lab: `/opt/1c-dev/{demo10413, redacted-third-party-config, demo_1_0_41_3}` (a real-ish
   config). Stand up a native client against it (it must be FREE; mind apache/W^X — [[ibsrv-odata-vs-httpservice]]).
2. **READ first** — `read_active_window` / `read_form_value(field)` against a form there. Does the read path work
   with NO fixture-specific capture? (Tests generality of bootstrap + addressing.)
3. **WRITE** — `write_form_value` into a field of a foreign form. Does the genuine string-SET template replay
   (only GUIDs differ), or does it need a per-config SET capture? Identify exactly what is fixture-specific.
4. **Classify** every shipped action: ✅ generalizes as-is / ⚠ needs a per-config capture / ❌ fixture-only.
   Produce a generality matrix + a "per-config onboarding" recipe (what minimal captures a new config needs).
5. If the bootstrap needs a per-config capture, redefine the claim honestly: "per-config-capture-free after a
   one-time connect capture" vs "universally capture-free".

**Deliverable.** A validation report (evidence) + the generality matrix + an onboarding recipe for a new config.
This card gates the "100% replacement" claim.

**Risks.** The handshake may carry config metadata (infobase id, config version/hash) needing a per-config
connect capture; foreign forms may use element kinds/controls we haven't decoded; licensing/W^X per IB.

---

## E5 — The rest (by demand): keyboard, table ops, messages, reports, async

Each is an independent capture→decode→productize cycle; pull in when a real scenario needs it.
- **Keyboard input** (Enter/Esc/Tab/arrows/shortcuts) — raw key events vs our protocol activate/SET. Needed to
  confirm/cancel dialogs (E1) and some navigation. Decode the key-press command.
- **Read user messages** (`Сообщить`/`ПоказатьПредупреждение` text) — the messages-to-user window. Vanessa asserts
  «нет сообщений пользователю»; we need to read it (E2's PF_ChoiceListDone uses `Сообщить`). Decode the message
  area in the read sweep (or add a marker in the fixture for clean tests).
- **Table ops**: delete row (Delete command on PF_TABLE_ITEMS), move up/down, copy, multi-select; and
  **number/date cells** in the grid (only the STRING cell is proven — number/date use a different per-type value
  buffer like the plain fields).
- **Reports / print / spreadsheet document** (ТабличныйДокумент) — run + read.
- **Dynamic-list ops**: filter, search-string, period, grouping on `ДенамическийСписокИерархия`.

---

## Success criteria for "100% replace the standard test manager"

- All high-frequency actions productized capture-free: input (all types) ✅, checkbox/choice ✅, navigation
  (page-switch ✅, open_list ✅, **open_card**, **close/activate window**), **dialogs answered**, **reference/list
  selection**, table ops (cell ✅/row ✅/**delete/number-date cells**), command click ✅, **keyboard** as needed.
- **Assertions** via read (we have read_form_value/summary) incl. **user messages**.
- **🚩 Proven on ≥1 real (non-fixture) config** (E4) with a documented per-config onboarding cost.
- (Framework parity — BDD orchestration, Allure reporting, data-tables, multi-client — is a SEPARATE,
  higher-layer concern; the protocol-driver gaps above are the prerequisite.)

## Pointers
- Decoded model + code map + capture recipe + decode loop: `capture-free-epic-state.md` §3–§6.
- Shipped code: `src/qa_mcp/protocol/{native_write,navigation,element_ref}.py`, `mcp_server.py`.
- Captures: `runtime/protocol-research/captures/genuine-card90-*`. Probes/features: `tools/protocol-research/*`.
- Memories: [[qa-mcp-capture-free-epic]] (START HERE), [[genuine-action-capture-recipe]],
  [[vanessa-mcp-linux-genuine-manager]], [[linux-native-testclient-xvfb]], [[edt-mcp-profile-and-deploy]],
  [[lab-infobase-access]], [[ibsrv-odata-vs-httpservice]], [[autonomous-1c-observability]].
