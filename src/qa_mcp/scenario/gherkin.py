"""Gherkin (.feature) → Scenario transpiler (card 74 Phase 4).

Parses Russian/English Gherkin and maps recognized step phrasings to the runner's Step kinds via
a pattern registry. Steps the runner cannot yet execute are reported as `unmapped` (coverage grows
as action kinds are added) — the transpiler never silently drops a step.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from typing import Any, Callable

from .model import Scenario, Step

# Gherkin step keywords to strip (ru + en), longest-first so "И" doesn't shadow nothing.
_KEYWORDS = ("Допустим", "Дано", "Когда", "Тогда", "Также", "Но", "И", "*",
             "Given", "When", "Then", "And", "But")
_FEATURE_RE = re.compile(r"^\s*(Функционал|Функция|Feature)\s*:\s*(?P<name>.*)$", re.IGNORECASE)
_SCENARIO_RE = re.compile(r"^\s*(Сценарий|Scenario)\s*:\s*(?P<name>.*)$", re.IGNORECASE)


def _strip_keyword(line: str) -> str:
    s = line.strip()
    for kw in _KEYWORDS:
        if s == kw or s.startswith(kw + " "):
            return s[len(kw):].strip()
    return s


@dataclass
class StepPattern:
    regex: re.Pattern[str]
    build: Callable[[re.Match[str]], Step]
    phrase: str = ""        # canonical human-readable phrasing (the discoverable step-library entry)
    example: str = ""       # a concrete example line that matches ``regex``
    description: str = ""   # what the step does
    category: str = "action"  # read | action | navigation


def _q(name: str) -> str:
    # a single/double-quoted capture group; allows an EMPTY value ('') — real Vanessa corpora assert
    # cleared fields with «… стал равен ''» (card 103).
    return rf"(?P<{name}_quote>['\"])(?P<{name}>.*?)(?P={name}_quote)"


# kind patterns -> Step. `name` defaults to the matched phrase. Each entry also carries its discoverable
# step-library metadata (phrase / example / description / category) — the registry IS the step vocabulary,
# exposed via search_steps() and the search_for_steps MCP tool (vanessa-mcp parity).
STEP_PATTERNS: list[StepPattern] = [
    StepPattern(re.compile(rf"я (?:читаю|получаю) активн\w* окн\w*", re.I),
                lambda m: Step(kind="read_active_window", name="read active window"),
                phrase="Я читаю активное окно", example="Я читаю активное окно",
                description="Read the active window's identity and markers (no Vanessa).", category="read"),
    StepPattern(re.compile(rf"я (?:читаю|получаю) (?:сводку формы|форму)", re.I),
                lambda m: Step(kind="read_form_summary", name="read form summary"),
                phrase="Я получаю сводку формы", example="Я получаю сводку формы",
                description="Read the current form summary (element/value snapshot).", category="read"),
    StepPattern(re.compile(rf"я (?:читаю|получаю) элемент {_q('marker')}", re.I),
                lambda m: Step(kind="read_element", name=f"read {m['marker']}", marker=m["marker"]),
                phrase="Я читаю элемент 'ИмяЭлемента'", example="Я читаю элемент 'PF_LAST_ACTION'",
                description="Read a single form element/marker by name.", category="read"),
    # Card 79 (Fork 1): EFFECT verification on a read — combined "field value contains" form.
    StepPattern(re.compile(rf"значени\w* поля {_q('field')} содержит {_q('value')}", re.I),
                lambda m: Step(kind="read_form_value", name=f"value {m['field']} contains {m['value']}",
                               marker=m["field"], expect_contains=m["value"]),
                phrase="Значение поля 'Имя' содержит 'Текст'",
                example="Значение поля 'PF_EDIT_STRING' содержит 'VALUE'",
                description="Assert a field's live value contains the given text (read + assert).", category="read"),
    # Card 79 (Fork 1): read a field's live value (assert via a following "результат содержит").
    StepPattern(re.compile(rf"я (?:читаю|получаю) значени\w* поля {_q('field')}", re.I),
                lambda m: Step(kind="read_form_value", name=f"read value {m['field']}", marker=m["field"]),
                phrase="Я читаю значение поля 'Имя'", example="Я читаю значение поля 'PF_EDIT_STRING'",
                description="Read a field's live value (assert with a following «результат содержит»).",
                category="read"),
    StepPattern(re.compile(rf"я открываю список {_q('catalog')}", re.I),
                lambda m: Step(kind="open_list", name=f"open list {m['catalog']}", marker="e1cib/list/",
                               params={"catalog": m["catalog"]}),
                phrase="Я открываю список 'Справочник'", example="Я открываю список 'Товары'",
                description="Open a catalog/dynamic list.", category="navigation"),
    StepPattern(re.compile(rf"я выбираю строку {_q('old')}(?: как {_q('new')})?", re.I),
                lambda m: Step(kind="select_row", name=f"select {m['old']}", marker=m["old"],
                               params={"old_value": m["old"], "new_value": m["new"] or m["old"]}),
                phrase="Я выбираю строку 'Значение' [как 'Новое']",
                example="Я выбираю строку 'PF_ROW_002_TEXT'",
                description="Select a table row by a cell value (optionally re-target to another row).",
                category="action"),
    StepPattern(re.compile(rf"я открываю карточку(?: кнопкой {_q('button')})?", re.I),
                lambda m: Step(kind="open_card", name="open card", marker=(m["button"] or "Изменить"),
                               params={"button": m["button"] or "Изменить"}),
                phrase="Я открываю карточку [кнопкой 'Имя']", example="Я открываю карточку",
                description="Drill the active list row into its record card.", category="navigation"),
    # Vanessa-canonical: "я нажимаю на кнопку [с именем] 'X'" — press the button (by name or caption).
    StepPattern(re.compile(rf"я нажимаю на кнопку (?:с именем )?{_q('button')}", re.I),
                lambda m: Step(kind="click_button", name=f"click {m['button']}", marker=m["button"]),
                phrase="Я нажимаю на кнопку с именем 'Имя'",
                example="Я нажимаю на кнопку с именем 'PF_ADD_ROW'",
                description="Click a form command/button by name or caption.", category="action"),
    StepPattern(re.compile(rf"в поле ссылки (?:с именем )?{_q('field')} я выбираю {_q('value')}", re.I),
                lambda m: Step(kind="input_text", name=f"select reference {m['field']}", marker=m["field"],
                               params={"old_value": m["field"], "new_value": m["value"],
                                       "field_mode": "reference", "value_type": "reference"}),
                phrase="В поле ссылки с именем 'Имя' я выбираю 'Значение'",
                example="В поле ссылки с именем 'Владелец' я выбираю 'Корнет ЗАО'",
                description="Select a reference display value in an open-link form field.", category="action"),
    # Vanessa-canonical: "в поле [с именем] 'F' я ввожу текст 'V'" — re-target the field value.
    StepPattern(re.compile(rf"в поле (?:с именем )?{_q('field')} я ввожу текст {_q('value')}", re.I),
                lambda m: Step(kind="input_text", name=f"input {m['field']}", marker=m["field"],
                               params={"old_value": m["field"], "new_value": m["value"]}),
                phrase="В поле с именем 'Имя' я ввожу текст 'Значение'",
                example="В поле с именем 'PF_EDIT_STRING' я ввожу текст 'NEW'",
                description="Type a value into a form field by name.", category="action"),
    # Vanessa-canonical: "я перехожу к закладке с именем 'P'" — switch the active tab page (card 86d).
    StepPattern(re.compile(rf"я перехожу к закладке с именем {_q('page')}", re.I),
                lambda m: Step(kind="switch_page", name=f"switch page {m['page']}", marker=m["page"]),
                phrase="Я перехожу к закладке с именем 'Имя'",
                example="Я перехожу к закладке с именем 'PF_PAGE_A'",
                description="Switch the active tab page.", category="navigation"),

    # --- Card 103 (E-FW) — Vanessa-canonical breadth, measured against the real project corpus
    # (public demo + private third-party Vanessa features). Each phrasing maps onto an existing 52-tool
    # capability; the highest-frequency corpus gaps come first. ---

    # Assert a form opened — Vanessa «Тогда открылась форма с именем 'X'» (corpus freq #1).
    StepPattern(re.compile(rf"открыл\w* форм\w* с именем {_q('marker')}", re.I),
                lambda m: Step(kind="assert_form_open", name=f"form open {m['marker']}", marker=m["marker"]),
                phrase="Открылась форма с именем 'Имя'",
                example="Открылась форма с именем 'Документ.Заказ.Форма.ФормаДокумента'",
                description="Assert a form with the given name is open.", category="read"),
    # Assert an element is present on the form — «элемент формы с именем 'X' присутствует на форме» (#2).
    StepPattern(re.compile(rf"элемент формы с именем {_q('marker')} присутствует на форме", re.I),
                lambda m: Step(kind="assert_element_present", name=f"present {m['marker']}", marker=m["marker"]),
                phrase="Элемент формы с именем 'Имя' присутствует на форме",
                example="Элемент формы с именем 'ДатаНачала' присутствует на форме",
                description="Assert a form element with the given name exists.", category="read"),
    # Assert an element's value EQUALS — «элемент формы с именем 'X' стал равен 'Y'» (#4, strict equality).
    StepPattern(re.compile(rf"элемент формы с именем {_q('field')} стал\w* рав\w* {_q('value')}", re.I),
                lambda m: Step(kind="read_form_value", name=f"equals {m['field']}", marker=m["field"],
                               expect_equals=m["value"]),
                phrase="Элемент формы с именем 'Имя' стал равен 'Значение'",
                example="Элемент формы с именем 'Договор' стал равен 'Основной'",
                description="Read an element and assert its value equals the text.", category="read"),
    # Open a metadata object's main form — «я открываю основную форму документа/обработки/… 'X'» (#3 family).
    StepPattern(re.compile(rf"я открываю основную форму (?P<otype>документа|обработки|отч[её]та|"
                           rf"списка справочника|справочника|регистра сведений|регистра накопления) {_q('name')}", re.I),
                lambda m: Step(kind="open_main_form", name=f"open main form {m['name']}", marker=m["name"],
                               params={"object_type": m["otype"].lower()}),
                phrase="Я открываю основную форму документа 'Имя'",
                example="Я открываю основную форму документа 'Заказ'",
                description="Open the main form of a metadata object (document/processing/report/catalog).",
                category="navigation"),
    # Card 109: open an EXTERNAL data processor/report (.epf/.erf) by file path — the corpus residual that closes
    # transpile to 100%. «Я открываю внешнюю обработку или отчет "<path>" (Расширение)». Executes via the native
    # «Главное меню → Файл → Открыть» xtest flow (the `open_external_processor` tool), not the protocol runner.
    StepPattern(re.compile(rf"я открываю внешнюю обработку или отчет {_q('path')}(?:\s*\((?P<mode>[^)]*)\))?", re.I),
                lambda m: Step(kind="open_external_epf", name=f"open epf {m['path']}", marker=m["path"],
                               params={"mode": (m["mode"] or "").strip()}),
                phrase="Я открываю внешнюю обработку или отчет \"путь.epf\" (Расширение)",
                example="Я открываю внешнюю обработку или отчет \"/opt/1c-dev/.../X.epf\" (Расширение)",
                description="Open an external data processor/report (.epf/.erf) by file path (native Файл→Открыть; "
                            "xtest — executed by the open_external_processor tool).",
                category="navigation"),
    # Card 106 change 4: open a NEW-object CREATE form — «я создаю новый документ/элемент справочника 'X'».
    StepPattern(re.compile(rf"я создаю новый (?P<otype>документ|элемент справочника|справочник) {_q('name')}", re.I),
                lambda m: Step(kind="open_create_form", name=f"create {m['name']}", marker=m["name"],
                               params={"object_type": m["otype"].lower()}),
                phrase="Я создаю новый документ 'Имя'",
                example="Я создаю новый документ 'Заказ'",
                description="Open a new-object create form (document or catalog item).",
                category="navigation"),
    # Close the active/current window — «я закрываю текущее окно» (#5).
    StepPattern(re.compile(r"я закрываю текущее окно", re.I),
                lambda m: Step(kind="close_window", name="close current window", params={"target": "current"}),
                phrase="Я закрываю текущее окно", example="Я закрываю текущее окно",
                description="Close the active window.", category="navigation"),
    # Close every client-application window — «я закрываю все окна клиентского приложения».
    StepPattern(re.compile(r"я закрываю все окна клиентского приложения", re.I),
                lambda m: Step(kind="close_all_windows", name="close all windows"),
                phrase="Я закрываю все окна клиентского приложения",
                example="Я закрываю все окна клиентского приложения",
                description="Close every open window of the client application.", category="navigation"),
    # Close a named window — «я закрываю окно 'X'» (after the текущее/все variants so it can't shadow them).
    StepPattern(re.compile(rf"я закрываю окно {_q('marker')}", re.I),
                lambda m: Step(kind="close_window", name=f"close window {m['marker']}", marker=m["marker"]),
                phrase="Я закрываю окно 'Заголовок'", example="Я закрываю окно 'Договоры контрагентов'",
                description="Close a window by caption.", category="navigation"),
    # Assert a window opened — «открылось окно 'X'».
    StepPattern(re.compile(rf"открыл\w* окно {_q('marker')}", re.I),
                lambda m: Step(kind="assert_window_open", name=f"window open {m['marker']}", marker=m["marker"]),
                phrase="Открылось окно 'Заголовок'", example="Открылось окно 'Договоры контрагентов'",
                description="Assert a window with the given caption is open.", category="read"),
    # Wait for a window to open within N seconds — «я жду открытия окна 'X' в течение N секунд».
    StepPattern(re.compile(rf"я жду открыти\w* окна {_q('marker')} в течение (?P<timeout>\d+) секунд", re.I),
                lambda m: Step(kind="wait_window", name=f"wait window {m['marker']}", marker=m["marker"],
                               params={"timeout_sec": int(m["timeout"])}),
                phrase="Я жду открытия окна 'Заголовок' в течение N секунд",
                example="Я жду открытия окна 'Договоры контрагентов' в течение 20 секунд",
                description="Wait until a window with the caption opens, up to N seconds.", category="read"),
    # Assert a button exists (element-present variant) — «кнопка 'X' существует».
    StepPattern(re.compile(rf"кнопка {_q('marker')} существует", re.I),
                lambda m: Step(kind="assert_element_present", name=f"button exists {m['marker']}", marker=m["marker"]),
                phrase="Кнопка 'Имя' существует", example="Кнопка 'Договоры' существует",
                description="Assert a button with the given name exists on the form.", category="read"),
    # Select / go to the current row of a table — «в таблице 'T' я выбираю текущую строку / перехожу к строке».
    StepPattern(re.compile(rf"в таблице {_q('table')} я выбираю текущую строку", re.I),
                lambda m: Step(kind="select_row", name=f"select current row {m['table']}", marker=m["table"],
                               params={"table": m["table"], "current": True}),
                phrase="В таблице 'Имя' я выбираю текущую строку",
                example="В таблице 'Список' я выбираю текущую строку",
                description="Select the current row of a table.", category="action"),
    StepPattern(re.compile(rf"в таблице {_q('table')} я перехожу к строке\s*$", re.I),
                lambda m: Step(kind="select_row", name=f"goto row {m['table']}", marker=m["table"],
                               params={"table": m["table"], "current": True}),
                phrase="В таблице 'Имя' я перехожу к строке",
                example="В таблице 'Список' я перехожу к строке",
                description="Move to the current row of a table.", category="action"),
    # Connect/launch a TestClient by profile — «я подключаю профиль TestClient 'X'» (qa-mcp owns the client).
    StepPattern(re.compile(rf"я подключаю профиль testclient {_q('marker')}", re.I),
                lambda m: Step(kind="connect_client", name=f"connect profile {m['marker']}", marker=m["marker"]),
                phrase="Я подключаю профиль TestClient 'Имя'",
                example="Я подключаю профиль TestClient 'sample-thin'",
                description="Connect/launch a TestClient by profile name (qa-mcp owns the client).",
                category="navigation"),
    # Vanessa-runtime setting flag — RECOGNIZED but a no-op for qa-mcp (no Vanessa runtime).
    StepPattern(re.compile(rf"я устанавливаю флаг настройки vanessa automation {_q('marker')}", re.I),
                lambda m: Step(kind="skip_step", name=f"skip vanessa setting {m['marker']}", marker=m["marker"],
                               params={"reason": "vanessa-runtime setting; no qa-mcp equivalent"}),
                phrase="Я устанавливаю флаг настройки Vanessa Automation 'Имя'",
                example="Я устанавливаю флаг настройки Vanessa Automation 'ИспользоватьКомпонентуVanessaExt'",
                description="Vanessa-runtime setting — recognized and skipped (no Vanessa runtime in qa-mcp).",
                category="skipped"),

    # --- Card 103 Wave 2 — steps that carry a DataTable (the «:»-suffixed forms). The parser attaches the
    # following `| … |` rows as params["table"]; the phrasing alone still transpiles (table optional). ---
    # Assert a table contains rows — «таблица 'T' содержит строки:» + DataTable.
    StepPattern(re.compile(rf"таблица {_q('table')} содержит строки", re.I),
                lambda m: Step(kind="assert_table_rows", name=f"table rows {m['table']}", marker=m["table"],
                               params={"table": m["table"]}),
                phrase="Таблица 'Имя' содержит строки:",
                example="Таблица 'ФайлыСервера' содержит строки:",
                description="Assert a table contains the rows given in the following DataTable.", category="read"),
    # Per-step perf budget — «каждый шаг выполняется быстрее N мс» (card 111 item 6, beyond Vanessa).
    StepPattern(re.compile(r"(?:кажд\w+ шаг|шаги|все шаги) выполня\w+ быстрее (?P<ms>\d+)\s*(?:мс|ms)", re.I),
                lambda m: Step(kind="assert_step_perf", name=f"steps within {m['ms']}ms",
                               params={"max_ms": float(m["ms"])}),
                phrase="Каждый шаг выполняется быстрее 5000 мс",
                example="Каждый шаг выполняется быстрее 5000 мс",
                description="Assert every prior step in the scenario completed within N ms (per-step perf budget).",
                category="read"),
    # Go to a table row matching the following DataTable — «в таблице 'T' я перехожу к строке:» + DataTable.
    StepPattern(re.compile(rf"в таблице {_q('table')} я перехожу к строке:", re.I),
                lambda m: Step(kind="select_row", name=f"goto row by table {m['table']}", marker=m["table"],
                               params={"table": m["table"], "by_table": True}),
                phrase="В таблице 'Имя' я перехожу к строке:",
                example="В таблице 'ФайлыСервера' я перехожу к строке:",
                description="Move to the table row matching the following DataTable (column=value).",
                category="action"),
    # Connect a TestClient from a parameters DataTable — «я подключаю клиент тестирования с параметрами:».
    StepPattern(re.compile(r"я подключаю клиент тестирования с параметрами", re.I),
                lambda m: Step(kind="connect_client", name="connect with params", params={"with_params": True}),
                phrase="Я подключаю клиент тестирования с параметрами:",
                example="Я подключаю клиент тестирования с параметрами:",
                description="Connect/launch a TestClient from the following parameters DataTable.",
                category="navigation"),
    # Nested scenario call — «я выполняю сценарий 'X'» / «выполнить сценарий 'X'».
    StepPattern(re.compile(rf"(?:я выполняю|выполнить) сценарий {_q('marker')}", re.I),
                lambda m: Step(kind="run_subscenario", name=f"run scenario {m['marker']}", marker=m["marker"]),
                phrase="Я выполняю сценарий 'Имя'", example="Я выполняю сценарий 'Вход в систему'",
                description="Run another scenario by name as a nested step.", category="action"),

    # --- Card 105 (E-XV) — DATA-LAYER assertion via read-only OData (beyond Vanessa, which is UI-only). The
    # OData $filter is double-quoted so it can contain single-quoted string literals. ---
    StepPattern(re.compile(rf'в базе {_q("entity")} где "(?P<filter>[^"]*)" поле {_q("field")} равно {_q("value")}', re.I),
                lambda m: Step(kind="assert_data", name=f"db {m['entity']}.{m['field']}", marker=m["entity"],
                               params={"entity_set": m["entity"], "filter": m["filter"], "field": m["field"],
                                       "expected": m["value"], "match": "equals"}),
                phrase="В базе 'EntitySet' где \"<OData-фильтр>\" поле 'Поле' равно 'Значение'",
                example="В базе 'Catalog_Товары' где \"Description eq 'Обувь'\" поле 'Code' равно '000000001'",
                description="Assert a value in the data layer via read-only OData — cross-check that a UI action "
                            "persisted (beyond Vanessa).",
                category="read"),
    # Card 111 item 7 (E-XV) — DATA-LAYER COUNT assertion (deeper than a single field).
    StepPattern(re.compile(rf'в базе {_q("entity")} где "(?P<filter>[^"]*)" количество записей '
                           r'(?P<cmp>не меньше|не больше|равно|больше|меньше) (?P<n>\d+)', re.I),
                lambda m: Step(kind="assert_data_count", name=f"db count {m['entity']} {m['cmp']} {m['n']}",
                               marker=m["entity"],
                               params={"entity_set": m["entity"], "filter": m["filter"], "expected": int(m["n"]),
                                       "op": {"равно": "eq", "больше": "gt", "меньше": "lt",
                                              "не меньше": "ge", "не больше": "le"}[m["cmp"].lower()]}),
                phrase="В базе 'EntitySet' где \"<OData-фильтр>\" количество записей равно N",
                example="В базе 'Catalog_Товары' где \"Code ne ''\" количество записей больше 0",
                description="Assert the NUMBER of records matching the filter (eq/больше/меньше/не меньше/не "
                            "больше) — a deeper data-layer check than a single field (beyond Vanessa).",
                category="read"),
    StepPattern(re.compile(rf'в базе {_q("entity")} где "(?P<filter>[^"]*)" записей нет', re.I),
                lambda m: Step(kind="assert_data_count", name=f"db count {m['entity']} == 0", marker=m["entity"],
                               params={"entity_set": m["entity"], "filter": m["filter"], "expected": 0,
                                       "op": "eq"}),
                phrase="В базе 'EntitySet' где \"<OData-фильтр>\" записей нет",
                example="В базе 'Catalog_Товары' где \"Description eq 'НетТакого'\" записей нет",
                description="Assert NO record matches the filter (data-layer absence check, beyond Vanessa).",
                category="read"),
]


def step_library() -> list[dict[str, str]]:
    """The discoverable Gherkin step vocabulary — each supported step's phrasing, example, native Step kind,
    category and description. Derived from STEP_PATTERNS (single source of truth), so it never drifts from what
    the transpiler actually recognizes. The trailing «И результат содержит 'Текст'» assertion modifier attaches
    to the preceding read step."""
    library: list[dict[str, str]] = []
    for pattern in STEP_PATTERNS:
        match = pattern.regex.search(pattern.example)
        kind = pattern.build(match).kind if match else "?"
        library.append({"phrase": pattern.phrase, "example": pattern.example, "kind": kind,
                        "category": pattern.category, "description": pattern.description})
    library.append({"phrase": "И результат содержит 'Текст'", "example": "И результат содержит 'VALUE'",
                    "kind": "assert", "category": "read",
                    "description": "Assertion modifier: the preceding read step's result must contain the text."})
    return library


def search_steps(keywords: str = "") -> list[dict[str, str]]:
    """Search the step vocabulary by keyword(s) — the search_for_steps-equivalent. Empty ``keywords`` returns the
    whole library. Each whitespace-separated token must appear (case-insensitive) somewhere in the entry."""
    library = step_library()
    tokens = keywords.lower().split()
    if not tokens:
        return library
    def hay(entry: dict[str, str]) -> str:
        return " ".join(entry.values()).lower()
    return [entry for entry in library if all(token in hay(entry) for token in tokens)]

# assertion pattern: attaches expect_contains to the PREVIOUS step
_ASSERT_RE = re.compile(rf"результат содержит {_q('text')}", re.I)


@dataclass
class TranspileResult:
    scenario: Scenario
    unmapped: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"scenario": self.scenario.name, "steps": len(self.scenario.steps), "unmapped": self.unmapped}


# Card 103 Wave 2 — BDD structure keywords (ru + en).
_BACKGROUND_RE = re.compile(r"^\s*(Предыстория|Background)\s*:", re.IGNORECASE)
_OUTLINE_RE = re.compile(r"^\s*(Структура сценария|Scenario Outline|Scenario Template)\s*:\s*(?P<name>.*)$", re.IGNORECASE)
_EXAMPLES_RE = re.compile(r"^\s*(Примеры|Examples)\s*:", re.IGNORECASE)


def _split_row(line: str) -> list[str]:
    """Split a Gherkin table row '| a | b |' into stripped cells, preserving escaped pipes."""
    text = line.strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|"):
        text = text[:-1]
    if not text:
        return [""]

    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for ch in text:
        if escaped:
            current.append("|" if ch == "|" else "\\" + ch)
            escaped = False
        elif ch == "\\":
            escaped = True
        elif ch == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
    if escaped:
        current.append("\\")
    cells.append("".join(current).strip())
    return cells


def _unquote(cell: str) -> str:
    if len(cell) >= 2 and cell[0] in "'\"" and cell[-1] == cell[0]:
        return cell[1:-1]
    return cell


def _substitute(text: str, mapping: dict[str, str]) -> str:
    """Outline placeholder substitution: replace each <column> with its Examples-row value."""
    for col, val in mapping.items():
        text = text.replace(f"<{col}>", val)
    return text


def _prepend_background(scenario: dict[str, Any], background: dict[str, Any]) -> None:
    """Prepend Background steps (+ their tables) to a scenario, shifting the scenario's own table indices."""
    bsteps = background.get("steps") or []
    if not bsteps:
        return
    n = len(bsteps)
    scenario["steps"] = list(bsteps) + scenario["steps"]
    shifted = {i + n: t for i, t in scenario["tables"].items()}
    shifted.update(background.get("tables") or {})
    scenario["tables"] = shifted


def _expand_outline(outline: dict[str, Any], background: dict[str, Any], out: list[dict[str, Any]]) -> None:
    """Expand a Scenario Outline into one scenario per Examples data row (header→value substitution)."""
    example_blocks = outline.get("examples") or []
    expanded = False
    for examples in example_blocks:
        if len(examples) < 2:
            continue
        header = [_unquote(c) for c in examples[0]]
        for row in examples[1:]:
            mapping = dict(zip(header, [_unquote(c) for c in row]))
            sc = {
                "name": _substitute(outline["name"], mapping),
                "tags": list(outline["tags"]),
                "steps": [_substitute(s, mapping) for s in outline["steps"]],
                "tables": {i: [[_substitute(c, mapping) for c in r] for r in t]
                           for i, t in outline["tables"].items()},
            }
            _prepend_background(sc, background)
            out.append(sc)
            expanded = True
    if not expanded:  # no data rows — keep the outline as a single (unsubstituted) scenario
        _prepend_background(outline, background)
        out.append({k: outline[k] for k in ("name", "tags", "steps", "tables")})


def parse_feature(text: str) -> list[dict[str, Any]]:
    """Split a .feature into scenarios with keyword-stripped steps, @tags, attached DataTables and expanded
    Scenario Outline examples (card 103 Wave 2).

    Each scenario dict: ``{name, tags: [str], steps: [str], tables: {step_index: [[cell,…],…]}}``. Background
    steps prepend to every scenario; @tags attach to the next Feature/Scenario (feature tags inherit); a
    Scenario Outline's ``Примеры:`` table expands into one scenario per data row with ``<col>`` substitution."""
    scenarios: list[dict[str, Any]] = []
    feature_tags: list[str] = []
    pending_tags: list[str] = []
    background: dict[str, Any] = {"steps": [], "tables": {}}
    current: dict[str, Any] | None = None
    section: str | None = None       # 'background' | 'scenario'
    in_examples = False
    in_docstring = False

    def container() -> dict[str, Any] | None:
        return background if section == "background" else current

    def finalize() -> None:
        nonlocal current
        if current is None:
            return
        if current.pop("_outline", False):
            _expand_outline(current, background, scenarios)
        else:
            _prepend_background(current, background)
            scenarios.append({k: current[k] for k in ("name", "tags", "steps", "tables")})
        current = None

    for raw in text.splitlines():
        line = raw.strip()
        if in_docstring:
            if line.startswith('"""'):
                in_docstring = False
            continue
        if not line or line.startswith("#"):
            continue
        if line.startswith("@"):
            pending_tags.extend(t for t in line.split() if t.startswith("@"))
            continue
        if _FEATURE_RE.match(line):
            feature_tags = pending_tags
            pending_tags = []
            continue
        if _BACKGROUND_RE.match(line):
            finalize()
            section = "background"
            in_examples = False
            background = {"steps": [], "tables": {}}
            continue
        mo = _OUTLINE_RE.match(line)
        ms = None if mo else _SCENARIO_RE.match(line)
        if mo or ms:
            finalize()
            name = (mo.group("name") if mo else ms.group("name")).strip() or "scenario"
            current = {"name": name, "tags": feature_tags + pending_tags, "steps": [], "tables": {},
                       "examples": []}
            if mo:
                current["_outline"] = True
            pending_tags = []
            section = "scenario"
            in_examples = False
            continue
        if _EXAMPLES_RE.match(line):
            in_examples = True
            if current is not None:
                current.setdefault("examples", []).append([])
            continue
        if line.startswith('"""'):
            cont = container()
            if cont is not None:
                cont["steps"].append("unsupported docstring block")
            in_docstring = True
            continue
        if line.startswith("|"):
            row = _split_row(line)
            if in_examples and current is not None:
                current.setdefault("examples", [])
                if not current["examples"]:
                    current["examples"].append([])
                current["examples"][-1].append(row)
            else:
                cont = container()
                if cont is not None and cont["steps"]:
                    cont["tables"].setdefault(len(cont["steps"]) - 1, []).append(row)
            continue
        cont = container()
        if cont is not None:
            cont["steps"].append(_strip_keyword(line))
    finalize()
    return scenarios


def transpile_scenario(
    name: str,
    raw_steps: list[str],
    *,
    tables: dict[int, list[list[str]]] | None = None,
    tags: list[str] | None = None,
) -> TranspileResult:
    """Transpile a scenario's step lines to a Scenario. ``tables`` (card 103 Wave 2) attaches a DataTable to
    the step at that raw-line index as ``params['table']``; ``tags`` carries the scenario's @tags."""
    steps: list[Step] = []
    unmapped: list[str] = []
    tables = tables or {}
    for index, raw in enumerate(raw_steps):
        text = raw["text"] if isinstance(raw, dict) else raw
        assert_m = _ASSERT_RE.search(text)
        if assert_m:
            if steps:
                last = steps[-1]
                steps[-1] = replace(last, expect_contains=assert_m.group("text"))
            else:
                unmapped.append(text)
            continue
        for pattern in STEP_PATTERNS:
            m = pattern.regex.search(text)
            if m:
                step = pattern.build(m)
                table = tables.get(index)
                if table is not None:
                    step = replace(step, params={**step.params, "table": table})
                steps.append(step)
                break
        else:
            unmapped.append(text)
    return TranspileResult(scenario=Scenario(name=name, steps=steps, tags=list(tags or [])), unmapped=unmapped)


def transpile_feature(text: str) -> list[TranspileResult]:
    return [
        transpile_scenario(s["name"], s["steps"], tables=s.get("tables"), tags=s.get("tags"))
        for s in parse_feature(text)
    ]


def filter_by_tags(
    results: list[TranspileResult],
    include: tuple[str, ...] | list[str] = (),
    exclude: tuple[str, ...] | list[str] = (),
) -> list[TranspileResult]:
    """Card 103 Wave 2 — select transpiled scenarios by @tags. ``include`` keeps scenarios carrying ANY of the
    given tags; ``exclude`` drops scenarios carrying ANY of them. Tag names may omit the leading '@'."""
    def norm(t: str) -> str:
        return t if t.startswith("@") else "@" + t
    inc = {norm(t) for t in include}
    exc = {norm(t) for t in exclude}
    out: list[TranspileResult] = []
    for r in results:
        tags = set(r.scenario.tags)
        if inc and not (tags & inc):
            continue
        if exc and (tags & exc):
            continue
        out.append(r)
    return out
