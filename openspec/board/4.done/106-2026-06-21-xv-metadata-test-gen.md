# 106. E-XV — metadata-driven test generation (smoke suites from the config)

## Status
4.done

## Order Index
106

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-21 project review: Vanessa requires hand-authored features. qa-mcp can ENUMERATE a config from
  metadata and auto-generate tests — a "beyond Vanessa" capability. Substrate ready: `meta-mcp`
  (`metadata_list` / `metadata_get` / `metadata_search`) + the capture-free `read_form_descriptor(open_link=…)`
  that opens + introspects ANY form on ANY config with no per-form capture.
- Parent epic: card 102. Capability: a new generator layer over `qa-mcp-protocol-lab` + `meta-mcp`.

## Summary
Generate runnable smoke/regression scenarios from metadata: enumerate forms/objects (lists, default forms),
build their `open_link`s, and emit a scenario set that opens each form and asserts it renders (descriptor
non-empty + expected key elements). Report coverage (forms touched / total). Look-ahead: autofill required
attributes from metadata to smoke create-forms. Turns "does this config still open everywhere?" into a one-command
regression Vanessa cannot author automatically.

## Acceptance
- Given a config, the generator emits a runnable scenario set covering N forms (list + object forms) with an
  "opens + renders" assertion per form, via `read_form_descriptor(open_link=…)`.
- A live run on a real config (e.g. demo БСП) executes the generated suite and reports form coverage
  (covered / total) + any forms that failed to open.
- Offline unit tests cover the metadata→`open_link`→scenario generation shape.

## Change Set (waves — living plan, lightweight: card-as-plan, no full OpenSpec ff)
1. ✅ `metadata-form-enumerate` — DONE 2026-06-21. `smoke.open_link_for(kind, name)` builds nav-links
   (Справочник/Документ → `e1cib/list/…`; Обработка/Отчёт → `e1cib/command/…`; kind ru/en). The live listing
   source is `meta-mcp metadata_list` (passed in as `objects`), so the generator is pure/offline-testable.
2. ✅ `smoke-scenario-generator` — DONE 2026-06-21. `generate_smoke_scenarios` / `generate_smoke_feature` emit a
   runnable `.feature` (open the main form + read its summary) using ONLY canonical card-103 steps → transpiles
   100% (self-consistency test). MCP tool `generate_smoke_suite(objects, feature_name, out_path)` (#55) returns
   the feature + `open_links` + counts.
3. ✅ `coverage-report` — DONE 2026-06-21. `smoke_coverage(objects, opened)` → {total, supported, covered,
   missing, unsupported}.
4. ✅ `create-form open + required-field-autofill` — DONE (LIVE) 2026-06-21.
   - **Open (live):** a NEW-object create form opens via `e1cib/data/<Тип>.<Имя>` (no `?ref=`) — ground-truth
     probe + `run_scenario` 3/3: Заказ→«Заказ (создание)», Валюты→«Валюта (создание)», Оплата→«Оплата товаров и
     услуг (создание)». New Gherkin step «я создаю новый документ / элемент справочника 'X'» → kind
     `open_create_form` → `_CREATE_FORM_PREFIX` → `navigate_resolver`. Evidence
     `evidence/card106-broaden-live-2026-06-21/`.
   - **Autofill (live):** `src/qa_mcp/scenario/autofill.py` — `required_fields_from_mdo` (EDT `.mdo`:
     `fillChecking=ShowError`; Owner/Parent gated on owners/hierarchy), `smoke_value_for_type` (String/Number/
     Date/Boolean; references → unfillable), `build_autofill_plan` + `create_fill_feature`; MCP
     `autofill_required_fields` (#56). LIVE end-to-end: Валюты.mdo → required field Наименование(String)→"QASMOKE"
     → `write_form_value_xtest` (saved) → `assert_data` Catalog_Валюты Description eq 'QASMOKE' → ok, record_count=1.
     411 tests. Evidence `evidence/card106-autofill-live-2026-06-21/`. Gap (documented): reference-typed required
     fields aren't auto-valued (need an existing ref); config-agnostic live write of arbitrary fields is a further
     capability (this demo's live write uses the Валюты xtest capture path).
5. ✅ (LIVE) drive end-to-end — DONE 2026-06-21 (boot session). On the live `vanessa_client` (БСП demo): object
   inventory from the real config's OData service doc → `generate_smoke_scenarios` → opened each form
   config-agnostically by nav-link via `read_form_descriptor(open_link, enumerate_live=True)` → **8/8 catalog
   forms opened + rendered** (genuine captions «Регионы РФ»/«Товары»/… , 44–67 elements each). Coverage signal =
   `element_count` (list forms have 0 EditFields — content is a dynlist Table). Evidence:
   `evidence/card106-smoke-live-2026-06-21/`.
6. ✅ (LIVE) broaden the object set beyond catalogs — DONE 2026-06-21. Via `run_scenario` + the card-103
   `navigate_resolver` on `vanessa_client`: **12/12 opened** — Документы 6/6 (`e1cib/list/Документ.`), Отчёты 3/3
   + Обработки 3/3 (`e1cib/app/<Тип>.`). **Research finding (the link-format fix):** reports/processors open via
   `e1cib/app/…`, NOT `e1cib/command/…` (which returned the bare main window) — a ground-truth window-list probe
   confirmed it; `smoke._KINDS` + `mcp_server._OPEN_MAIN_FORM_PREFIX` corrected accordingly (offline tests
   updated). Object-specific exception: `Обработка.ЖурналРегистрации` is a platform-special (registration-log),
   not a normal openable form. Evidence: `evidence/card106-broaden-live-2026-06-21/`.

## Verify
- Offline — `pytest` **411 green** (`tests/test_smoke_gen.py` open_link mapping incl. e1cib/app for reports/procs;
  `tests/test_autofill.py` required-field detection + value synthesis + plan + create-fill feature transpiles;
  gherkin `open_create_form` mapping; `autofill_required_fields` MCP tool). 56 MCP tools; server imports clean.
- LIVE (boot session) — generated smoke run on the real `vanessa_client`: **8/8 catalog forms opened + rendered**
  via `read_form_descriptor(open_link, enumerate_live=True)`. Evidence `evidence/card106-smoke-live-2026-06-21/`.
- LIVE (broadening) — via `run_scenario` + `navigate_resolver`: **12/12 opened** across the new types (Документы
  6/6 `e1cib/list/Документ.`; Отчёты 3/3 + Обработки 3/3 `e1cib/app/<Тип>.`); report/processor link format
  corrected `e1cib/command/…` → `e1cib/app/…`. Evidence `evidence/card106-broaden-live-2026-06-21/`.
- LIVE (create form) — `open_create_form` via `run_scenario`: **3/3** opened («Заказ (создание)» / «Валюта
  (создание)» / «Оплата … (создание)»); link `e1cib/data/<Тип>.<Имя>`. Evidence (createform-probe/verify).
- LIVE (autofill) — metadata → required field Наименование(String)→"QASMOKE" → `write_form_value_xtest` (saved) →
  `assert_data` Catalog_Валюты Description eq 'QASMOKE' → ok, record_count=1. Evidence
  `evidence/card106-autofill-live-2026-06-21/`.

## Archive
- card complete (offline + LIVE: smoke gen, broadening, create form, autofill); kept as the living record
  (lightweight card-as-plan, no OpenSpec ff). Documented gap: reference-typed required fields aren't auto-valued.

## Result
Metadata-driven test generation COMPLETE — offline + LIVE across all object types: `smoke.py` (generator +
`generate_smoke_suite` #55 + coverage) and `autofill.py` (required-field detection + value synthesis + create-fill
plan + `autofill_required_fields` #56), unit-tested (411). LIVE on `vanessa_client`: catalogs 8/8, broadening
12/12 (Документ `e1cib/list/`; Отчёт/Обработка `e1cib/app/`), create forms 3/3 (`e1cib/data/`), and the
metadata→autofill→write→save→assert-in-DB loop. A regression generator Vanessa cannot author automatically.
**Follow-on done 2026-06-21: reference autofill** — `autofill.reference_entity_set` + `resolve_reference_value`
resolve CatalogRef./DocumentRef. required fields to an EXISTING value via OData, so the plan covers DOCUMENTS
(Заказ 1/7→6/7, ПоступлениеДенег 2/7→7/7 fillable; live). `autofill_required_fields` gained `resolve_references`.
Remaining gap: EnumRef (enums aren't OData sets) + config-agnostic live WRITE of arbitrary fields. Card → 4.done.

## Next
- closed. Follow-ons (separate cards): auto-value reference required fields (pick an existing ref via OData);
  config-agnostic live write of an arbitrary field on any create form (foreground + xtest into a located field).

## Related
- Parent: card 102. Substrate: `meta-mcp` (`metadata_list`/`metadata_get`), `read_form_descriptor(open_link=…)`
  (config-agnostic open, proven on demo БСП — card 98). Code: `src/qa_mcp/mcp_server.py`,
  `src/qa_mcp/scenario/`.
- Memory: [[surpass-vanessa-native-superset-goal]], [[qa-mcp-capture-free-epic]].

## Log
- 2026-06-21 card created (E-XV track — substrate ready). Thin backlog stub; change set outlined, not yet
  ff-processed.
- 2026-06-21 LIVE end-to-end (boot session): real-config object inventory → generate_smoke_scenarios → opened
  each form by nav-link via read_form_descriptor(open_link, enumerate_live=True) on the live vanessa_client →
  **8/8 catalog forms opened+rendered** (genuine captions, 44–67 elements). Coverage signal = element_count (not
  field_count — list forms have 0 EditFields). Evidence `evidence/card106-smoke-live-2026-06-21/`. Change 5 DONE.
- 2026-06-21 DONE (offline) in-session, lightweight card-as-plan: `src/qa_mcp/scenario/smoke.py`
  (`open_link_for` / `generate_smoke_scenarios` / `generate_smoke_feature` / `smoke_coverage`) + MCP
  `generate_smoke_suite` (#55); `tests/test_smoke_gen.py` (4, incl. generated feature transpiles 100%). 373 tests
  green. Card → 3.inprogress; only the live end-to-end run on a real config remains (change 5).
- 2026-06-21 BROADENING (change 6) LIVE: extended the open beyond catalogs via `run_scenario` + the card-103
  `navigate_resolver` → **12/12** (Документы 6/6 `e1cib/list/`; Отчёты 3/3 + Обработки 3/3 `e1cib/app/`). A
  ground-truth window-list probe found reports/processors open via `e1cib/app/…`, NOT `e1cib/command/…` (the old
  mapping returned the bare main window); fixed `smoke._KINDS` + `mcp_server._OPEN_MAIN_FORM_PREFIX` + offline
  tests (404 green). `Обработка.ЖурналРегистрации` is a platform-special non-opener. Evidence
  `evidence/card106-broaden-live-2026-06-21/`.
- 2026-06-21 CREATE-FORM open (change 4, open side) LIVE: a NEW-object create form opens via
  `e1cib/data/<Тип>.<Имя>` (no `?ref=`) — ground-truth probe + `run_scenario` 3/3 («Заказ (создание)» / «Валюта
  (создание)» / «Оплата … (создание)»). New Gherkin «я создаю новый документ / элемент справочника 'X'» → kind
  `open_create_form` → `_CREATE_FORM_PREFIX` → `navigate_resolver`; +1 gherkin test, nav-link tests. 405 green.
  Remaining (change 4): required-field autofill (the write side).
- 2026-06-21 AUTOFILL (change 4, write side) LIVE → card CLOSED to 4.done. `src/qa_mcp/scenario/autofill.py`
  (required_fields_from_mdo [fillChecking=ShowError; Owner/Parent gated on owners/hierarchy], smoke_value_for_type,
  build_autofill_plan, create_fill_feature) + MCP `autofill_required_fields` (#56) + `tests/test_autofill.py`.
  411 green. LIVE end-to-end: Валюты.mdo → required Наименование(String)→"QASMOKE" → write_form_value_xtest (saved)
  → assert_data Catalog_Валюты Description eq 'QASMOKE' → ok, record_count=1. Evidence
  `evidence/card106-autofill-live-2026-06-21/`. All changes (1-6 + 4) ✅; card → 4.done. Gap: ref-typed required
  fields not auto-valued; config-agnostic live write of arbitrary fields = follow-on cards.
- 2026-06-21 FOLLOW-ON: reference autofill. `autofill.reference_entity_set` (CatalogRef./DocumentRef. → Catalog_/
  Document_ OData set) + `resolve_reference_value` (first record's Description/Number/Code) + `build_autofill_plan`
  `odata_client=` + `autofill_required_fields` `resolve_references`. Documents now autofill: LIVE vs vanessa_client
  OData — Заказ 1/7→6/7 (Покупатель→«Поставщики»/Валюта→«EUR»/…), ПоступлениеДенег 2/7→7/7. +4 tests → 416 green.
  Evidence `evidence/card106-ref-autofill-live-2026-06-21/`.
- 2026-06-21 FOLLOW-ON (EnumRef autofill): `enum_values_from_mdo` + `resolve_enum_value(type, enum_mdo_provider)`
  resolve a required EnumRef to the first enum value (synonym) from the enum's `.mdo`; `build_autofill_plan`
  `enum_mdo_provider=` + `autofill_required_fields` `enum_src_root=`. LIVE: Документ.Заказ now **7/7** fillable
  (СостояниеЗаказа → «Открыт»). +3 tests → 419 green. Remaining gap: config-agnostic live WRITE of arbitrary fields.
- 2026-06-21 FOLLOW-ON (config-agnostic live arbitrary-field write — last autofill gap): MCP tool
  `write_form_fields_by_label(open_link, labels, values, display)` — foreground the form (`_foreground_form_by_link`),
  then per field: `locate_text("<label>:")` (colon disambiguates substring labels) → click `input_offset`px right
  (into the input) → `xtest_type_unicode` → Tab. New primitive already shared with card 109. LIVE on the Валюты
  create form: single-field probe (Наименование=QAARBWRITE) + the shipped tool writing TWO fields
  (Наименование=QATOOLWRITE, Наименование основной валюты=USD) — both landed (screenshot). No per-field capture
  (generalizes write_form_value_xtest). 58 tools. Evidence `evidence/card106-arbwrite-live-2026-06-21/`. Both
  minor autofill gaps (EnumRef + arbitrary-field write) now CLOSED.
