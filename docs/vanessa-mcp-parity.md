# qa-mcp ↔ vanessa-mcp parity & Gherkin step library (card 98 #3)

qa-mcp drives 1C forms over the native TestClient protocol **capture-free, with NO Vanessa Automation runtime**.
This note maps the vanessa-mcp tool/step surface to qa-mcp coverage so an agent can author tests against qa-mcp
instead of Vanessa, and discover the supported step vocabulary.

## Discoverable step vocabulary

Call `search_for_steps(keywords="")` (the `search_for_steps`-equivalent) to list the supported Gherkin steps —
each entry has a canonical phrasing, an example, its native Step kind, a category and a description. The library
is derived from the transpiler's `STEP_PATTERNS`, so it exactly matches what `transpile` / `run_scenario`
execute (a no-drift unit test pins every example to its kind). Author a `.feature` from these phrasings;
`transpile` flags any unmapped lines (the transpiler never silently drops a step).

| category | step phrasing | native kind |
| --- | --- | --- |
| read | `Я читаю активное окно` | read_active_window |
| read | `Я получаю сводку формы` | read_form_summary |
| read | `Я читаю элемент 'Имя'` | read_element |
| read | `Я читаю значение поля 'Имя'` | read_form_value |
| read | `Значение поля 'Имя' содержит 'Текст'` | read_form_value (assert) |
| read | `И результат содержит 'Текст'` (modifier) | assert |
| navigation | `Я открываю список 'Справочник'` | open_list |
| navigation | `Я открываю карточку [кнопкой 'Имя']` | open_card |
| navigation | `Я перехожу к закладке с именем 'Имя'` | switch_page |
| action | `Я нажимаю на кнопку [с именем] 'Имя'` | click_button |
| action | `В поле [с именем] 'Имя' я ввожу текст 'Значение'` | input_text |
| action | `Я выбираю строку 'Значение' [как 'Новое']` | select_row |
| read | `Открылась форма с именем 'Имя'` | assert_form_open |
| read | `Открылось окно 'Заголовок'` | assert_window_open |
| read | `Элемент формы с именем 'Имя' присутствует на форме` · `Кнопка 'Имя' существует` | assert_element_present |
| read | `Элемент формы с именем 'Имя' стал равен 'Значение'` | read_form_value (equals) |
| read | `Я жду открытия окна 'Заголовок' в течение N секунд` | wait_window |
| read | `Таблица 'Имя' содержит строки:` + DataTable | assert_table_rows |
| read | `Каждый шаг выполняется быстрее N мс` (beyond Vanessa — per-step perf budget) | assert_step_perf |
| read | `В базе 'X' где "filter" количество записей <op> N` · `… записей нет` (beyond Vanessa — data-layer count) | assert_data_count |
| navigation | `Я открываю основную форму документа/обработки/отчёта/списка справочника 'Имя'` | open_main_form |
| navigation | `Я закрываю текущее окно` · `Я закрываю окно 'Заголовок'` | close_window |
| navigation | `Я закрываю все окна клиентского приложения` | close_all_windows |
| navigation | `Я подключаю профиль TestClient 'Имя'` · `… клиент тестирования с параметрами:` | connect_client |
| action | `В таблице 'Имя' я выбираю текущую строку` · `… я перехожу к строке[:]` | select_row |
| action | `Я выполняю сценарий 'Имя'` | run_subscenario |
| skipped | `Я устанавливаю флаг настройки Vanessa Automation 'Имя'` | skip_step (recognized no-op) |

`search_for_steps` (the live library, derived from `STEP_PATTERNS`) is the authoritative, no-drift list; the
table above is a curated digest. **BDD mechanics (card 103 Wave 2):** `@tags` (feature-level inherited) with
`filter_by_tags` include/exclude · `Предыстория:`/`Background:` (prepended to each scenario) · step `DataTables`
(`| … |` attached as `params["table"]`) · `Структура сценария:`/`Scenario Outline:` + `Примеры:`/`Examples:`
(expanded per data row with `<col>` substitution, in cells too) · nested scenarios (`run_subscenario`).

Beyond the Gherkin runner, qa-mcp exposes 55 native MCP tools for finer control (the full action surface:
`set_table_cell` / `set_reference_field` / `answer_dialog` / `choose_from_{list,menu}` / `run_report` /
`read_spreadsheet_cell` / `assert_form_value` / `wait_for_form_value` / `read_form_descriptor` / the table-row
ops / window ops / `write_form_value_xtest` / `send_keys`, …) plus the state/results/infobase/window surface
(`get_state` / `get_test_results` / `write_test_report` / `infobase_info` / `get_window_list` /
`get_window_list_testclient`; card 98 #2 + card 104 reporting). The Gherkin library is the high-level authoring
surface; the MCP tools are the programmatic one.

## Step-library breadth & corpus coverage (card 103, E-FW)

Drop-in for EXISTING Vanessa feature suites depends on transpile breadth. Measured against the real lab corpus
(`/opt/1c-dev/demo10413/tests/vanessa` contracts + `${QA_MCP_PRIVATE_CORPUS_ROOT}/tests/vanessa` smokes) with
`tools/protocol-research/corpus_transpile_coverage.py`:

- **11.9% → 97.8%** transpile coverage after Wave 1 (vocabulary) + Wave 2 (BDD mechanics). 9 of 11 corpus
  features transpile 100% (4 demo10413 contracts + 6 private third-party smokes + the in-repo sample).
- **Gate:** `tests/test_corpus_gate.py` — a hermetic in-repo gate (`tools/protocol-research/qa-vanessa-canonical-corpus.feature`
  must transpile 0-unmapped) + an optional lab-corpus gate (≥95%, skipped when `/opt/1c-dev` is absent and
  fail-loud when either the four-file public group or six-file private group is incomplete). The CLI
  `corpus_transpile_coverage.py --min 0.95` exits non-zero below threshold for CI.

**Corpus = 100% (card 109 closed the last residual).** The one previously-unmapped mechanism — `Я открываю
внешнюю обработку или отчет '…​.epf' (Расширение)` (open an EXTERNAL data processor/report inside the running
client) — is now covered. There is no `e1cib`/URL link for an external file (the platform opens it via
`ВнешниеОбработкиМенеджер.Подключить(path)`, which Vanessa drives through its **VanessaExt** component, gated on
«ИспользоватьКомпонентуVanessaExt»). qa-mcp does it the **Vanessa-component-free, 1C-native way**: the
`open_external_processor` tool drives «Главное меню → Файл → Открыть» → the GTK file chooser → Ctrl+L → a
Unicode-safe path → Enter (xtest, the card-100 class). LIVE-verified opening the fixture `.epf` (the «QA MCP
Protocol Fixture V1» form). The Gherkin step «Я открываю внешнюю обработку или отчет '<path>' (Расширение)» maps
to it, so the lab + in-repo corpora transpile **100%** (gate `LAB_MIN=1.0`). Card 109 (`4.done`); evidence
`evidence/card109-open-epf-live-2026-06-21/` + research `evidence/card103-external-epf-research-2026-06-21/`.

**Execution note:** the above is the AUTHORING / transpile layer (what `transpile` / the step library accept).
EXECUTION of the new step kinds through the scenario runner (card 103 Wave 3) is wired OFFLINE as of 2026-06-21:
the runner executes the assert family (assert_form_open / assert_window_open / wait_window / assert_element_present
/ assert_table_rows) over a single cached live read, `expect_equals` strict-equality, `assert_data` (data-layer,
no TestClient needed), `skip_step` (no-op) and `run_subscenario` (callee runs on the same bootstrapped handle).
The remaining new ACTION kinds (open_main_form / close_window / close_all_windows / connect_client) route to the
runner's `action_resolver` like the original action steps; synthesizing their live command frames + an on-lab
read+assert verify is the LAB-gated remainder of Wave 3.

## Beyond Vanessa — data-layer cross-verification (card 105, E-XV)

Vanessa Automation asserts only through the UI. qa-mcp adds a capability Vanessa does not have: assert what a UI
action DID against the DATA LAYER, in the same scenario. A self-contained read-only OData client
(`qa_mcp.data.ODataClient`) backs the MCP tool `assert_data(entity_set, field, expected, filter|key,
match=equals|contains|regex)` and the Gherkin step «В базе 'EntitySet' где "<OData-filter>" поле 'Поле' равно
'Значение'». Combined with a UI write (`write_form_value_xtest` → save), this is a full UI→DB roundtrip check
(`Записать` → confirm the value persisted). Read-only; connection via `QA_MCP_ODATA_URL`/`USER`/`PASSWORD`
(the lab's standard OData, published via Apache). This is the first of the E-XV "native superset" capabilities
(epic 102).

**Metadata-driven test generation (card 106, E-XV).** `generate_smoke_suite(objects)` turns a metadata listing
(from meta-mcp `metadata_list`, kinds Справочник/Документ/Обработка/Отчёт) into a runnable smoke `.feature` —
"does every form still open + render?" — using only canonical steps (transpiles 100%), plus per-object
`open_links` for `read_form_descriptor` and a `smoke_coverage` roll-up. Vanessa requires hand-authored features;
qa-mcp auto-generates the regression suite from the config.

## vanessa-mcp tool → qa-mcp coverage

✅ covered · 〜 partial / different model · ❌ out of scope (not a capture-free protocol concern)

| vanessa-mcp | qa-mcp | notes |
| --- | --- | --- |
| `get_form_analysis` | ✅ `read_form_descriptor` | full element name→value descriptor + Gherkin state; card 98 #1 |
| `search_for_steps_by_keywords` | ✅ `search_for_steps` | this card (98 #3) |
| `frequently_used_steps` | 〜 `search_for_steps` | the same library; no usage-frequency ranking |
| `run_scenario` | ✅ `run_scenario` | runs a `.feature` / scenario JSON natively |
| `execute_feature_step` / `execute_step_from_text` | ✅ `run_step` | single step |
| `load_features` / `open_feature_file` | ✅ `run_scenario(feature=…)` / `transpile` | feature input + transpile preview |
| `capture_screenshot_with_fallback` / `get_window_screenshot_os` | ✅ `capture_screenshot` | OS screenshot of the client display |
| `activate_window` | ✅ `activate_window` | + `close_window` |
| (keyboard steps — Enter/Esc/Tab/arrows) | ✅ `send_keys` | raw OS keys via XTEST (1C keyboard is OS-level — no protocol frame; card 96 change 4). High-level intents prefer `answer_dialog` / `select_table_row` / `click_command` |
| `connect_test_client` / `ensure_test_client_profile` | 〜 `launch_test_client` / `test_client_status` | qa-mcp launches+owns the client (card 84/85) |
| `get_active_window_data` / `ui_read_tree` | ✅ `read_form_descriptor` | the full element tree (every `<Kind>[name]` — EditField/Button/Table/Group/…) via the live descriptor; `open_link` introspects ANY form by nav-link (card 98 change-1) |
| `infobase_info` | ✅ `infobase_info` | infobase/connection metadata from the `.ai1c` profile (password-redacted) + live listening; card 98 #2 |
| `get_test_results` | ✅ `get_test_results` | aggregates the scenarios run this server session (pass/fail/step counts); card 98 #2 |
| `get_VanessaAutomation_state` / `get_editor_state` | ✅ `get_state` | the capture-free `get_state`-equiv: connection + run-session + infobase identity; card 98 #2 |
| `get_window_list_os` | ✅ `get_window_list` | OS top-level windows on the client display via xdotool (id/title/geometry); card 98 #2. NB: 1C opens forms as MDI tabs inside ONE X window, so this lists the app window, not the open forms |
| `get_window_list_testclient` | ✅ `get_window_list_testclient` | the 1C-internal window/tab list (caption + frame kind SecondaryFrame/MainFrame/HomePage) — the genuine query replayed by splicing onto a live value-read header; card 98 #2 (evidence card98-windowlist-decode-2026-06-20) |
| `get_info_about_line_scenario` | ❌ | Vanessa-runtime scenario-line internals — N/A capture-free |
| `manage_breakpoints` / `manage_variables` | ❌ | debugger control — out of scope |
| `get_data_from_knowledge_base` | ❌ | Vanessa KB — out of scope |
| `run_role_scenario_matrix` / `ensure_infobase_user_with_roles` | ❌ | role/admin orchestration — out of scope |

## Authoring a Vanessa-style feature against qa-mcp

A Vanessa-canonical `.feature` runs against qa-mcp via `run_scenario` after `transpile` confirms coverage. The
phrasings above are Vanessa-canonical (`я нажимаю на кнопку с именем …`, `в поле с именем … я ввожу текст …`,
`я перехожу к закладке с именем …`), so most existing features transpile unchanged. Documented adaptations:

- Steps qa-mcp does not yet map appear in `transpile`'s `unmapped` list (never silently dropped) — pick a
  supported phrasing from `search_for_steps` or drop to the MCP action tools.
- Element/field/button identifiers are addressed BY NAME (the captured leaf), matching Vanessa's `с именем 'X'`.
- A read assertion is `Значение поля 'X' содержит 'V'` or a read step followed by `И результат содержит 'V'`.

Sample: `tools/protocol-research/qa-vanessa-style.feature` (transpiles 100% — exercised by the step-library tests
and runnable live with `run_scenario`).
