# 90. Fixture coverage for the uncaptured action types (checkbox / open_list / tables)

## Status
4.done

## Order Index
90

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-17: the genuine multi-action capture (card 86, `genuine-multiaction-20260617`) captured genuine DATE
  input + page-SWITCH, but **checkbox / open_list / table actions were NOT captured**:
  - no Vanessa step phrasing surfaced for a checkbox ("флажок" search returned 0);
  - the fixture `Обработка.ФикстураПротоколаTestClient` is a data PROCESSOR → no `e1cib/list/…` to open;
  - the tab-page field `PF_PAGE_B_FIELD` is not a plain text control → its input step failed
    («Неподходящий тип элемента управления для вызванного действия»);
  - table-row ops need the table-cell step variant, not yet exercised.
  Without a genuine capture of each, cards 86c (per-type SET: checkbox/choice), 86d (open_list), 86e (tables)
  cannot decode those command shapes.

## Summary
Give the protocol-research fixture genuine, drivable coverage for the still-uncaptured element/action types so
their native command frames can be captured and decoded — by EXTENDING the existing fixture or (preferred, the
current one is already overloaded with V1–V4 PF_* controls) adding a NEW, focused fixture processor.

## Acceptance
- A fixture (extended or new) exposes, with Vanessa-drivable steps, at minimum: a writable checkbox/flag, a
  catalog/list the manager can open (`e1cib/list/…`) or a navigation that yields a list-open command, and a
  table with add/edit/select-row.
- A genuine multi-action capture (the card-86 recipe: manager → tcpdump → run a `.feature` → pcap_to_traffic)
  records the checkbox SET, the open-list command, and the table-row command.
- The exact Vanessa step phrasings for each (checkbox, open list, table row) are documented (resolve the
  "no «флажок» step" gap — find the real checkbox step, or drive the checkbox via value/click).
- Decide & document: extend `Обработка.ФикстураПротоколаTestClient` vs a new `Обработка.Фикстура…V5` — keep
  element names stable (the `PF_*` convention) so the addressing decode (86a) keeps working.

## Notes / constraints
- Fixture development is 1C work via **edt-mcp** (memory edt-mcp-profile-and-deploy: EDT_MCP_TOOL_PROFILES=all),
  deployed into the `vanessa_client` infobase; do not use a standalone Configurator.
- Keep the `PF_*` naming + group structure conventions so `read_form_summary` introspection + element-path
  addressing remain valid.
- Page-field nuance: a field on a tab page may not be a plain text control — choose control types that the
  Vanessa input steps support, or document the right step per control type.

## Plan for the new session (start here)

Read `docs/protocol-research/capture-free-epic-state.md` first (the consolidated handoff). The fixture
ALREADY has checkboxes/pages/tables (V1–V4) — the four remaining types are blocked by DIFFERENT causes;
diagnose before rewriting the fixture:

1. **checkbox / choice** — likely a STEP-research gap, not a fixture gap. The fixture has `PF_CHECKBOX_*`; no
   Vanessa step matched "флажок". Boot the genuine manager and `search_for_steps_by_keywords` for «Булево» /
   «переключ» / «устанавливаю значение» / «выбираю из списка». If a toggle/choice step exists → capture +
   decode (boolean uses the `e0` value tag in reads) → productize (commit-partner). Maybe NO fixture change.
2. **tables** — also likely step-research. Vanessa table steps exist («в таблице "T" я нажимаю на кнопку
   "Добавить"», «в таблице "T" в поле с именем 'F' я ввожу текст …»). Capture a row add/edit → decode the
   table-cell addressing (`…TableBox[T].Column[C]` / row). Likely NO fixture change.
3. **page-field input** — `PF_PAGE_*_FIELD` is "not a plain text control" → **fixture change via edt-mcp**:
   add/convert a page field to a plain string ВводТекста so the cross-group write (86b) commits after a
   `switch_page`.
4. **open_list** — the fixture is a data PROCESSOR (no `e1cib/list/…`) → **fixture change OR scope change**:
   add a command/button that opens a catalog list, or capture against a real catalog in vanessa_client; then
   decode the open-list command (nav-link framing already decoded: `navigation.retarget_nav_link`).

For each: follow the decode→productize loop in the state doc (capture → diff → genuine SET + focus-change →
`derive_write_template`/`switch_page` → MCP tool + live verify). Keep `PF_*` naming + group structure so the
86a element addressing keeps working. Old fixture is overloaded — a new focused `…V5` processor is acceptable.

## Path B in progress (2026-06-17) — table-cell source fix staged; deploy needs infobase link

Chosen path: **B (extend the existing embedded fixture)**. Table-cell source fix MADE + verified (NOT yet
deployed → the live fixture is still read-only until deployed):
- File (NOT git-tracked; backed up as `Form.form.bak-card90`):
  `/opt/1c-dev/vanessa_qa/vanessa_client/src/DataProcessors/ФикстураПротоколаTestClient/Forms/Форма/Form.form`.
- Edits: removed the table's editing `<excludedCommands>` (Add/Change/Copy/Delete/EndEdit/Move*/Sort*) and the
  `<readOnly>true</readOnly>` on columns `PF_TABLE_TEXT` + `PF_TABLE_NUMBER` (kept `PF_TABLE_MARKER` read-only).
  XML re-validated well-formed; table data attribute was already `edit=common:true`.

**DEPLOY BLOCKER (next step):** the `vanessa_client` EDT project is NOT linked to an infobase
(`get_infobase_state`: `linked:false, deployAllowed:false, association.present:false`) and edt-mcp's infobase
registry (`/opt/ai-dev-suite-for-1c/edt-mcp/.runtime/custom-ibases.v8i`) is EMPTY. So a dev-apply needs first:
register the `/opt/1c-dev/vanessa_client` infobase in edt-mcp → associate/link the EDT project → then
`run_dev_infobase_apply` (config load + db update; check-only first). This is a consequential lab-infobase
change; the native replay client also needs the infobase FREE (Vanessa + apache down). Then: Vanessa capture of
a table-cell SET/row-add → decode (cell addressing `…TableBox/Table[T] … Column/EditField[C]` + row index) →
productize (mirror write_form_value/toggle). page-field + open_list follow on the same fixture (the dynamic
list `ДенамическийСписокИерархия` is already present for open_list).

## Change Set
- (staged, undeployed) Form.form: PF_TABLE_ITEMS made editable (table-cell fix), backed up `.bak-card90`.

## Related
- card 86 (capture-free action synthesis; `genuine-multiaction-20260617`), card 88 (element-type & interaction
  coverage), card 87 (general form introspection), evidence
  `docs/protocol-research/evidence/genuine-multiaction-capture-2026-06-17/`, memory
  genuine-action-capture-recipe; fixtures V1–V4 (board 4.done 01–04-2026-06-04).

## Progress (2026-06-17, step-research + checkbox decode)

Diagnosis done — **3 of 4 remaining types need NO fixture change** (the blocker was Vanessa step VOCABULARY,
not the fixture). Evidence: `docs/protocol-research/evidence/genuine-card90-checkbox-decode-2026-06-17/`.

- ✅ **checkbox / choice / table = step-gap, NOT fixture-gap.** The word is «флаг», not «флажок»
  (`флажок`→0 hits, `флаг`→18). Steps exist by NAME (fit `PF_*`): checkbox `Я устанавливаю/снимаю/изменяю
  флаг с именем '…'` (`UI.Формы.Поля.Флаги`); radio `Я меняю значение переключателя с именем '…' на '…'`
  (`UI.Формы.Поля.Переключатели`); table `в таблице "T" я добавляю строку` + `… в поле с именем 'F' я ввожу
  текст "V"`.
- ✅ **checkbox CAPTURED + COMMITTED live** (via Vanessa): `PF_CHECKBOX_FALSE`→Да, `PF_CHECKBOX_TRUE`→Нет;
  server marker `PF_MUTATION_CHECKBOX_MARKER` recorded both. Captures (gitignored):
  `runtime/protocol-research/captures/genuine-card90-20260617/{traffic,traffic-selfcontained}`.
- ✅ **checkbox commit law DECODED:** a checkbox commits by an ACTIVATE/TOGGLE frame on the `EditField`
  (`…EditField[NAME] … e0 4b 55`), **value-free** — the `e0 4b 55` marker is byte-identical for set and clear,
  no Истина/Ложь on the wire; the server toggles. New law, distinct from the value-SET types. `e0 4b 5x` is an
  activate-with-action tag family (`55`=toggle, `53`=choose-variant for radio). Structurally a twin of the
  86d page-switch.
- ✅ **checkbox PRODUCTIZED + LIVE-VERIFIED (capture-free, no Vanessa):** `derive_checkbox_toggle` /
  `toggle_checkbox` / `NativeWriteSession.toggle_checkbox` + **MCP tool `toggle_checkbox`** (qa-mcp now 12
  tools), mirroring the page-switch trio with `kind="EditField"`. Unit tests added (suite 210 passed). Live
  proof (`checkbox_toggle_probe.py`, fresh `launch_test_client`, 2 runs): toggling `PF_CHECKBOX_FALSE` then a
  RE-TARGETED `PF_CHECKBOX_TRUE` drives the server side-effect `PF_LAST_ACTION` to each checkbox's name ⇒ the
  toggle COMMITS. (Boolean reads back Cyrillic Да/Нет, so verified via the ASCII side-effect field.)

- ✅ **choice/radio PRODUCTIZED + LIVE-VERIFIED:** variant addressed by VALUE NAME (PF_CHOICE_A/B/C; index
  `'3'` rejected). Law: activate the `EditField` + carry the variant as a length-prefixed string
  (`…EditField[NAME] … e0 4b 53 <0x9a><len><variant>`) — re-target the variant via `build_write_frame`.
  `derive_choice_set` / `set_choice` / `NativeWriteSession.set_choice` + **MCP tool `set_choice`** (qa-mcp now
  **13 tools**), unit tests (suite 212 passed). Live proof (`choice_set_probe.py`, fresh client, 2 runs): set
  PF_CHOICE_C/PF_CHOICE_A → reads back the requested variant ⇒ commits, no Vanessa. Capture
  `genuine-card90-choice-20260617`. ⚠ native replay client needs `vanessa_client` FREE (Vanessa down).

Remaining (carry forward) — **all three now confirmed FIXTURE gaps → edt-mcp work:**
- **table-cell edit (86e):** CONFIRMED the fixture table `PF_TABLE_ITEMS` is **READ-ONLY** (2026-06-17 research).
  Cell input fails identically on existing AND new rows ("ВвестиТекст не может быть вызван"), even after
  «начинаю редактирование строки» (returns OK but cells stay read-only); «добавляю строку» returns OK but the
  row is NOT retained (count stays 3); `PF_MUTATION_SUPPORTED_TARGETS` excludes all table columns. ⇒ needs a
  **fixture change via edt-mcp**: make the table editable (ИзменятьСоставСтрок) + a column editable
  (ТолькоПросмотр=Нет), keep `PF_*` names, then capture→decode→productize the cell SET + row-add command.
- **page-field input** + **open_list:** genuine fixture/scope gaps (the fixture also exposes a dynamic list
  `ДенамическийСписокИерархия` — candidate for open_list without a new catalog).

⚠ DECISION (card flags it): extend `Обработка.ФикстураПротоколаTestClient` (already overloaded V1–V4) vs a new
focused `…V5` processor. All three remaining items need 1C metadata edits + an edt-mcp deploy into
`vanessa_client` (keep `PF_*` so 86a addressing stays valid). The native replay client needs the infobase FREE.

**edt-mcp constraint discovered (2026-06-17):** edt-mcp's structured create/edit facades cover
catalog/document/register/enum/etc. but **NOT data processors** (`edt_capabilities` families exclude it). It
CAN create/build **external** `.epf` processors (`create_external_data_processor` + form/module tools) but
NOT embedded config data processors. The existing fixture `ФикстураПротоколаTestClient` is an EMBEDDED config
DataProcessor (`vanessa_client/src/DataProcessors/…`, single form `Форма`, 346-line module) that ALREADY
contains the dynamic list `ДенамическийСписокИерархия` (open_list candidate) + the read-only table + pages.
⇒ two real paths: (A) **new external `.epf` V5** via edt-mcp (opened via the connect step's «Запускаемая
обработка» column), full form built from scratch; (B) **extend the existing embedded fixture** by hand-editing
its `Form.form` XML (make `PF_TABLE_ITEMS` editable + a page field plain) + `Module.bsl`, then deploy the
config — smaller, reuses the existing open step + the already-present dynamic list. (B) is now the lighter path
for open_list (list already present) and table-cell (one editable-table edit).

## Log
- 2026-06-17T00:00:00Z card created — record the checkbox/open_list/table capture gap surfaced by the genuine
  multi-action capture; return via fixture extension or a new focused fixture.
- 2026-06-17 step-research + checkbox decode: «флаг» resolves the checkbox/choice/table step gap (no fixture
  change); checkbox captured, committed live, and its value-free toggle commit law (`e0 4b 55`) decoded;
  productization specified (mirror `switch_page`, `kind="EditField"`) with a replayable capture ready. See
  Progress above + evidence `genuine-card90-checkbox-decode-2026-06-17/`.
- 2026-06-17 checkbox PRODUCTIZED + live-verified: `derive_checkbox_toggle`/`toggle_checkbox`/
  `NativeWriteSession.toggle_checkbox` + MCP tool (12 tools), unit tests (210 passed), capture-free toggle
  proven to commit on a fresh client via the PF_LAST_ACTION side-effect (base + re-targeted, 2 runs). Checkbox
  done; choice/table-cell/page-field/open_list carry forward.
- 2026-06-17 choice/radio PRODUCTIZED + live-verified: variant by value name; law = activate + length-prefixed
  variant string (`e0 4b 53`); `derive_choice_set`/`set_choice`/`NativeWriteSession.set_choice` + MCP tool (13
  tools), unit tests (212 passed), read-back proven on a fresh client (2 runs). Checkbox + choice done;
  table-cell/page-field/open_list carry forward.
- 2026-06-17 table-cell RESEARCH concluded: the fixture table `PF_TABLE_ITEMS` is READ-ONLY (cell input fails
  on existing+new rows even after «начинаю редактирование строки»; add-row not retained;
  PF_MUTATION_SUPPORTED_TARGETS excludes tables). ⇒ table-cell is a FIXTURE gap, not a step gap. All three
  remaining items (table-cell, page-field, open_list) now require edt-mcp fixture edits + deploy.
- 2026-06-17 decision: path B (extend the existing embedded fixture) — chosen after discovering edt-mcp can't
  create embedded data processors + the existing fixture already has the dynamic list. Table-cell SOURCE FIX
  staged (Form.form: table made editable, backed up) but NOT deployed: dev-apply is blocked because the EDT
  project isn't linked to an infobase + edt-mcp's IB registry is empty. Next: register+link the infobase, then
  run_dev_infobase_apply, then Vanessa capture→decode→productize. See "Path B in progress" above.
