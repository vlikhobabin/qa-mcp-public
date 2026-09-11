"""Card 74 Phase 4: Gherkin (.feature) -> Scenario transpiler (offline)."""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "src"))

from qa_mcp.scenario import parse_feature, transpile_feature, transpile_scenario  # noqa: E402


WAVE2_FEATURE = """# language: ru
@feature_tag
Функционал: демо BDD

  Предыстория:
    Дано я закрываю все окна клиентского приложения

  @smoke @ui
  Сценарий: таблица файлов
    И таблица 'ФайлыСервера' содержит строки:
      | 'Имя' |
      | 'a.txt' |

  Структура сценария: открыть <Документ>
    Дано Я открываю основную форму документа '<Документ>'
    Тогда открылась форма с именем '<Форма>'

    Примеры:
      | Документ | Форма |
      | Заказ    | Документ.Заказ.Форма.ФормаДокумента |
      | Оплата   | Документ.Оплата.Форма.ФормаДокумента |
"""


def test_card103_wave2_tags_background_datatable_outline() -> None:
    from qa_mcp.scenario import filter_by_tags

    results = transpile_feature(WAVE2_FEATURE)
    # 1 table scenario + 2 expanded outline rows
    assert [r.scenario.name for r in results] == ["таблица файлов", "открыть Заказ", "открыть Оплата"]
    assert all(r.unmapped == [] for r in results), [r.unmapped for r in results]

    table_sc = results[0].scenario
    # feature tag inherited + scenario tags
    assert table_sc.tags == ["@feature_tag", "@smoke", "@ui"]
    # Background prepended, then the table step; the DataTable is attached to the table step's params
    assert [s.kind for s in table_sc.steps] == ["close_all_windows", "assert_table_rows"]
    assert table_sc.steps[1].params["table"] == [["'Имя'"], ["'a.txt'"]]

    # Outline expanded with <col> substitution, Background prepended to each
    zakaz = results[1].scenario
    assert [s.kind for s in zakaz.steps] == ["close_all_windows", "open_main_form", "assert_form_open"]
    assert zakaz.steps[1].marker == "Заказ"
    assert zakaz.steps[2].marker == "Документ.Заказ.Форма.ФормаДокумента"
    assert results[2].scenario.steps[1].marker == "Оплата"
    assert results[1].scenario.tags == ["@feature_tag"]  # outline inherits the feature tag

    # tag filtering: @smoke selects only the table scenario; exclude drops it
    assert [r.scenario.name for r in filter_by_tags(results, include=["smoke"])] == ["таблица файлов"]
    assert [r.scenario.name for r in filter_by_tags(results, exclude=["@smoke"])] == ["открыть Заказ", "открыть Оплата"]


def test_card105_data_assert_step_maps() -> None:
    r = transpile_scenario("db", [
        "В базе 'Catalog_Товары' где \"Description eq 'Обувь'\" поле 'Code' равно '000000001'",
    ])
    assert r.unmapped == []
    step = r.scenario.steps[0]
    assert step.kind == "assert_data"
    assert step.params == {
        "entity_set": "Catalog_Товары",
        "filter": "Description eq 'Обувь'",
        "field": "Code",
        "expected": "000000001",
        "match": "equals",
    }


def test_card103_corpus_canonical_steps_map() -> None:
    """Card 103 (E-FW): the high-frequency Vanessa-canonical phrasings measured against the real project
    corpus must transpile to the right kinds with no unmapped lines (drop-in authoring breadth)."""
    lines = [
        "Тогда открылась форма с именем 'Документ.Заказ.Форма.ФормаДокумента'",
        "И элемент формы с именем 'ДатаНачала' присутствует на форме",
        "И элемент формы с именем 'Договор' стал равен 'Основной'",
        "Когда я открываю основную форму документа 'Заказ'",
        "И я открываю основную форму обработки 'ФикстураПротоколаTestClient'",
        "И я открываю основную форму списка справочника 'Контрагенты'",
        "И я нажимаю на кнопку 'Список'",
        "Тогда открылось окно 'Договоры контрагентов'",
        "И я жду открытия окна 'Договоры контрагентов' в течение 20 секунд",
        "И кнопка 'Договоры' существует",
        "И в таблице 'Список' я выбираю текущую строку",
        "И я закрываю текущее окно",
        "И я закрываю окно 'Договоры контрагентов'",
        "И я закрываю все окна клиентского приложения",
        "Дано я подключаю профиль TestClient 'sample-thin'",
        "И я устанавливаю флаг настройки Vanessa Automation 'ИспользоватьКомпонентуVanessaExt'",
    ]
    r = transpile_scenario("corpus", lines)
    assert r.unmapped == [], r.unmapped
    kinds = [s.kind for s in r.scenario.steps]
    assert kinds == [
        "assert_form_open", "assert_element_present", "read_form_value",
        "open_main_form", "open_main_form", "open_main_form",
        "click_button", "assert_window_open", "wait_window", "assert_element_present",
        "select_row", "close_window", "close_window", "close_all_windows",
        "connect_client", "skip_step",
    ]
    # «стал равен» carries strict equality, not contains
    equals_step = r.scenario.steps[2]
    assert equals_step.marker == "Договор" and equals_step.expect_equals == "Основной"
    assert equals_step.expect_contains is None
    # open_main_form records the metadata object type; wait_window parses the timeout
    assert r.scenario.steps[3].params["object_type"] == "документа"
    assert r.scenario.steps[5].params["object_type"] == "списка справочника"
    assert r.scenario.steps[8].params["timeout_sec"] == 20
    # the close-current vs close-named variants are distinguished
    assert r.scenario.steps[11].params == {"target": "current"}
    assert r.scenario.steps[12].marker == "Договоры контрагентов"

FEATURE = """# language: ru
Функционал: складская навигация

  Сценарий: открыть склад и проверить
    Дано я читаю активное окно
    Тогда результат содержит 'HomePage'
    И я открываю список 'Справочник.Склады'
    И я выбираю строку 'Средний' как 'Малый'
    И я открываю карточку
    Когда я читаю сводку формы
    И я нажимаю на кнопку с именем 'PF_RESET_STATE'
"""


def test_parse_feature_splits_scenarios_and_strips_keywords() -> None:
    scenarios = parse_feature(FEATURE)
    assert len(scenarios) == 1
    s = scenarios[0]
    assert s["name"] == "открыть склад и проверить"
    # keywords stripped, comments/language line skipped
    assert s["steps"][0] == "я читаю активное окно"
    assert "нажимаю на кнопку" in s["steps"][-1]


def test_transpile_maps_supported_steps_and_reports_unmapped() -> None:
    result = transpile_feature(FEATURE)[0]
    kinds = [step.kind for step in result.scenario.steps]
    assert kinds == ["read_active_window", "open_list", "select_row", "open_card", "read_form_summary", "click_button"]
    # the assertion line attached expect_contains to the active-window step
    assert result.scenario.steps[0].expect_contains == "HomePage"
    # select_row carries the retarget params
    select = result.scenario.steps[2]
    assert select.params == {"old_value": "Средний", "new_value": "Малый"}
    assert select.marker == "Средний"
    # open_list catalog param
    assert result.scenario.steps[1].params == {"catalog": "Справочник.Склады"}
    # the Vanessa button-click step now maps to click_button (Phase 5 follow-up #1)
    assert any(s.kind == "click_button" and s.marker == "PF_RESET_STATE" for s in result.scenario.steps)
    assert result.unmapped == []


def test_vanessa_canonical_click_and_input_map() -> None:
    r = transpile_scenario("s", [
        "я нажимаю на кнопку с именем 'PF_RESET_STATE'",
        "в поле с именем 'PF_EDIT_STRING' я ввожу текст 'НовоеЗначение'",
    ])
    assert [s.kind for s in r.scenario.steps] == ["click_button", "input_text"]
    assert r.scenario.steps[0].marker == "PF_RESET_STATE"
    assert r.scenario.steps[1].params == {"old_value": "PF_EDIT_STRING", "new_value": "НовоеЗначение"}
    assert r.unmapped == []


def test_quoted_values_preserve_embedded_opposite_quote() -> None:
    single = transpile_scenario("s", ["в поле с именем 'Наименование' я ввожу текст 'ООО \"Ромашка\"'"])
    assert single.unmapped == []
    assert single.scenario.steps[0].params["new_value"] == 'ООО "Ромашка"'

    double = transpile_scenario("s", ['в поле с именем "Name" я ввожу текст "owner\'s value"'])
    assert double.unmapped == []
    assert double.scenario.steps[0].params["new_value"] == "owner's value"


def test_reference_input_maps_to_explicit_field_mode() -> None:
    r = transpile_scenario("s", ["в поле ссылки с именем 'Владелец' я выбираю 'Корнет ЗАО'"])

    step = r.scenario.steps[0]
    assert step.kind == "input_text"
    assert step.marker == "Владелец"
    assert step.params["new_value"] == "Корнет ЗАО"
    assert step.params["field_mode"] == "reference"
    assert step.params["value_type"] == "reference"
    assert r.unmapped == []


def test_read_form_value_combined_and_separate_assert_map() -> None:
    # Card 79 (Fork 1): both the combined "значение поля 'F' содержит 'V'" and the separate
    # read + "результат содержит" forms transpile to read_form_value with the field marker.
    combined = transpile_scenario("s", ["значение поля 'PF_EDIT_STRING' содержит 'PF_EDIT_STRING_VALUE'"])
    step = combined.scenario.steps[0]
    assert step.kind == "read_form_value"
    assert step.marker == "PF_EDIT_STRING"
    assert step.expect_contains == "PF_EDIT_STRING_VALUE"
    assert combined.unmapped == []

    separate = transpile_scenario("s", [
        "я читаю значение поля 'PF_EDIT_STRING'",
        "результат содержит 'PF_EDIT_STRING_VALUE'",
    ])
    assert separate.scenario.steps[0].kind == "read_form_value"
    assert separate.scenario.steps[0].expect_contains == "PF_EDIT_STRING_VALUE"
    assert separate.unmapped == []


def test_select_row_without_target_defaults_to_identity() -> None:
    result = transpile_scenario("s", ["я выбираю строку 'Средний'"])
    step = result.scenario.steps[0]
    assert step.params == {"old_value": "Средний", "new_value": "Средний"}


def test_unmapped_assertion_without_prior_step() -> None:
    result = transpile_scenario("s", ["результат содержит 'X'"])
    assert result.scenario.steps == []
    assert result.unmapped == ["результат содержит 'X'"]


def test_english_keywords_and_read_element() -> None:
    result = transpile_scenario("s", ["When я читаю элемент 'PF_FIELD_VERSION'"])
    assert result.scenario.steps[0].kind == "read_element"
    assert result.scenario.steps[0].marker == "PF_FIELD_VERSION"


def test_gherkin_to_runner_end_to_end_offline() -> None:
    # transpile a read-only feature, then drive it through the runner with a fake session
    from tests.test_scenario_runner import FakeBootstrapSession  # reuse the fake
    from qa_mcp.scenario import ScenarioRunner

    feature = """# language: ru
Сценарий: чтение
  Дано я читаю активное окно
  Тогда результат содержит 'HomePage'
  И я читаю сводку формы
  Тогда результат содержит 'PF_TABLE_ITEMS'
"""
    result = transpile_feature(feature)[0]
    assert result.unmapped == []
    session = FakeBootstrapSession()
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        runner = ScenarioRunner(
            session_factory=lambda: session, bootstrap=object(), templates=object(), output_dir=d, synthesized=object()
        )
        run = runner.run_single_session(result.scenario)
    assert run.passed
    assert [s.kind for s in result.scenario.steps] == ["read_active_window", "read_form_summary"]


def test_open_create_form_step_maps_document_and_catalog() -> None:
    # Card 106 change 4: «я создаю новый …» -> open_create_form (a NEW-object create form).
    lines = [
        "Когда я создаю новый документ 'Заказ'",
        "И я создаю новый элемент справочника 'Валюты'",
    ]
    r = transpile_scenario("create", lines)
    assert r.unmapped == [], r.unmapped
    assert [s.kind for s in r.scenario.steps] == ["open_create_form", "open_create_form"]
    assert r.scenario.steps[0].marker == "Заказ" and r.scenario.steps[0].params["object_type"] == "документ"
    assert r.scenario.steps[1].marker == "Валюты"
    assert r.scenario.steps[1].params["object_type"] == "элемент справочника"


def test_multiple_examples_blocks_skip_each_header() -> None:
    feature = """# language: ru
Функционал: примеры

  Структура сценария: открыть <Документ>
    Дано Я открываю основную форму документа '<Документ>'

    Примеры:
      | Документ |
      | Заказ |

    Примеры:
      | Документ |
      | Оплата |
"""
    results = transpile_feature(feature)
    assert [r.scenario.name for r in results] == ["открыть Заказ", "открыть Оплата"]
    assert all(r.unmapped == [] for r in results)
    assert [r.scenario.steps[0].marker for r in results] == ["Заказ", "Оплата"]


def test_escaped_pipe_stays_inside_table_cell() -> None:
    feature = """# language: ru
Функционал: таблицы

  Сценарий: escaped pipe
    И таблица 'ФайлыСервера' содержит строки:
      | Имя | Значение |
      | a\\|b | c |
"""
    result = transpile_feature(feature)[0]
    assert result.unmapped == []
    assert result.scenario.steps[0].params["table"] == [["Имя", "Значение"], ["a|b", "c"]]


def test_docstring_is_reported_unmapped_not_executed() -> None:
    feature = '''# language: ru
Функционал: docstring

  Сценарий: unsupported pystring
    Дано я читаю активное окно
    """
    я нажимаю на кнопку с именем 'НЕ_ИСПОЛНЯТЬ'
    """
    И я читаю сводку формы
'''
    result = transpile_feature(feature)[0]
    assert [s.kind for s in result.scenario.steps] == ["read_active_window", "read_form_summary"]
    assert result.unmapped == ["unsupported docstring block"]


def test_open_external_epf_step() -> None:
    # Card 109: «я открываю внешнюю обработку или отчет "<path>" (Расширение)» — the corpus residual, now mapped.
    lines = [
        'И я открываю внешнюю обработку или отчет "/opt/1c-dev/x/ВыгрузкаДвижений.epf" (Расширение)',
        "И я открываю внешнюю обработку или отчет 'C:/tmp/Отчет.erf'",  # no mode, single quotes, .erf
    ]
    r = transpile_scenario("epf", lines)
    assert r.unmapped == [], r.unmapped
    assert [s.kind for s in r.scenario.steps] == ["open_external_epf", "open_external_epf"]
    assert r.scenario.steps[0].marker == "/opt/1c-dev/x/ВыгрузкаДвижений.epf"
    assert r.scenario.steps[0].params["mode"] == "Расширение"
    assert r.scenario.steps[1].marker == "C:/tmp/Отчет.erf"
    assert r.scenario.steps[1].params["mode"] == ""
