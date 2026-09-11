# 75. Protocol tail coverage (unsupported_initial + safe_ui candidates)

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-14: follow-up #4 from the native runner work. The replacement architecture is complete
  (134/160 accepted + full runner/MCP); this card grows the remaining coverage %.

## Summary
The tail members are actions accepted via the capture → probe (probe-ordinal) → promote loop.
Investigation (2026-06-14) found most are gated on fixture/config additions (user side), with their
exact Vanessa steps identified:

| member | class | status / what unblocks it |
| --- | --- | --- |
| TestedFormTable.Choose | unsupported_initial | **✅ ACCEPTED 2026-06-14** — captured via `fixture-table-choose.json`; probe_runner replay → `compare_probe_reference --mode probe-ordinal --phase action` verdict=accepted (structural_match + client/manager hashes match) → promoted to accepted_reviewed (134→135). Evidence: `evidence/tail-corpus/table-choose-2026-06-14/`. NOTE: the full-capture probe replay hangs in the long post-action poll tail (killed after the action phase replayed correctly); compare ran on the captured action frames. |
| TestedForm.ExecuteChoiceFromList | unsupported_initial | BLOCKED — step `И я выбираю из списка "Значение"` requires the form to show a list via `ПоказатьВыборИзСписка()` (event-intercept popup); the plain ComboBox does NOT trigger it. Needs fixture code. |
| TestedForm.ExecuteChoiceFromMenu | unsupported_initial | **✅ ACCEPTED 2026-06-14** — button `PF_SHOW_CHOICE_MENU` added; captured `fixture-choice-menu-cap` (open → click PF_SHOW_CHOICE_MENU → `И в меню формы я выбираю 'PF_MENU_2'`); PF_MENU_2 choose command @ord293 (UTF-8); bounded native replay `--max-ordinal 294` → diverged_at=null (292/292) → promoted (136→137). Evidence `evidence/tail-corpus/choice-menu-2026-06-14/`. |
| TestedFormDecoration.ClickFormattedStringHyperlink | unsupported_initial | **✅ ACCEPTED 2026-06-14** — decoration `PF_DECORATION_FMT` (caption `Новый ФорматированнаяСтрока("Открыть ", Новый ФорматированнаяСтрока("ссылку",,,,"PF_FMT_LINK"))`) added. KEY: the Vanessa step is `И у поля с именем 'PF_DECORATION_FMT' я нажимаю гиперссылку 'ссылку' по шаблону` (changelog #1119), NOT `нажимаю на гиперссылку с именем` (that does element-name lookup → fails). The click command encodes the DECORATION element name `PF_DECORATION_FMT` in UTF-16LE @ord283 (not the presentation/value). Bounded native replay `--max-ordinal 284` → diverged_at=null (285/285) → promoted (137→138). Evidence `evidence/tail-corpus/fmt-hyperlink-2026-06-14/`. |
| TestedClientApplicationWindow.GotoNextWindow / GotoPreviousWindow / GotoStartPage | safe_ui_action candidate | BLOCKED — need a multi-window / main-window navigation context in the demo config. |
| TestedClientApplicationWindow.ChooseUserMessage | safe_ui_action candidate | BLOCKED — needs a user-message panel with a clickable message. |
| TestedForm.Activate / TestedFormButton.Activate | safe_ui_action candidate | BLOCKED — no driver/target in the demo config (focus move with nothing to assert). |
| TestedFormTable.Expand | safe_ui_action candidate | BLOCKED — needs a dynamic-list HIERARCHY table (tree) to expand. |

The 3 remaining read_only (WaitForCondition, Field/Decoration.GetObject) are closed (user-deferred /
architecturally N/A).

## RESUME — protocol next steps (context anchor, 2026-06-14)
Goal: replace the Vanessa test manager. State: **136/160 accepted_reviewed** (+1 seed, 7 candidate,
16 uncovered). Architecture DONE — bootstrap synthesized (cards 62/73), native runner read/click/
input + Gherkin + MCP (card 74, all proven live, zero divergence). This card grows the remaining %.

**The proven per-tail-member acceptance loop:**
1. USER adds the fixture form element (+ BSL handler from this card) in the Configurator/EDT designer,
   does **F7 (update DB config)**, closes the Configurator (frees the license).
2. qa-mcp authors an action manifest (`tools/protocol-research/action-manifests/<id>.json`):
   `open fixture form` → trigger steps → the ACTION step.
3. Capture: `run_protocol_capture.ps1 -Scenario demo-action-manifest -ActionManifest <m> -RunId <id>-cap`.
4. Locate the action command ordinal (`find_marker_ordinal`, tries UTF-16LE then UTF-8).
5. **Bounded native replay** (NOT probe_runner — it hangs in the poll tail):
   `native_action_scenario.py <capture> --scenario <form_command @marker> --max-ordinal <past action>
   --keep-every-poll 8` against a fresh client (15381) → `diverged_at_send_index=null` = accepted.
6. `promote_member.py --api <member> --bucket accepted_reviewed --evidence docs/.../tail-corpus/<id>/`.

**Remaining tail members (each gated on the USER adding the fixture element below):**
- ✅ Table.Choose, ✅ ExecuteChoiceFromList, ✅ ExecuteChoiceFromMenu, ✅ ClickFormattedStringHyperlink (all done).
- D. safe_ui candidates (7) — NEXT: Table.Expand (tree table), GotoNext/Prev/StartPage (multi-window),
    ChooseUserMessage (message panel — link-click already populates one), Form/Button.Activate.
- 3 read_only (WaitForCondition, Field/Decoration.GetObject): closed (deferred / architecturally N/A).

(Detour 2026-06-14: testing whether qa-mcp can make the fixture/config edits itself via edt-mcp
on `C:\1C_BASES\EDT\vanessa_qa\vanessa_client\src\` + deploy to the base — would remove the manual
designer step from the loop above. edt-mcp was disconnected at detour start; reconnect needed.)

## Fixture additions spec (2026-06-14) — division of labour
Form elements (buttons/decorations/tree tables) are added by the USER in the Configurator/EDT form
designer (as with the decorations/combo/Контрагент). The BSL handlers below are supplied here; once
the element + handler are in, qa-mcp does capture → probe-ordinal → promote. EDT project:
`C:\1C_BASES\EDT\vanessa_qa\vanessa_client`.

### A. TestedForm.ExecuteChoiceFromList — ✅ ACCEPTED 2026-06-14 (button `PF_SHOW_CHOICE_LIST` added)
Captured `fixture-choice-list-cap2` (open → click PF_SHOW_CHOICE_LIST → choose PF_CHOICE_B); bounded
native replay `--max-ordinal 291` (choose command @ord290, located via UTF-8 find_marker) →
diverged_at=null (289/289) → promoted (135→136). Evidence `evidence/tail-corpus/choice-list-2026-06-14/`.
NOTE: probe_runner full-replay must run PAST the action ordinal before killing the poll-tail hang —
bounded native_action_scenario is the reliable path. The button element name must match the click
step (Имя), and the DB config must be updated (F7), not just saved.
Original spec (for reference):
```bsl
&НаКлиенте
Процедура PF_SHOW_CHOICE_LIST(Команда)
    Список = Новый СписокЗначений;
    Список.Добавить("PF_CHOICE_A"); Список.Добавить("PF_CHOICE_B"); Список.Добавить("PF_CHOICE_C");
    ПоказатьВыборИзСписка(Новый ОписаниеОповещения("PF_ChoiceListDone", ЭтотОбъект), Список);
КонецПроцедуры
&НаКлиенте
Процедура PF_ChoiceListDone(Выбранный, Доп) Экспорт
    Если Выбранный <> Неопределено Тогда Сообщить("PF_CHOICE=" + Выбранный.Значение); КонецЕсли;
КонецПроцедуры
```
Vanessa capture: click `PF_SHOW_CHOICE_LIST` → `И я выбираю из списка "PF_CHOICE_B"`.

### B. TestedForm.ExecuteChoiceFromMenu — add a button `PF_SHOW_CHOICE_MENU`
```bsl
&НаКлиенте
Процедура PF_SHOW_CHOICE_MENU(Команда)
    Меню = Новый СписокЗначений; Меню.Добавить("PF_MENU_1"); Меню.Добавить("PF_MENU_2");
    ПоказатьВыборИзМеню(Новый ОписаниеОповещения("PF_MenuDone", ЭтотОбъект), Меню);
КонецПроцедуры
&НаКлиенте
Процедура PF_MenuDone(Выбранный, Доп) Экспорт
    Если Выбранный <> Неопределено Тогда Сообщить("PF_MENU=" + Выбранный.Значение); КонецЕсли;
КонецПроцедуры
```
Vanessa capture: click `PF_SHOW_CHOICE_MENU` → `И в меню формы я выбираю 'PF_MENU_2'`.

### C. TestedFormDecoration.ClickFormattedStringHyperlink — add a Надпись decoration `PF_DECORATION_FMT`
In `ПриСозданииНаСервере`:
```bsl
Элементы.PF_DECORATION_FMT.Заголовок = Новый ФорматированнаяСтрока(
    "Открыть ", Новый ФорматированнаяСтрока("ссылку", , , , "PF_FMT_LINK"));
```
Decoration event handler:
```bsl
&НаКлиенте
Процедура PF_DECORATION_FMTОбработкаНавигационнойСсылки(Элемент, Ссылка, СтандартнаяОбработка)
    СтандартнаяОбработка = Ложь; Сообщить("PF_FMT_CLICK=" + Ссылка);
КонецПроцедуры
```
Vanessa capture: `И я нажимаю на гиперссылку с именем 'PF_FMT_LINK'` (decoration formatted-string hyperlink).

### D. safe_ui candidates (bigger fixture/config changes — later)
- Table.Expand: add a tree (hierarchical dynamic-list or a tree value-table) to the fixture form.
- GotoNextWindow/PrevWindow/StartPage: need a second open window / a main-window navigation context.
- ChooseUserMessage: a user-message panel with a clickable message (the link-click `Сообщить` already
  populates one — likely doable: capture the link click then "выбираю сообщение").
- Form.Activate / Button.Activate: a focus driver/target to assert the activation.

## Acceptance
- TestedFormTable.Choose accepted (capture → probe-ordinal → promote).
- For each BLOCKED member: the precise fixture/config addition is recorded above; when the user adds
  it (ПоказатьВыборИзСписка/Меню popups, a formatted-string-hyperlink decoration, a tree table, a
  multi-window context), run the same capture→probe→promote loop.

## Next
- triage: do Table.Choose; batch the rest after the fixture/config additions.

## STUDY 2026-06-14 — direct test-API path for the 7 safe_ui candidates (decision: prove on 1, then batch)
The 7 remaining candidates were re-investigated. **Root blocker is NOT fixtures — it is the Vanessa
step library having no wrapper** that calls these API methods (recorded in the evidence-map notes):
- GotoNextWindow / GotoPreviousWindow / GotoStartPage / ChooseUserMessage — "No VanessaAutomation step
  drives this method (none in step_definitions, none in the step DB)".
- Form.Activate — no step; `я активизирую форму` drives **window** Activate, not form Activate.
- Button.Activate — no `активизирую кнопку` step; the field-finder doesn't reach command-bar buttons.
- Table.Expand — **platform limitation**: `Развернуть` throws `Неподходящее состояние элемента
  управления` on a collapsed dynamic-list group row (both `Развернуть()` and `Развернуть(,Истина)`);
  Collapse works, Expand doesn't. Needs a static `ДеревоЗначений` tree — Товары/Контрагенты won't work.

**Key finding — the capture harness already drives the raw test-API directly**, bypassing Vanessa steps:
the `manager-fixture-v1` inline harness (`New-ManagerHarnessInlineCommandBlock`, `run_protocol_capture.ps1`)
connects its OWN `ТестируемоеПриложение`, `УстановитьСоединение()`, and dispatches `command_kind`
snippets that call raw API (`ПолучитьАктивноеОкно()`, `НайтиОбъект(...).Активизировать()`, …). This is
how read_only was accepted. It runs through the proxy, so the raw call **emits + captures the protocol
command** → we can then bounded-replay it (`native_action_scenario.py`, diverged_at=null) to accept.

**V2 safe-action subsystem exists but stalled.** `v2_safe_action_tooling.py` + scenario
`manager-fixture-v2-safe-action` (board cards 02/06/10/40/50/60) was purpose-built for exactly these
families (`activate_existing_window_or_form`, `focus_existing_element`, `expand_or_collapse_menu_or_group`).
It ran LIVE on 2026-06-07 (`runtime/.../captures/20260607-first-focused-v2-safe-action-live-runner*`) but
produced **only candidate rows, 0 accepted** — gated on `missing_action_frame_range`,
`replay_or_probe_unavailable`, `pending_action_result`. The proven bounded-replay (this card's tail loop)
is exactly the missing piece. **Decision (user, 2026-06-14):** don't revive V2; prove via the simpler
`command_kind` + bounded-replay path on ONE member (Form.Activate), then batch the rest.

**Per-member feasibility / plan (existing config, NO fixture edits for 6/7):**
| member | family | direct-API call | data-safety |
| --- | --- | --- | --- |
| TestedForm.Activate | activate form | `НайтиОбъект(ТестируемаяФорма,"QA MCP Protocol Fixture V1").Активизировать()` | read-only focus — PROVE FIRST |
| TestedFormButton.Activate | focus element | `НайтиОбъект(ТестируемаяКнопкаФормы,,имя).Активизировать()` on Документ.Заказ form | read-only focus |
| GotoNextWindow / GotoPreviousWindow | window nav | open 2 windows (Контрагенты+Товары) → `ПолучитьАктивноеОкно().ПерейтиКСледующемуОкну()` | read-only |
| GotoStartPage | window nav | `ПолучитьАктивноеОкно().ПерейтиКНачальнойСтранице()` | read-only |
| ChooseUserMessage | window | `ПолучитьАктивноеОкно().ВыбратьСообщениеПользователю(...)` — needs a message in the panel | user: try **Расширение2** handler (no mutation) first, then post Документ.Заказ ref bbf30050 (mutation → COM snapshot→restore) |
| Table.Expand | expand | platform limit on dynamic lists | needs a static `ДеревоЗначений` fixture (defer / separate) |

**Mechanism to implement (Form.Activate proof):** (1) add a `form_activate` `command_kind` branch in
`New-ManagerHarnessInlineCommandBlock`; (2) add a catalog case in
`manager_fixture_v1_command_catalog.json` with `safety_class=safe_ui_action`; (3) relax the catalog
validator (`Read-ManagerFixtureV1Catalog`, currently read_only/bootstrap_navigation only) to accept
`safe_ui_action`; (4) capture via `-Scenario manager-fixture-v1-readonly -CaseIds <case>` with
`-ManagerFixtureV1OpenFixtureViaCommandInterfaceBootstrap` (opens the fixture form first); (5) locate the
Активизировать command ordinal; (6) bounded `native_action_scenario.py` replay → diverged_at=null;
(7) `promote_member.py`. Then batch the other 5 (window-nav + button) the same way.

## Log
- 2026-06-14: card created; tail investigated, exact Vanessa steps + per-member blockers recorded.
- 2026-06-14: tail members accepted via fixture+bounded-replay loop — Table.Choose, ExecuteChoiceFromList,
  ExecuteChoiceFromMenu, ClickFormattedStringHyperlink (135→138/160).
- 2026-06-14: STUDY of the 7 safe_ui candidates (above) — root blocker = no Vanessa step; chosen path =
  raw test-API `command_kind` + bounded-replay; V2 subsystem stalled at candidate; prove Form.Activate first.
- 2026-06-14: PROOF (Form.Activate, partial). Added `form_activate` `command_kind` +
  `tm-v1-form-activate` catalog case + relaxed the catalog validator to accept `safe_ui_action`.
  Capture `fixture-form-activate-cap` via `manager-fixture-v1-readonly -ManagerFixtureV1CaseId
  tm-v1-form-activate -ManagerFixtureV1OpenFixtureViaCommandInterfaceBootstrap`: **status=ok, command
  executed** (`form_activated=QA MCP Protocol Fixture V1`), 307 manager chunks captured → the direct
  test-API command_kind path WORKS (the core feasibility claim). BUT acceptance via zero-divergence
  replay does NOT fit this capture type: probe_runner adaptive replay **diverged_at_send_index=22
  (21/307)** in the BOOTSTRAP — the manager-fixture-v1 command-interface bootstrap (section-button
  presses) is not deterministically replayable (accepted safe-ui like Table.Collapse used a nav-link
  `e1cib/list/...` bootstrap → 198/198). Also `Активизировать` is markerless (no string in the manager
  stream) so it can't be isolated for bounded-replay-by-marker. native_action_scenario likewise reset
  (it expects action-manifest captures). **Conclusion:** these 6 are EXECUTABLE + CAPTURABLE via direct
  API, but the realistic acceptance class is the **result-contract** (same as read_only:
  manager_result_preview + command frames present = accepted_protocol_mapping), NOT zero-divergence
  replay — unless a deterministic (nav-link) bootstrap is added for manager-fixture-v1 to make the
  replay clean. DECISION PENDING (asked user): result-contract accept vs invest in a replayable bootstrap.
- 2026-06-14: user chose "make bootstrap replayable". Diagnosed frame-22 divergence = JSON form-desc
  frames with an UNMAPPED GUID (captured 11 / mapped 10). Tried **Route B (connect-only)**: new
  `active_form_activate` command_kind + `tm-v1-active-form-activate` case, capture with
  `-ManagerFixtureV1ActivateAppWindowBootstrap` only → command OK (`active_form_activated=Продажи`, 253
  frames) but probe-replay STILL diverged at frame 16 (15/253), again ONE unmapped GUID (7/6).
  **CONCLUSION: divergence is the raw-API `ТестируемоеПриложение` (manager-fixture-v1) connection's
  early session frames carrying a GUID the GuidRebinder doesn't rebind — NOT the navigation.** Accepted
  safe-ui replayed clean via the VANESSA connection (action-manifest). Route B OUT. Remaining: (A)
  Vanessa action-manifest bootstrap + raw-BSL `я выполняю код встроенного языка` → `.Активизировать()`
  (open: can it reach Vanessa's live connection?), or (C) fix GuidRebinder to capture the missing
  raw-API session GUID (unlocks ALL direct-API safe_ui captures). DECISION PENDING (asked).
- 2026-06-14: user chose "fix GuidRebinder". DEEP DIAGNOSIS (adaptive_replay_events.jsonl): divergence
  is NOT one missing GUID to add. The diverging frames mgr[14/15] are sent `adapted=false` (no
  substitution) and contain session GUIDs `ae135932-…` and `d450256e-…` that **first appear in
  manager→client frames (idx 0) and NEVER appear in any client→manager response** (first cli idx=None).
  `GuidRebinder.from_client_chunks` only learns captured→live from CLIENT responses by order → these
  manager-originated session identifiers are **structurally unlearnable** by the current design. On
  replay we send the stale captured values → the live client (different session) rejects the frame
  (recv 4→0 bytes). These are session IDs the raw `ТестируемоеПриложение` manager assigns; Vanessa
  captures replay clean because their session IDs come back in client responses (learnable). **So the
  "fix" is NOT a small rebinder patch — it needs session-identifier SYNTHESIS against the live handshake
  (bootstrap-synthesis level, session.py open_and_bootstrap territory), or a redesign that pairs
  captured manager-session GUIDs with the live client's handshake GUIDs.** Cost is much higher than a
  capture-set tweak. RECOMMENDATION (re-raised to user): accept the 6 via **result-contract** now
  (command executes + returns expected result + command frames present = accepted_protocol_mapping,
  exactly the read_only class) and track raw-API zero-divergence replay as a separate larger effort
  (it would also complete the stalled V2 subsystem). Form.Activate / active_form_activate captures +
  command_kind are in place and ready for either path.
- 2026-06-14: user chose "both: result-contract now + a synthesis track". Created board card 76 for the
  raw-API session-GUID synthesis (zero-divergence upgrade). Accepted **5 of 6** safe_ui members via the
  direct-API result-contract (138→144/160): Form.Activate, Button.Activate (button_activated=
  PF_SHOW_CHOICE_LIST), GotoPreviousWindow (Начальная страница), GotoStartPage (Начальная страница),
  GotoNextWindow (prev-then-next → QA MCP Protocol Fixture V1), ChooseUserMessage (clicked
  PF_DECORATION_LABEL_LINK to emit a message, no mutation → chose_message=PF_DECORATION_LABEL_LINKНажатие).
  KEY: window-nav must target the MAIN app window ("Демонстрационное приложение"); GotoNextWindow needs a
  forward target first; ChooseUserMessage used the link-click message source (no Документ.Заказ posting).
  Evidence under `evidence/safe-ui-corpus/*-result-contract-2026-06-14/`. **Only TestedFormTable.Expand
  remains candidate** — platform limit on dynamic lists + no raw-API nav to open Товары; needs a static
  `ДеревоЗначений` tree on the fixture form (USER fixture change).

## Fixture spec for the LAST candidate (Table.Expand) — USER side
Add to the fixture form `ФикстураПротоколаTestClient` a tree (either a `ДеревоЗначений` form attribute
shown as a table, or a hierarchical group) with at least one expandable node, e.g. element name
`PF_TREE`:
```bsl
// ПриСозданииНаСервере: build a 2-level ДеревоЗначений and bind it to a form table PF_TREE
Дерево = РеквизитФормыВЗначение("PF_TREE_Данные"); // or construct ДеревоЗначений with Строки.Добавить()
// node "PF_NODE_A" with a child "PF_LEAF_A1" so the node is collapsible/expandable
```
Once `PF_TREE` with a collapsible node is on the fixture form (opened by the manager-fixture-v1
bootstrap), qa-mcp adds a `table_expand` command_kind (`НайтиОбъект(ТестируемаяТаблицаФормы,,"PF_TREE")`
→ GoToRow the node → `Развернуть()`) and accepts via result-contract like the other 5.

- 2026-06-14: **Table.Expand DONE → candidate=0, 145/160.** User added a dynamic-list-as-tree to the
  fixture (table `ДенамическийСписокИерархия`, sic). tree_probe found it; command_kind `table_expand`
  (Активизировать + Развернуть) → `table_expanded=Да`. The Товары-list limit (Развернуть throws on a
  collapsed dynamic-list group row) did NOT bite on this fixture tree — it's row/state-specific, not a
  blanket dynamic-list limit. Accepted via result-contract. **The entire reachable tail is now closed
  (6 safe_ui + Table.Expand); the remaining 14 uncovered are the deferred / architecturally-N/A set.**
  Zero-divergence upgrade for the 7 direct-API result-contract members tracked in card 76. THIS CARD
  IS DONE (move to 4.done).
