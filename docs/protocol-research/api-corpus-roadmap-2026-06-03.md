# API Corpus Roadmap

Дата среза: 2026-06-03.
Дата актуализации инфраструктурных MCP: 2026-06-03.

Этот документ фиксирует предложенный переход от ручной расшифровки отдельных
кадров к конвейеру protocol reverse engineering для конечной поверхности
объектов автоматизированного тестирования 1C.

## Статус Инфраструктурных MCP

На момент актуализации выполнены все три подготовительные карточки,
которые были заведены для перехода к активной разработке 1C-фикстур и
manager-harness:

- `edt-mcp`: карточка
  `openspec/board/4.done/2026-06-03T13-30-00Z-support-multi-project-infobase-targets.md`
  завершена и опубликована коммитом
  `feat(edt-mcp): support multi-project infobase targets`;
- `meta-mcp`: карточка
  `openspec/board/4.done/2026-06-03T13-31-00Z-support-multi-source-metadata-contexts.md`
  завершена и опубликована коммитом
  `feat(mcp): add metadata source contexts`;
- `live-mcp`: карточка
  `openspec/board/4.done/2026-06-03T13-32-00Z-add-windows-com-multi-connection-provider.md`
  завершена и опубликована коммитом
  `feat(live): add connection management tools`.

Фактически это меняет стартовую точку roadmap: подготовку клиентской формы,
manager-обработки, metadata evidence и live read-only проверки теперь нужно
строить не через ручное переключение MCP-серверов, а через явные контексты
`target_id`, `source_id` и `connection_id`.

### Что Готово В edt-mcp

`edt-mcp` теперь закрывает управляемую работу с двумя EDT-проектами в одном
workspace:

- добавлена модель workspace-local target context для стабильной привязки
  `target_id -> workspace/project/infobase/role`;
- добавлены публичные инструменты `list_target_contexts` и
  `register_workspace_target`;
- добавлен UI-free операторский workflow
  `connect_existing_infobase_workspace`, который создает или переиспользует
  EDT workspace, делает существующую ИБ видимой для `1cedtcli`, импортирует
  проект и опционально регистрирует target context;
- добавлены target-bound wrappers:
  `validate_project_infobase_binding`, `retrieve_target_from_infobase`,
  `apply_target_db_update`, `prepare_target_hot_deploy`;
- multi-project операции теперь должны fail-closed при неоднозначном выборе
  проекта/ИБ или при несовпадении binding;
- evidence от операций содержит выбранный `target_id`, project, infobase и
  binding summary без раскрытия секретов.

Важное ограничение: `EDT_MCP_INFOBASE_REGISTRY_PATH` остается внутренним
селектором edt-mcp и не подменяет реальный каталог ИБ для `1cedtcli`.
Импорт через `1cedtcli infobase-import -n` требует, чтобы база была видима в
реальном EDT/1C user infobase catalog, пока не доказан поддерживаемый EDT
override.

Практический вывод для qa-mcp:

- целевой workspace можно держать одним, например
  `C:\1C_BASES\EDT\vanessa_protocol_lab`;
- внутри него должны быть два проекта, например `vanessa_client` и
  `vanessa_manager`;
- дальнейшие EDT-операции в наших сценариях должны явно указывать
  `target_id=client` или `target_id=manager`.

### Что Готово В meta-mcp

`meta-mcp` теперь закрывает одновременную работу с metadata двух конфигураций:

- добавлен контракт `METADATA_MCP_1C_METADATA_SOURCES`;
- добавлена session source registry, где внешний `source_id` (`qa_client`,
  `qa_manager`) резолвится в существующий runtime scope
  `configuration_id` / `build_id` / route;
- добавлена компактная операция `metadata_sources` для list/register/status и
  explicit compare сценариев;
- source-aware routing распространен на metadata/code/search/reference/graph
  чтение;
- при нескольких зарегистрированных sources обычные чтения без `source_id`
  fail-closed, кроме доказанно однозначных single-source случаев;
- evidence для qa-mcp теперь source-qualified: metadata objects, modules,
  routines, search results, references, call graph и feature-context payloads
  несут `source_id` или однозначный source envelope;
- добавлен явный cross-source comparison режим
  `metadata_sources(operation="compare")`.

Важное ограничение: первый слой не мигрирует Postgres serving schema на
physical `source_id` в каждом primary key. Внешний `source_id` применяется как
runtime/evidence context поверх существующих `configuration_id` и `build_id`.
Физическая миграция storage остается отдельной будущей задачей, только если
она реально потребуется.

Практический вывод для qa-mcp:

- metadata-контекст клиентской базы должен регистрироваться как
  `source_id=qa_client`;
- metadata-контекст manager базы должен регистрироваться как
  `source_id=qa_manager`;
- все corpus/evidence записи должны хранить пары вида
  `{source_id, object_id}`, `{source_id, module_id}`, `{source_id, routine_id}`,
  а не голые identifiers.

### Что Готово В live-mcp

`live-mcp` теперь закрывает Windows-local live-доступ к двум file infobases
через COM без публикации базы:

- базовый COM provider уже существовал: explicit provider selection,
  Windows-only supervised COM worker subprocess, COM-backed
  `validate_1c_query`, `execute_1c_query` и compatible resource tools;
- третья карточка добавила connection-management MCP surface:
  `list_live_connections`, `check_com_connection`,
  `get_com_connection_info`;
- один live-mcp server может держать registry подключений, например
  `connection_id=client` для `C:\1C_BASES\vanessa_client` и
  `connection_id=manager` для `C:\1C_BASES\vanessa_manager`;
- рекомендуемый qa-mcp режим - не задавать
  `LIVE_MCP_FOR_1C_DEFAULT_CONNECTION_ID`, чтобы любые runtime calls без
  `connection_id` fail-closed, а не выбирали первую базу неявно;
- connection diagnostics secret-safe: они показывают ids, provider kind,
  наличие/валидность настроек, timeout, COM prog id и категории ошибок, но не
  печатают raw infobase path, username, password или full connection string;
- COM check открывает и закрывает bounded external connection через worker и
  не возвращает строки live-данных;
- canonical read-only data tools остаются `execute_1c_query`,
  `validate_1c_query` и resource/query tools с явным `connection_id`;
- произвольное выполнение BSL, mutating tools и COM DCS не входят в этот слой.

Практический вывод для qa-mcp:

- live runtime-контекст клиентской базы должен использовать
  `connection_id=client`;
- live runtime-контекст manager базы должен использовать
  `connection_id=manager`;
- публикация базы, HTTP-сервис, OData и HTTP-расширение для локальной Windows
  лаборатории не требуются;
- до старта corpus run нужно выполнить `list_live_connections` и
  `check_com_connection` для обоих ids и сохранить secret-safe результат как
  run preflight evidence.

Проверка результата на стороне документации:

- done-карточка `live-mcp` подтверждает архивированный change
  `add-live-connection-management-tools`;
- актуальная спецификация `live-connection-management-tools` фиксирует
  перечисленные инструменты и no-default fail-closed поведение;
- targeted check в `live-mcp` прошел:
  `uv run pytest -q tests/test_connection_management.py tests/test_mcp_tools.py tests/test_config.py`
  -> 35 passed;
- import check прошел:
  `uv run python -c "import live_mcp_for_1c.mcp_server; import finshtab_1c_live.mcp_server"`
  -> imports ok.

## Исходная Гипотеза

Поверхность, которую должен заменить Python TestManager, конечна. В справке 1C
есть разделы `Автоматизированное тестирование` и `Агент клиентского приложения`
с ограниченным набором объектов, свойств, методов и конструкторов. Это
позволяет строить не бесконечное исследование трафика, а управляемую API
matrix:

- объект языка 1C;
- свойство, метод или конструктор;
- тип операции: read, write, action, constructor;
- параметры;
- ожидаемый результат или исключение;
- состояние UI до и после операции;
- соответствующие request/response frames в TestManager/TestClient protocol.

Проверка через `help-mcp` для платформы `8.3.27.1786` подтвердила наличие
ключевых объектов:

- `ТестируемоеПриложение` (`TestedApplication`);
- `ТестируемоеОкноКлиентскогоПриложения`
  (`TestedClientApplicationWindow`);
- `ТестируемаяФорма` (`TestedForm`);
- `ТестируемаяГруппаФормы` (`TestedFormGroup`);
- `ТестируемаяДекорацияФормы` (`TestedFormDecoration`);
- `ТестируемаяКнопкаФормы` (`TestedFormButton`);
- `ТестируемаяТаблицаФормы` (`TestedFormTable`);
- `ТестируемоеПолеФормы` (`TestedFormField`);
- `ТестируемыйКомандныйИнтерфейсОкна`
  (`TestedWindowCommandInterface`);
- `ТестируемаяГруппаКомандногоИнтерфейса`
  (`TestedCommandInterfaceGroup`);
- `ТестируемаяКнопкаКомандногоИнтерфейса`
  (`TestedCommandInterfaceButton`);
- `ТестируемоеДополнениеЭлементаФормы`
  (`TestedFormItemAddition`) и расширения по видам элементов;
- `МенеджерАгентаКлиентскогоПриложения`
  (`ClientApplicationAgentManager`).

Дополнительные enum и extension-типы должны входить в inventory как
семантические зависимости, но не должны раздувать первый replay scope.

## Вывод Из Исследования PRE

Наш текущий подход уже совпадает с классической практикой protocol reverse
engineering: capture, message splitting, clustering, dynamic-field
normalization, replay и active probing. Но масштаб нужно менять.

Полезные ориентиры:

- Netzob описывает процесс как импорт/capture сообщений, inference vocabulary
  and grammar, simulation и active experiments against real implementations:
  https://netzob.org/overview
- Discoverer строит message formats из traces через tokenization, initial and
  recursive clustering, поиск length/cookie/format-distinguisher fields и
  merge похожих форматов:
  https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/discoverer-security07.pdf
- Wireshark dissector guidance напоминает, что TCP payload нельзя считать
  готовыми сообщениями: нужны reassembly, обработка partial messages,
  multiple messages per segment и sanity checks:
  https://wiki.wireshark.org/lua/dissectors

Для нашего случая это означает:

- единица знания должна быть не raw packet, а protocol symbol/template;
- повтор captured packet полезен только как первый тест;
- accepted mapping должен появляться только после generalized replay/probe;
- нужно разделять vocabulary/message formats и state machine;
- нужно собирать controlled variations, а не только три одинаковых повтора.

## Целевая Архитектура Конвейера

Целевой pipeline:

```text
help-mcp API inventory
        |
        v
api-corpus manifest
        |
        v
controlled TestClient fixture form/base
        |
        v
1C TestManager harness executes one case at a time
        |
        v
Python TCP proxy captures bidirectional traffic
        |
        v
case-event correlation maps API case to frame ranges
        |
        v
normalizer extracts stable/dynamic/semantic fields
        |
        v
template renderer + replay/probe validates operation symbol
        |
        v
accepted protocol dictionary descriptor
```

Support plane для подготовки и проверки 1C-артефактов:

```text
edt-mcp target_id
        |
        +--> author/update client fixture project
        +--> author/update manager harness project

meta-mcp source_id
        |
        +--> source-qualified metadata/code evidence
        +--> same-name object collision protection

live-mcp connection_id
        |
        +--> read-only live checks through Windows COM provider
        +--> later guarded runtime probes without HTTP publication
```

## План Работ

### 0. MCP Infrastructure Binding

Outcome:

- one EDT workspace with two registered target contexts:
  - `target_id=client` -> `C:\1C_BASES\vanessa_client`;
  - `target_id=manager` -> `C:\1C_BASES\vanessa_manager`;
- two metadata sources:
  - `source_id=qa_client`;
  - `source_id=qa_manager`;
- two live runtime connections:
  - `connection_id=client`;
  - `connection_id=manager`.

Acceptance:

- `edt-mcp` lists both target contexts and target-bound validation succeeds;
- `meta-mcp` lists both metadata sources and scoped reads return
  source-qualified evidence;
- `live-mcp` lists both COM connections and can run read-only checks without
  HTTP publication;
- qa-mcp corpus artifacts store `target_id`, `source_id` and `connection_id`
  wherever a case depends on EDT metadata, static metadata or live runtime
  facts.

Status:

- `edt-mcp`: implemented and published;
- `meta-mcp`: implemented and published;
- `live-mcp`: implemented and published.

### 1. API Inventory From Help

Создать машинный inventory из `help-mcp`:

- объект;
- русское имя;
- английский alias;
- свойства;
- методы;
- конструкторы;
- параметры;
- возвращаемые типы;
- declared exceptions, если доступны;
- owner section;
- safety class по умолчанию.

Предлагаемый артефакт:

```text
docs/protocol-research/api-inventory/automated-testing-8.3.27.1786.json
```

Первичная классификация safety:

| Class | Meaning |
| --- | --- |
| `read_only` | чтение свойств, поиск объектов, получение коллекций |
| `safe_ui_action` | фокус, активизация, раскрытие, переключение страницы без бизнес-записи |
| `mutation` | ввод значения, выбор, нажатие команды, изменение данных |
| `agent_runtime` | операции агента клиентского приложения |
| `unsupported_initial` | требует отдельного fixture или не относится к TestClient TCP path |

### 2. Controlled Fixture Surface

Сделать контролируемую клиентскую форму или выбрать существующую форму только
как временный bootstrap target. Для стабильного корпуса предпочтительна своя
fixture form в TestClient базе.

Минимальный набор UI:

- `EditField` с уникальным caption/value;
- `CheckBox`;
- `Button`, безопасная кнопка без бизнес-мутации;
- `Table` с 2-3 стабильными строками;
- `CommandBar` и несколько команд, включая disabled command;
- `Page`/tab group;
- `Label`/decoration;
- `Group`;
- элементы с visible/disabled/read-only variants.

Каждый элемент должен иметь уникальные markers, например `PF_EDIT_MAIN`,
`PF_CHECKBOX_READONLY`, `PF_TABLE_ITEMS`, чтобы response parsing и evidence
review не зависели от случайных демо-строк.

С учетом выполненной карточки `edt-mcp` fixture нужно создавать и обновлять
через `target_id=client`, а не через неявный текущий EDT project. Перед
изменением формы или модулей target-bound операция должна подтвердить binding
проекта с `vanessa_client`.

### 3. TestManager Harness

На стороне manager базы нужна обработка/harness, которая принимает manifest и
выполняет один API case за раз.

Для каждого case harness должен писать side-channel record:

```json
{
  "case_id": "TestedFormField.Title.get",
  "run_id": "20260603-api-corpus-001",
  "started_at": "...",
  "finished_at": "...",
  "object": "ТестируемоеПолеФормы",
  "member": "Заголовок",
  "operation_kind": "property_get",
  "target_path": "ProtocolFixture.ManagedForm.EditField[PF_EDIT_MAIN]",
  "params": [],
  "repeat_index": 1,
  "expected_marker": "PF_EDIT_MAIN",
  "result_kind": "value",
  "result_value_preview": "PF_EDIT_MAIN",
  "exception": null,
  "pre_state": {},
  "post_state": {}
}
```

Ключевое требование: operation id должен быть виден в side-channel events и
должен коррелировать с proxy chunk counters. Не нужно внедрять marker bytes в
сам TCP protocol.

С учетом выполненной карточки `edt-mcp` manager harness нужно создавать и
обновлять через `target_id=manager`. Metadata lookup для кода harness должен
идти через `source_id=qa_manager`; metadata lookup для fixture-формы - через
`source_id=qa_client`.

### 4. Capture Layout

Runtime output:

```text
runtime/protocol-research/api-corpus/<run-id>/
  api_inventory.json
  case_manifest.json
  case_events.jsonl
  traffic.jsonl
  manager_to_client.bin
  client_to_manager.bin
  connections/
  cases/
    TestedForm/
      Title.get/
        manager_case.json
        traffic_slice.json
        probe_result.json
    TestedFormField/
      Value.get/
      Title.get/
      SetText.action/
```

Reviewed compact output:

```text
docs/protocol-research/evidence/api-corpus/<run-id>/
  corpus_summary.json
  corpus_cases.jsonl
  corpus_report.md
  accepted_mappings.json
  accepted_mappings.md
```

Raw bytes, full logs, screenshots and platform output stay under ignored
`runtime/`.

### 5. Repeat And Variation Strategy

Повторять каждый case три раза полезно, но недостаточно. Нужны две группы
прогонов:

1. Repeatability runs:
   - тот же объект;
   - тот же метод/свойство;
   - те же параметры;
   - fresh session и same session variants.

2. Controlled variation runs:
   - тот же метод на разных объектах одного класса;
   - тот же метод на разных subclasses/extensions;
   - разные параметры;
   - positive/negative result;
   - supported/disabled/invisible target;
   - different UI state before call.

Именно controlled variations позволяют отличить:

- session cookie от semantic token;
- object identity от method token;
- аргумент метода от случайного nonce;
- response marker от background refresh.

### 6. Analyzer And Dictionary

Analyzer должен строить operation descriptor, а не только hash:

```json
{
  "symbol": "TestedFormField.Title.get",
  "object": "ТестируемоеПолеФормы",
  "member": "Заголовок",
  "operation_kind": "property_get",
  "request_frame_range": {"from": 101, "to": 101},
  "response_frame_range": {"from": 102, "to": 102},
  "request_size": 347,
  "response_size": 332,
  "stable_fields": [],
  "dynamic_fields": [
    "ack_guid_uuid_le",
    "sequence_uint16_le",
    "nonce",
    "managed_form_guid_utf16le"
  ],
  "semantic_fields": [
    "operation_token",
    "element_path",
    "property_or_method_token"
  ],
  "state_preconditions": [
    "connected",
    "active_form_known",
    "target_element_resolved"
  ],
  "response_schema": "utf16 strings plus token echo",
  "replay_status": "accepted"
}
```

Accepted dictionary entry появляется только когда:

- есть frame range;
- есть stable normalized hash или accepted shape group;
- dynamic fields описаны;
- semantic token сохранен или объяснен;
- replay/probe с generated template воспроизвел результат;
- response markers совпали с expected result;
- evidence сохранено в compact reviewed form.

### 7. Replay/Probe Loop

Порядок проверки одной операции:

1. Replay original captured request.
2. Replay request with live ACK GUID, sequence and nonce.
3. Replay generalized template for the same object and member.
4. Replay with changed semantic target, if safe.
5. Replay negative target, if safe.
6. Compare response markers and state transition.

Цель: не подтвердить один captured packet, а доказать symbol template.

## Work Packages

### WP0: MCP Context Binding

Outcome:

- registered EDT targets `client` and `manager`;
- registered metadata sources `qa_client` and `qa_manager`;
- registered COM runtime connections `client` and `manager`;
- qa-mcp runtime configuration that records these ids in every corpus run.

Acceptance:

- EDT target listing and binding validation pass for both projects;
- metadata source listing and scoped lookup/search pass for both sources;
- no qa-mcp evidence stores bare metadata/code ids without `source_id`;
- live connection listing and read-only checks pass through COM for both
  `connection_id` values.

Current status:

- `edt-mcp`, `meta-mcp` and `live-mcp` support layers are implemented;
- local lab ids still need to be registered/configured and proven by preflight
  evidence before the first corpus run.

### WP1: Inventory

Outcome:

- `api_inventory.json`;
- class/member counts;
- safety classification;
- list of fixture requirements.

Acceptance:

- inventory generated from `help-mcp`;
- manually reviewed exclusions are explicit;
- no live 1C runtime required.

### WP2: Fixture

Outcome:

- controlled fixture form/base;
- target path map;
- stable expected markers.
- EDT changes applied through `target_id=client`.

Acceptance:

- TestClient can open the fixture form;
- read-only form analysis sees every target family;
- no business-data mutation is needed for read-only corpus.
- `validate_project_infobase_binding(target_id=client)` passes before
  retrieve/update/hot-deploy operations.

### WP3: Harness

Outcome:

- 1C manager harness executes manifest cases;
- side-channel JSON events;
- per-case result records.
- EDT changes applied through `target_id=manager`.

Acceptance:

- one operation maps to a case id;
- case start/end correlates with proxy chunk counters;
- exceptions are captured as results, not lost in logs.
- manager metadata/code evidence is requested with `source_id=qa_manager`;
- fixture metadata/code evidence is requested with `source_id=qa_client`.

### WP4: Corpus Runner

Outcome:

- `api-corpus` runner orchestrates TestClient, proxy, manager harness;
- runtime capture layout;
- compact reviewed report.

Acceptance:

- read-only subset runs end to end;
- cleanup stops only owned PIDs;
- raw bytes remain ignored.

### WP5: Analyzer

Outcome:

- frame ranges per API case;
- normalized shape groups;
- dynamic field table;
- semantic token candidates;
- response markers.

Acceptance:

- active-window/form existing mappings are reproduced;
- `form-element-details` receives accepted repeated request hash evidence;
- unsupported rows stay visible.

### WP6: Replay And Template Promotion

Outcome:

- generated templates per operation symbol;
- direct Python replay/probe proof;
- accepted dictionary descriptors.

Acceptance:

- accepted read-only descriptors expand beyond active window/form;
- useful probe-only descriptors are not promoted without reviewed wire evidence.

### WP7: Safe Actions

Outcome:

- safe action manifest for focus, activate window, switch page, expand menu;
- separated action frame ranges;
- recovery evidence.

Acceptance:

- no mutation cases in safe-action corpus;
- action rows require replay/probe proof before acceptance.

### WP8: Mutation Layer

Outcome:

- controlled mutation cases;
- rollback/recovery plan;
- state cleanup evidence.

Acceptance:

- mutation starts only after read-only and safe-action dictionaries are stable;
- every mutating case has recovery and infobase cleanup evidence.

## Near-Term Priority

The next practical changes should be:

1. Create or connect the EDT workspace for the lab and register target
   contexts:
   - `target_id=client`;
   - `target_id=manager`.
2. Register metadata sources in `meta-mcp`:
   - `source_id=qa_client`;
   - `source_id=qa_manager`.
3. Configure live-mcp Windows COM connections in no-default mode and run
   preflight checks:
   - `connection_id=client`;
   - `connection_id=manager`;
   - `list_live_connections`;
   - `check_com_connection` for both ids.
4. Generate and review `api_inventory.json` from `help-mcp`.
5. Build a first `api-corpus` manifest for read-only operations on:
   - `ТестируемоеПриложение`;
   - `ТестируемоеОкноКлиентскогоПриложения`;
   - `ТестируемаяФорма`;
   - `ТестируемоеПолеФормы`.

After that, implement the manager harness, create the controlled client fixture
through `edt-mcp`, and run a small end-to-end corpus before adding all classes.

## Risk Controls

- Do not accept mappings from metadata or help alone.
- Do not infer action behavior from read-only response shapes.
- Do not combine many operations into one unsegmented capture.
- Do not treat same-size responses as equivalent without markers.
- Do not normalize operation tokens until repeated evidence proves they are
  non-semantic.
- Do not start mutation research without rollback and recovery evidence.

## Relationship To Current Status

The current accepted surface remains limited:

- `active-window-context`;
- `active-form-context`.

Infrastructure status is better than protocol coverage:

- EDT authoring can now be routed by `target_id`;
- metadata/code evidence can now be routed and stored by `source_id`;
- live runtime checks can now be routed by `connection_id` through Windows COM
  without HTTP publication;
- accepted TestClient wire symbols have not expanded just because support MCPs
  were improved.

The roadmap is intended to replace the current manual-growth model with a
finite API-driven corpus pipeline. The current research tools remain useful,
but they need to become stages in a repeatable corpus system rather than
standalone one-off probes.
