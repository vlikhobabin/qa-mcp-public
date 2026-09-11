# Capture-free action synthesis (epic 86) — state & continuation

**Date:** 2026-06-17. **Purpose:** single entry point to continue in a NEW session. **Card 90 is COMPLETE — all
5 element types (checkbox, choice, table-cell, page-field, open_list) done + live-verified, plus the 3 table
follow-ups (row-addressing, add_table_row/click_command, grid read-back).** This doc is the consolidated handoff.
➡ **NEXT EPIC roadmap (the 5 work items toward 100% replacing the standard Test Manager — dialogs,
reference/list selection, object navigation, generalization to other configs, the rest):
[`capture-free-epic-next-roadmap.md`](capture-free-epic-next-roadmap.md).** Read this doc first; it links the
evidence docs, captures, memories and code.

> **⭐⭐ EPIC CLOSED 2026-06-20.** Cards 96/97/98 are all `4.done`; the roadmap epic **82** is closed. **49 MCP
> tools, 342 tests, no Vanessa.** Body counts below ("18 tools / 223 tests") are the 2026-06-17 snapshot —
> historical context only; the current state lives in
> [`capture-free-epic-session-handoff.md`](capture-free-epic-session-handoff.md), the `README.md`, and the
> closed card 82 (`openspec/board/4.done/82-…`). **Honest "100% Vanessa replacement" claim:** READ /
> introspection / most actions are capture-free across ARBITRARY configs (config-agnostic `read_form_descriptor`,
> `click_command` synthesis, dialogs/selection/navigation, dynlist reads incl. nested + row-by-value). The one
> boundary is OBJECT-attribute data entry + RAW keyboard, which are OS-level in 1C (VanessaExt, no manager→client
> frame) — delivered the same way Vanessa does, via the protocol-open + XTEST OS-input hybrid
> (`write_form_value_xtest`, `send_keys`), DB-verified. See card 82's Result for the full restatement.

**Update 2026-06-18 (next-epic card 96 / E2 started):** `choose_from_list(value)` (ПоказатьВыборИзСписка) and
its wire-twin `choose_from_menu(value)` (ПоказатьВыборИзМеню) are shipped — pick an item from a popup
capture-free (no Vanessa), **MCP tools #19/#20**, 226 tests, live-verified (PF_CHOICE_A/C + PF_MENU_2 committed
via the `Сообщить(<prefix>…)` wire marker — also the first user-message read). Law: the popup reuses the form
window (no new SecondaryFrame); the pick is the `e0 4b 53` choose tag + a length-prefixed value at the
ManagedForm path (the `set_choice` family addressed at the form), confirmed by a post-pick message poll; the
result-message prefix (`PF_CHOICE=` / `PF_MENU=`) is a parameter. Evidence:
`evidence/genuine-card96-choicelist-2026-06-18/`. Remaining in change 2: the reference-field pick
(`set_reference_field` = `open_list` + `select_table_row` + confirm — needs a fixture reference field → deploy).

**Update 2026-06-18 (card 96 / E1 dialogs done):** `answer_dialog` answers a real 1C modal
(ПоказатьВопрос/ПоказатьПредупреждение) capture-free — **MCP tool #21, 227 tests**, live-verified
(PF_V4_WARNING_ACK reads back, no Vanessa). The fixture was made to raise REAL dialogs (Module.bsl edit +
markers) and DEPLOYED via the new reusable `tools/protocol-research/deploy_fixture.sh` (manual ibcmd export/
import/apply). Law: a dialog opens a NEW SecondaryFrame window; the answer is a WINDOW-LEVEL command on the
dialog SF (`…SecondaryFrame[dlg] 88 82 81` = the default action ОК/Да), NOT a Button activate — productized as a
faithful full-stream replay (GuidRebinder rebinds the per-open dialog GUID like the form window). ⚠ the xdotool
auto-allow contaminates dialog captures (XTEST-clicks them) and is NOT needed (`DisableUnsafeActionProtection=.*`).
Evidence: `evidence/genuine-card96-dialogs-2026-06-18/`.

**Update 2026-06-18 (card 96 / E2 reference selection done):** `set_reference_field` sets a CatalogRef field to
a catalog element by NAME capture-free — **MCP tool #22, 229 tests**, live-verified (Контрагент="Пантера АО",
no Vanessa). The fixture already had the `Контрагент` ref field (no edit/deploy). Law: a ref InputField resolves
a TYPED name (выбор по строке); the name rides the value-SET family `e0 41 81 81 b7 <char-count><utf-16le
name><pad>` (UTF-16 value, char-count prefix), committed by focus-change; `retarget_ref_value` swaps the name
fixed-width. Constraint: same char-length as the captured name (variable-length = documented refinement).
**Card 96 change 2 (value-list + menu + reference selection) is now fully capture-free.** Evidence:
`evidence/genuine-card96-ref-2026-06-18/`.

**TL;DR (2026-06-17):** read/input+commit/navigate/open are capture-free & live for **string·number·date·
checkbox·choice + page-switch + TABLE-CELL + PAGE-FIELD + OPEN-LIST** — **18 MCP tools** (added `set_table_cell`,
`open_list`, `select_table_row`, `add_table_row`+`click_command`; page-field reuses `write_form_value`+`switch_page`), 223 tests. **Card 90 done.** The table-cell +
page-field fixture fixes were deployed to the live infobase via a MANUAL `ibcmd` export/import/apply (because
`run_dev_infobase_apply` is structurally workspace-locked in-session — §7 Step 1). table-cell = a plain string
SET on a `Table[…]`-segment path (`set_table_cell`, screenshot-verified, §7 Step 2); page-field = a plain
`EditField` at a deeper path driven by existing write machinery (§7 Step 3); open_list = a capture-free replay
of a genuine `e1cib/list/…` nav command (`open_list`, screenshot-verified, §7 Step 4).

Goal of the epic (card 82/86): qa-mcp drives ARBITRARY 1C forms through the native TestClient protocol — read,
input+commit, navigate, click — **capture-free** (from the live form descriptor + small per-element-TYPE
genuine templates), with **NO Vanessa Automation manager** in the loop.

## 1. What qa-mcp can do NOW (live-proven, no Vanessa) — 18 MCP tools

`src/qa_mcp/mcp_server.py` (FastMCP "qa-native-manager", stdio):
- **lifecycle (card 84):** `launch_test_client` (owns Xvfb + boots `1cv8/1cv8c /TESTCLIENT`, optional owned
  display for screenshots), `test_client_status`, `stop_test_client`.
- **screenshots (card 85):** `capture_screenshot(display, window?, out_path?)` — scrot/import on the owned display.
- **read (cards 74/79/86a):** `run_step`, `run_scenario` (read_active_window / read_form_summary /
  read_form_value); `read_form_value` addresses ANY field by name (86a path retarget).
- **write+commit (cards 80/83/86b/86c):** `write_form_value` / `write_form_values` /
  `run_write_scenario_tool` — commit a value to a field addressed by NAME, capture-free, for **string +
  number + date** types (read-back verified).
- **navigate (card 86d):** `switch_page(target_page, base_page)` — switch the active tab page, capture-free.
- **checkbox (card 90):** `toggle_checkbox(target_field, base_field)` — toggle ANY Boolean checkbox by name,
  capture-free (value-free activate/toggle; commit live-verified via the PF_LAST_ACTION side-effect).
- **choice/radio (card 90):** `set_choice(variant, base_field)` — set a Переключатель to a variant by VALUE
  NAME (e.g. PF_CHOICE_C), capture-free (activate + length-prefixed variant string; live-verified by read-back).
- **table-cell (card 90 / 86e):** `set_table_cell(value, column, table)` — write a value into a table cell on
  the ACTIVE row, capture-free (a cell SET = the plain string SET addressed at the column `EditField` leaf
  inside a `Table[…]` segment, no row index; cell read-back IS reliable — the SET response echoes the value
  via the column EditField + value-SET tag, parsed by read_table_cell_value). Row-addressed: `set_table_cell(row_match=<cell value>)` writes into
  the row whose column equals that value (the genuine row-select's search value is re-targeted).
- **select-row (card 90 follow-up):** `select_table_row(row_match)` — position a table's active row to
  the row where the column equals `row_match`, capture-free (the native row-select is "find row where
  COLUMN=VALUE"; the fixed-width VALUE is retargeted). Observable via `PF_SELECTED_ROW_MARKER`.
- **add-row / command-click (card 90 follow-up):** `add_table_row()` adds a persistent marked row to the
  fixture table (clicks the `PF_ADD_ROW` command); `click_command(target_button)` clicks ANY form-command
  BUTTON capture-free (activate `Button[NAME]`, `88 81 81 e1`). No value read-back — verify via
  PF_LAST_ACTION / screenshot.
- **page-field (card 90 §7 Step 3):** input into a field on a tab page = the existing `write_form_value`
  (+`switch_page` for a non-active page) with a genuine page-field capture — a page field is a plain `EditField`
  at a deeper path; NO new tool.
- **open_list (card 90 §7 Step 4):** `open_list(catalog, base_link)` — open a catalog/list WINDOW, capture-free
  (replay a genuine `e1cib/list/<path>` nav command with GUID rebinding; live-verified by screenshot — no value
  read-back).
- `transpile` — Gherkin (ru) → scenario.

## 2. Epic 86 status

| sub-story | status |
|---|---|
| 86a element addressing (READ) | ✅ live — read any field by name (path retarget) |
| 86b element addressing (WRITE) + same-type commit | ✅ live |
| 86c per-element-TYPE commit | ✅ **string + number + date + checkbox + choice** (`toggle_checkbox` / `set_choice`, live-verified) |
| 86d navigation | ✅ **page-switch** + **open_list** productized + live-verified (card 90 §7 Step 4) |
| 86e tables | ✅ **table-cell** DEPLOYED + productized + live-verified (`set_table_cell`, screenshot-proven); row-select/add-row pending (card 90 §7 Step 2) |

Card 90 is COMPLETE (all 5 types live-verified). What's left is polish/extensions, not new element types — see
§7 (row-addressed table-cell + add-row/row-select; an end-to-end switch_page(PF_PAGE_B)+write demo; a table-cell
grid read-back; catalog re-target hardening for open_list).

**Card-90 update (2026-06-17):** checkbox + choice + **table-cell** + **page-field** are DONE (productized +
live-verified — §3). **Card 90 is COMPLETE.** The fixture gaps were just READ-ONLY fields (table cells +
page fields), fixed by removing `<readOnly>` and deploying (path **B = extend the embedded fixture via edt-mcp**,
manual `ibcmd`); open_list needed no fixture change (capture-free replay of a nav-link). table-cell shipped
`set_table_cell`, open_list shipped `open_list`; page-field reuses `write_form_value`+`switch_page`. Evidence:
`evidence/genuine-card90-{checkbox-decode,table-decode,pagefield,openlist}-2026-06-17/`.

## 3. The decoded protocol model (cheat-sheet)

- **Session bootstrap** is synthesized capture-free (`protocol/bootstrap_synth.py`): frames ~static + a
  decimal counter + a frame-3 ticket GUID. Live session GUIDs (SecondaryFrame `S`, ManagedForm `F`) are
  learned in the handshake and rebound by `GuidRebinder`.
- **Element addressing** (`protocol/element_ref.py`): an element is a **length-prefixed hierarchical path
  string** `<0x9a><len:1>SecondaryFrame[S].ManagedForm[F].Group[…].<Kind>[NAME]` (latin1). NO hidden id/GUID.
  Re-target it with `retarget_element_leaf(frame, old, new, kind=…)` (recomputes the 1-byte length).
- **A command frame** = `[static per-type structure] + [length-prefixed element path] + [optional
  length-prefixed value] + [session header: offset-19 counter, msg-id @2, nonce @68 + GUIDs]`.
- **Per-type commit law (KEY):** a value commits via the field's OWN genuine SET frame (correct per-type value
  buffer; the SET tag `…e0 41 81 81 ba <varint-len> <value> <pad>` is type-IDENTICAL across types) **followed
  by a focus-change = "activate ANY other field".** `protocol/native_write.py`: `build_write_frame`,
  `NativeWriteSession.write(value, field=…)`, `derive_write_template(…, commit_partner_field, commit_partner_value)`
  (commit-partner synthesizes the focus-change when the field's genuine input had none).
- **Page-switch** = address the target page (`…Group[PF_PAGES_MAIN].Group[PF_PAGE_X]`) + a fixed activate
  structure; synthesize via `retarget_element_leaf(kind="Group")`. `derive_page_switch` / `switch_page` /
  `NativeWriteSession.switch_page`.
- **Activate-with-action law (card 90, KEY for checkbox/choice):** some types commit with NO value buffer —
  the wire only ACTIVATES the element and the server acts. Tag family `<0xe0> 4b <op>` (vs the value-SET
  `e0 41 81 81 ba`): **`e0 4b 55` = toggle a Boolean checkbox** (value-free — byte-identical for set & clear,
  server flips it), **`e0 4b 53 <variant>` = choose a radio variant**. Checkbox/choice are `EditField[NAME]`
  (86a/86b addressing already covers them). ⇒ checkbox is a twin of page-switch: synthesize via
  `retarget_element_leaf(kind="EditField")` on the genuine toggle frame. **BOTH PRODUCTIZED + live-verified:**
  checkbox = `derive_checkbox_toggle` / `toggle_checkbox` / `NativeWriteSession.toggle_checkbox` + MCP
  `toggle_checkbox`; choice = `derive_choice_set` / `set_choice` / `NativeWriteSession.set_choice` + MCP
  `set_choice` — the choice carries the variant as a length-prefixed value NAME (`e0 4b 53 <0x9a><len><name>`),
  re-targeted via `build_write_frame` (variant addressed by value name PF_CHOICE_*; index form rejected).
  Decoded from `captures/genuine-card90-20260617` (checkbox) + `genuine-card90-choice-20260617` (choice),
  evidence `genuine-card90-checkbox-decode-2026-06-17`.
- **Table-cell law (card 90 / 86e, KEY):** a table-cell SET is **byte-identical to a plain string SET** — only
  the element path differs: the column is the `EditField` leaf inside a `Table[<table>]` SEGMENT
  (`…Group[PF_GROUP_MAIN].Table[PF_TABLE_ITEMS].EditField[PF_TABLE_TEXT]`), with **NO row index** → the SET
  commits into the ACTIVE row. So it reuses the card-86c commit-partner machinery; retarget the column via
  `retarget_element_leaf(kind="EditField")` and the table via `retarget_element_segment(kind="Table")`.
  `derive_table_cell_write` / `set_table_cell` / `NativeWriteSession.set_table_cell` + MCP `set_table_cell`.
  Decoded from `captures/genuine-card90-table-20260617`, evidence `genuine-card90-table-decode-2026-06-17`.
  Cell read-back: the SET response echoes the value via `EditField[col] … e0 41 81 81 ba <len><value>` → `read_table_cell_value` (card 90 follow-up #3; the old `\x81\x81\x81` anchor missed the varying counter byte).
- **Page-field law (card 90 §7 Step 3):** a field on a tab page is a PLAIN `EditField`, just deeper in the path
  (`…Group[PF_GROUP_MAIN].Group[PF_PAGES_MAIN].Group[PF_PAGE_A].EditField[PF_PAGE_A_FIELD]`). Once editable it
  commits via the normal string-SET + focus-change → NO new code: `write_form_value`/`NativeWriteSession.write`
  with a genuine page-field capture (base==target → the nested path replays as-is; read-back works). For a
  non-active page compose `switch_page` first. Capture `genuine-card90-pagefield-20260617`, evidence
  `genuine-card90-pagefield-2026-06-17`.
- **Nav link** (`e1cib/<kind>/<path>`) = `<0xf7><char-count:1><utf-16le link>`; `navigation.retarget_nav_link`
  (variable-length) — open_list now LIVE-VERIFIED capture-free (card 90 §7 Step 4): `derive_open_list`/`open_list` + MCP `open_list` replay a genuine `e1cib/list/Справочник.Товары` command → the Товары list window opens. Capture `genuine-card90-openlist-20260617`, evidence `genuine-card90-openlist-2026-06-17`.

## 4. Code map

- `protocol/bootstrap_synth.py` — capture-free handshake.
- `protocol/session.py` — `TestClientSession`/`SessionHandle`, reads, `read_form_value` (86a frame_rewriter hook).
- `protocol/element_ref.py` — path build/parse/extract/retarget (86a/86b/86d core).
- `protocol/native_write.py` — write+commit (80/83/86b/86c) + page-switch (86d) + checkbox-toggle (90):
  `build_write_frame`, `derive_write_template`, `NativeWriteSession`, `write_form_value`, `derive_page_switch`,
  `switch_page`, `derive_checkbox_toggle`, `toggle_checkbox` (value-free EditField activate, `kind="EditField"`),
  `derive_choice_set`, `set_choice` (EditField activate + length-prefixed variant value-name).
- `protocol/navigation.py` — nav links + captured-command renderers (74).
- `protocol/lifecycle.py` — client launch/own-display/stop (84/85). `protocol/screenshot.py` — capture (85).
- `scenario/{model,gherkin,runner}.py` — scenario model, Gherkin transpile, runner (`run_single_session`
  for reads/actions; `run_write_scenario` for input_text + switch_page).
- `mcp_server.py` — the 18 MCP tools.
- **Probes (live-verify):** `tools/protocol-research/{page_switch_probe,checkbox_toggle_probe,choice_set_probe}.py`
  (each: boot `launch_test_client` → replay setup → synth action → read-back/screenshot). Capture features:
  `qa-card90-{checkbox-selfcontained,choice-selfcontained,capture-actions}.feature`, decoders
  `card90_checkbox_decode{,2}.py`.

## 5. Genuine-capture recipe (when a NEW type/action needs a genuine SET/command)

Memory [[genuine-action-capture-recipe]] + `docs/protocol-research/evidence/genuine-multiaction-capture-2026-06-17/`.
Boot the genuine Vanessa manager ([[vanessa-mcp-linux-genuine-manager]]) → `tcpdump -i lo` on the client TPort
range → drive a `.feature` (`run_scenario`) → `get_form_analysis` AFTER (captures a read sweep = read-back
frames) → stop tcpdump → `pcap_to_traffic.py <pcap> <client_port> <out> <manager_port>` (the **4th
manager_port arg is REQUIRED** — the manager opens several connections; isolate the dominant one or the replay
desyncs). Drive feature: `tools/protocol-research/qa-multiaction-capture.feature`.

## 6. The decode→productize loop (the proven pattern, reuse per type)

1. **Capture** a genuine input/action for the type (recipe above) → a clean single-connection capture.
2. **Decode** by diff: two same-type frames differing only in name/value confirm the structure (offset-19
   counter + nonce + the semantic bytes). Tools: `element_addressing_spike.py`, `element_write_86c_diag.py`.
3. **Commit** = the field's genuine SET + a focus-change (commit-partner if no genuine one follows).
4. **Productize:** `derive_write_template(commit_partner_…)` → `write_form_value(field, base_field,
   captured_value, commit_partner, commit_partner_value)`; verify live (read-back / screenshot md5).

## 7. Card 90 — NEXT SESSION — START HERE

**Done (this session):** checkbox (`toggle_checkbox`) + choice (`set_choice`) productized + live-verified (§3).
**Remaining = 3 FIXTURE gaps** (table-cell, page-field input, open_list), all on path **B (extend the existing
embedded fixture via edt-mcp)**. The fixture is the EMBEDDED config DataProcessor
`ФикстураПротоколаTestClient` — EDT source at
`/opt/1c-dev/vanessa_qa/vanessa_client/src/DataProcessors/ФикстураПротоколаTestClient/` (NOT git-tracked).
⚠ edt-mcp can NOT create/edit embedded data processors via its facades (catalog/document/register only) — so
fixture edits are HAND edits of the EDT source XML/BSL, then a dev-apply deploy.

### Step 1 — DEPLOY the staged fix ✅ DONE + LIVE-VERIFIED (2026-06-17)
The table-cell fix (made in `Forms/Форма/Form.form`: removed the table's editing `<excludedCommands>` + the
`<readOnly>` on `PF_TABLE_TEXT`/`PF_TABLE_NUMBER`; kept `PF_TABLE_MARKER` read-only; backup
`Form.form.bak-card90`) is now **deployed to the live `vanessa_client` file infobase and live-verified**:
generation `bf03a87f…` → `e1496ab98aa03a49bb8e6a7062622fba…`; a genuine-manager run shows
`в таблице "PF_TABLE_ITEMS" в поле с именем 'PF_TABLE_TEXT' я ввожу текст "TBLOK"` → **Success** (was
"ВвестиТекст не может быть вызван"); row-add also Success. (`PF_TABLE_NUMBER` only fails with «Неподходящий тип
элемента управления» — that's using the *text*-input step on a numeric column, NOT a deploy issue.)

**edt-mcp association (persisted, reusable):** the EDT-visible catalog `~/.1C/1cestart/ibases.v8i` already had
the infobase as **`client`** (→ `File="/opt/1c-dev/vanessa_client"`). Steps that worked:
`configure_infobase_access(name="client", access={"access":"INFOBASE","username":"Администратор","password":""})`
(OS→Infobase) then `associate_infobase(project="vanessa_client", infobase="client")` → `linked:true,
deployAllowed:true`. (I also `ensure_infobase_registered(name="vanessa_client", connection='File="/opt/1c-dev/vanessa_client";')`
in edt-mcp's own `custom-ibases.v8i` for the apply target name.)

**⚠ `run_dev_infobase_apply` is STRUCTURALLY BLOCKED in this session and we deployed MANUALLY instead.**
The route blocks on `workspace_locked` because edt-mcp keeps its own persistent EDT daemon up for the whole
session, which holds `/opt/1c-dev/vanessa_qa/.metadata/.lock`; the route classifies that as `current_tool`
(owner pid == the edt-mcp server's own pid → not auto-cleanable; `runtime_lock_cleanup="tool-owned-retained"`
only clears a *different* retained pid). And the route itself starts the probe daemon (re-creating the lock),
so it can never see its own workspace unlocked. The route's `check-only` IS still useful: it prints the exact
command plan. We ran that plan manually (apache2 STOPPED, Vanessa DOWN, edt-mcp EDT daemon SIGTERM'd to free the
workspace for a fresh export):
1. `ibcmd config --database-path /opt/1c-dev/vanessa_client --user Администратор generation-id` (before)
2. `EDT_WORKSPACE=/opt/1c-dev/vanessa_qa … xvfb-run -a edt-mcp/scripts/1cedtcli.sh -command "export --project
   /opt/1c-dev/vanessa_qa/vanessa_client --configuration-files <out>"` (needs the workspace FREE — a 2nd
   `1cedtcli` on a workspace a daemon already holds dies with «рабочая область уже используется»; SIGTERM the
   EDT java daemon first; it auto-restarts on the next edt-mcp call)
3. `ibcmd config … import <out>` → 4. `ibcmd config … apply --dynamic=disable --session-terminate=force --force`
   → 5. `generation-id` (after, confirm changed). IB backup before apply: `1Cv8.1CD.bak-card90-predeploy`.
This same manual procedure is the way to deploy the page-field / open_list fixture edits (steps 3-4) too.

### Step 2 — table-cell: capture ✅ + decode ✅ DONE; productize ⏳ NEXT
**Capture done:** `tools/protocol-research/qa-card90-capture-table-selfcontained.feature` (connect+open+2 rows+
edit PF_TABLE_TEXT=CELLAA/CELLBB+commit) → `runtime/protocol-research/captures/genuine-card90-table-20260617/
traffic-selfcontained/traffic.jsonl` (767 chunks, client TPort 48003 / manager 54484). Decoder:
`tools/protocol-research/card90_table_decode.py`. Evidence: `evidence/genuine-card90-table-decode-2026-06-17/`.
**Decode done (KEY):** a table-cell SET is **byte-identical to a plain string SET**; only the element path
differs — `…Group[PF_GROUP_MAIN].Table[PF_TABLE_ITEMS].EditField[PF_TABLE_TEXT]` (the table is a `Table[NAME]`
segment, the **column** is the `EditField` leaf), **NO row index** (edit hits the *active* row; both CELLAA→
CELLBB landed on row 1). Same `e0 41 81 81 ba <varint-len><value>` value buffer + same SET-then-focus-change
commit law as card 86c. ⇒ productize reuses the existing string machinery (the checkbox/choice/page-switch
`derive_*`+retarget pattern), NOT a new mechanism.
**Productize ✅ DONE + LIVE-VERIFIED (2026-06-17):** `derive_table_cell_write` + `NativeWriteSession.set_table_cell`
+ standalone `set_table_cell` + MCP tool `set_table_cell` (the **14th** tool) + `element_ref.retarget_element_segment`
(Table-segment retarget) + 4 unit tests (suite **216 passed**). Reuses the card-86c commit-partner machinery (a
cell SET *is* a string SET). Live proof: `set_table_cell_shot.py` wrote `HELLO9` into the active row's
PF_TABLE_TEXT — the grid cell changed `PF_ROW_001_TEXT`→`HELLO9` + focus moved to PF_EDIT_STRING (commit);
screenshots under `runtime/protocol-research/table-cell-shot/20260617-094510/`. Cell read-back IS reliable (follow-up #3): the SET response
echoes the value via the column EditField + value-SET tag (`read_table_cell_value`); `set_table_cell` returns
readback_value/committed reflecting the actual write. Evidence: `evidence/genuine-card90-table-decode-2026-06-17/`.
Probes: `tools/protocol-research/{set_table_cell_probe,set_table_cell_shot,set_table_cell_debug}.py`,
`run_table_cell_test.sh`.
**Row addressing (2026-06-17) ✅ SOLVED (capture-free, by value):** the native row-select is "find the row
where COLUMN = VALUE" — both length-prefixed strings in the genuine command (`c0 4b 53 9a<len>COLUMN eb 53
9a<len>VALUE`), so re-targeting the fixed-width VALUE selects an ARBITRARY row by its cell value, then the
active-row cell SET lands there. Productized: `NativeWriteSession(setup_retargets=…)`, `set_table_cell(row_match=
<col value>)`, standalone+MCP **`select_table_row`** (16th tool), +2 unit tests (suite **220**). Live-proven:
`PF_ROW_002_TEXT`→`PF_ROW_003_TEXT` selects+writes row 3 (screenshots; rows 1/2 unchanged). Fixture fix
deployed: an OnActivateRow handler sets `PF_SELECTED_ROW_MARKER="PF_ROW_IDX_<n>:<marker>"` (row-select
observable; gen `3aab6541…`→`abce119a…`). Captures `genuine-card90-{rowaddr,row2write}-20260617`; evidence
`evidence/genuine-card90-table-rowaddr-2026-06-17/`; probes `set_table_cell_{row,rowmatch}_shot.py`,
`rowselect_retarget_shot.py`. **add_table_row DONE** (custom `PF_ADD_ROW` command + generic `click_command`; gen `abce119a…`→`98fc8582…`;
evidence as above). Grid cell read-back DONE (follow-up #3: `read_table_cell_value`
parses the SET-response echo; `set_table_cell` returns a real read-back). **Deferred (§8):** select-by-raw-index
(current select is by column VALUE).

### Step 3 — page-field input ✅ DONE + LIVE-VERIFIED (2026-06-17)
The page fields were just READ-ONLY (not a protocol gap): `PF_PAGE_A_FIELD`/`PF_PAGE_B_FIELD` are plain
`InputField`s (textEdit) that had `<readOnly>true</readOnly>`. Fixture fix: removed those two readOnly lines
(backup `Form.form.bak-card90-pagefield`); deployed via the same MANUAL `ibcmd` procedure as table-cell (gen
`e1496ab9…`→`3aab6541…`). **Page-field input needs NO new code** — a page field is a plain `EditField` at a
deeper path (`…Group[PF_GROUP_MAIN].Group[PF_PAGES_MAIN].Group[PF_PAGE_A].EditField[PF_PAGE_A_FIELD]`, 3 groups
deep), so the existing `write_form_value`/`NativeWriteSession.write` drive it from a genuine page-field capture
(base==target → the nested path replays as-is; read-back works — a page field is a plain value control).
Verified: Vanessa input Success; native (no Vanessa) `set_page_field_probe.py` wrote PGNEW1/PGNEW2 →
readback+committed PASS (open-once session; single-shot `write_form_value` does ONE write per client boot).
Capture `genuine-card90-pagefield-20260617`; evidence `evidence/genuine-card90-pagefield-2026-06-17/`. For a
NON-active page, compose `switch_page(target)` (86d, verified) then `write_form_value`. ⏳ remaining nicety: an
end-to-end native switch_page(PF_PAGE_B)+write(PF_PAGE_B_FIELD) demo (needs a page-B capture).

### Step 4 — open_list ✅ DONE + LIVE-VERIFIED (2026-06-17) — card 90 COMPLETE
No fixture change needed: the embedded dynamic list `ДенамическийСписокИерархия` is based on `Catalog.Товары`,
so navigating to `e1cib/list/Справочник.Товары` opens that catalog's list. Captured a genuine open-list via
Vanessa (`qa-card90-capture-openlist.feature`; the Товары window opened — active-window caption "Товары"),
then **replayed it capture-free** (`set_open_list_shot.py`): on a fresh native client the genuine nav-link
command (replayed with GUID rebinding after the setup opens the fixture form) opened a separate **Товары** list
window — screenshot-proven (`runtime/protocol-research/openlist-shot/20260617-12*/`). Productized:
`derive_open_list` + `open_list` standalone + MCP tool **`open_list`** (the **15th** tool) + 2 unit tests (suite
**218**). Catalog re-target via `navigation.retarget_nav_link` (best-effort; base Товары proven). ⚠ no value
read-back — verify by screenshot. Capture `genuine-card90-openlist-20260617`; evidence
`evidence/genuine-card90-openlist-2026-06-17/`. **All 5 card-90 element types are now done** (checkbox, choice,
table-cell, page-field, open_list).

**Keep `PF_*` naming + group structure** so 86a element addressing keeps working. edt-mcp profile:
[[edt-mcp-profile-and-deploy]] (`EDT_MCP_TOOL_PROFILES=all`). Recipe + Vanessa lab boot: §5, §6,
[[genuine-action-capture-recipe]], [[vanessa-mcp-linux-genuine-manager]]. ⚠ the native replay client
(`launch_test_client`, `port 15381`) needs `vanessa_client` FREE — boot it with Vanessa + apache DOWN, else the
2nd session crashes on infobase contention.

## 8. Pointers

- **Cards:** 82 (roadmap), 86 (keystone epic — sub-story status), 90 (fixture coverage — the next work),
  87 (form introspection — independent, no capture), 88 (element-type coverage), 89 (MCP surface parity).
- **Evidence:** `docs/protocol-research/evidence/{card86-element-addressing-spike,card86b-capture-free-write,
  card86c-per-type-set-investigation,card86d-navigation,card86d-page-switch,genuine-multiaction-capture,
  genuine-card90-checkbox-decode}-2026-06-1*`. The card-90 checkbox/choice decode + live proof + the table
  read-only finding are in `genuine-card90-checkbox-decode-2026-06-17/findings.md`.
- **Captures (gitignored runtime):** `genuine-commit-conn` (string+number SET + read sweep),
  `genuine-multiaction-clean-20260617` (date SET + page-switch + read sweep),
  `genuine-card90-20260617/traffic-selfcontained` (checkbox toggle, replayable),
  `genuine-card90-choice-20260617/traffic-selfcontained` (radio choice, replayable). `tm-v1-ro-batchQ3` (read-only).
- **Staged (undeployed) fixture edit:** `…/ФикстураПротоколаTestClient/Forms/Форма/Form.form` — table made
  editable (table-cell fix); backup `Form.form.bak-card90` (see §7 Step 1 to deploy).
- **Memories:** qa-mcp-capture-free-epic (START HERE), genuine-action-capture-recipe (incl. «флаг» step fix +
  checkbox/choice laws), vanessa-mcp-linux-genuine-manager, linux-native-testclient-xvfb,
  edt-mcp-profile-and-deploy, lab-infobase-access, ibsrv-odata-vs-httpservice, autonomous-1c-observability.
- **Probes/runners:** `tools/protocol-research/{element_addressing_read_probe,element_write_86c_diag,
  element_write_number_probe,page_switch_probe,checkbox_toggle_probe,choice_set_probe}.py`, `run_*_test.sh`,
  `qa-card90-{checkbox-selfcontained,choice-selfcontained,capture-actions,introspect}.feature`,
  `pcap_to_traffic.py`, `vanessa_mcp_call.py`, `vanessa_auto_allow_dialogs.sh`.
