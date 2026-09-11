#!/usr/bin/env python3
"""Build a narrow live manager harness for focused V2 safe actions."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

from v2_safe_action_tooling import (
    MANAGER_MANIFEST_SCHEMA,
    MANAGER_RESULT_SCHEMA,
    PHASE_EVENTS_SCHEMA,
    RAW_OUTPUT_POLICY,
    RUNNER_RESULTS_SCHEMA,
    V2_SAFE_ACTION_SCENARIO,
)


SUPPORTED_ACTIONS = {
    "safe-switch-fixture-page-b": {
        "family": "switch_fixture_page",
        "target_marker": "PF_PAGES_MAIN",
    },
    "safe-focus-existing-edit-string": {
        "family": "focus_existing_element",
        "target_marker": "PF_EDIT_STRING",
    },
}
SUPPORTED_FAMILIES = sorted({row["family"] for row in SUPPORTED_ACTIONS.values()})
FIXTURE_FORM_TITLE = "QA MCP Protocol Fixture V1"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8",
    )


def bsl_string(value: Any) -> str:
    return '"' + str(value).replace('"', '""') + '"'


def bsl_array(name: str, values: Iterable[Any]) -> list[str]:
    lines = [f"{name} = Новый Массив;"]
    for value in values:
        lines.append(f"{name}.Добавить({bsl_string(value)});")
    return lines


def executable_items(validation: dict[str, Any]) -> list[dict[str, Any]]:
    return [item for item in validation.get("rows", []) if item.get("executable")]


def reviewed_live_commands(validation: dict[str, Any]) -> list[dict[str, Any]]:
    commands: list[dict[str, Any]] = []
    for item in executable_items(validation):
        row = dict(item.get("row") or {})
        action_id = str(row.get("action_id") or item.get("action_id") or "")
        family = str(row.get("allowed_action_family") or item.get("allowed_action_family") or "")
        target_marker = str(row.get("target_marker") or item.get("target_marker") or "")
        supported = SUPPORTED_ACTIONS.get(action_id)
        if not supported:
            raise ValueError(f"live_runner_action_not_allowlisted:{action_id}")
        if family != supported["family"]:
            raise ValueError(f"live_runner_family_mismatch:{action_id}:{family}!={supported['family']}")
        if target_marker != supported["target_marker"]:
            raise ValueError(
                f"live_runner_target_marker_mismatch:{action_id}:{target_marker}!={supported['target_marker']}"
            )
        if row.get("mutates_business_data") is not False:
            raise ValueError(f"live_runner_mutation_not_allowed:{action_id}")
        commands.append(row)
    if not commands:
        raise ValueError("live_runner_no_executable_rows")
    return commands


def append_json_line_block(struct_name: str, path_name: str, suffix: str) -> list[str]:
    return [
        f"ЗаписьJSON{suffix} = Новый ЗаписьJSON;",
        f"ЗаписьJSON{suffix}.УстановитьСтроку();",
        f"ЗаписатьJSON(ЗаписьJSON{suffix}, {struct_name});",
        f"СтрокаJSON{suffix} = ЗаписьJSON{suffix}.Закрыть();",
        f"СтрокаJSON{suffix} = СтрЗаменить(СтрокаJSON{suffix}, Символы.ПС, \"\");",
        f"СтрокаJSON{suffix} = СтрЗаменить(СтрокаJSON{suffix}, Символы.ВК, \"\");",
        f"ЗаписьТекста{suffix} = Новый ЗаписьТекста({path_name}, КодировкаТекста.UTF8, , Истина);",
        f"ЗаписьТекста{suffix}.ЗаписатьСтроку(СтрокаJSON{suffix});",
        f"ЗаписьТекста{suffix}.Закрыть();",
    ]


def write_event_block(
    command: dict[str, Any],
    phase: str,
    status: str,
    result_preview_expr: str | None = None,
    action_result_markers: Iterable[str] | None = None,
    recovery_result_expr: str | None = None,
) -> list[str]:
    markers = list(action_result_markers or [])
    lines = [
        "Событие = Новый Структура;",
        f"Событие.Вставить(\"schema\", {bsl_string(PHASE_EVENTS_SCHEMA)});",
        "Событие.Вставить(\"run_id\", RunID);",
        f"Событие.Вставить(\"scenario\", {bsl_string(V2_SAFE_ACTION_SCENARIO)});",
        f"Событие.Вставить(\"phase\", {bsl_string(phase)});",
        f"Событие.Вставить(\"status\", {bsl_string(status)});",
        "Событие.Вставить(\"timestamp\", Формат(ТекущаяУниверсальнаяДата(), \"ДФ=yyyy-MM-ddTHH:mm:ss\") + \"Z\");",
        f"Событие.Вставить(\"case_id\", {bsl_string(command.get('case_id') or command.get('action_id'))});",
        f"Событие.Вставить(\"action_id\", {bsl_string(command.get('action_id'))});",
        f"Событие.Вставить(\"target_id\", {bsl_string(command.get('target_id'))});",
        f"Событие.Вставить(\"target_marker\", {bsl_string(command.get('target_marker'))});",
        f"Событие.Вставить(\"allowed_action_family\", {bsl_string(command.get('allowed_action_family'))});",
        "Событие.Вставить(\"proxy_testclient_port\", ProxyPort);",
        "Событие.Вставить(\"tcp_marker_policy\", \"side_channel_only_no_tcp_markers\");",
    ]
    if result_preview_expr:
        lines.append(f"Событие.Вставить(\"result_preview\", Лев(Строка({result_preview_expr}), 1000));")
    else:
        lines.append("Событие.Вставить(\"result_preview\", \"\");")
    if markers:
        lines += bsl_array("МаркерыСобытия", markers)
        lines.append("Событие.Вставить(\"action_result_markers\", МаркерыСобытия);")
    else:
        lines.append("Событие.Вставить(\"action_result_markers\", Новый Массив);")
    if recovery_result_expr:
        lines.append(f"Событие.Вставить(\"recovery_result\", {recovery_result_expr});")
    lines += append_json_line_block("Событие", "EventsPath", "События")
    lines += append_json_line_block("Событие", "CaseEventsPath", "СобытияCase")
    return lines


def wait_next_second_block() -> list[str]:
    return [
        "СекундаGuard = Формат(ТекущаяУниверсальнаяДата(), \"ДФ=yyyyMMddHHmmss\");",
        "Пока Формат(ТекущаяУниверсальнаяДата(), \"ДФ=yyyyMMddHHmmss\") = СекундаGuard Цикл",
        "\tСекундаGuard = СекундаGuard;",
        "КонецЦикла;",
    ]


def find_fixture_form_block() -> list[str]:
    title = bsl_string(FIXTURE_FORM_TITLE)
    return [
        "АктивноеОкноКоманды = ТестируемоеПриложениеКлиента.ПолучитьАктивноеОкно();",
        "ТестируемаяФормаКоманды = Неопределено;",
        "Если АктивноеОкноКоманды <> Неопределено Тогда",
        "\tПопытка",
        f"\t\tТестируемаяФормаКоманды = АктивноеОкноКоманды.НайтиОбъект(Тип(\"ТестируемаяФорма\"), {title}, , 15);",
        "\tИсключение",
        "\t\tТестируемаяФормаКоманды = Неопределено;",
        "\tКонецПопытки;",
        "КонецЕсли;",
        "Если ТестируемаяФормаКоманды = Неопределено Тогда",
        f"\tТестируемаяФормаКоманды = ТестируемоеПриложениеКлиента.НайтиОбъект(Тип(\"ТестируемаяФорма\"), {title}, , 15);",
        "КонецЕсли;",
        "Если ТестируемаяФормаКоманды = Неопределено Тогда",
        "\tВызватьИсключение \"fixture form not found\";",
        "КонецЕсли;",
    ]


def open_fixture_bootstrap_block() -> list[str]:
    title = bsl_string(FIXTURE_FORM_TITLE)
    return [
        "МаркерФормыBootstrap = Ложь;",
        "Попытка",
        f"\tМаркерФормыBootstrap = ТестируемоеПриложениеКлиента.ОжидатьОтображениеОбъекта(Тип(\"ТестируемаяФорма\"), {title}, , 3);",
        "Исключение",
        "\tМаркерФормыBootstrap = Ложь;",
        "КонецПопытки;",
        "Если МаркерФормыBootstrap = Ложь Тогда",
        "\tОкноПриложенияBootstrap = ТестируемоеПриложениеКлиента.НайтиОбъект(Тип(\"ТестируемоеОкноКлиентскогоПриложения\"), \"Демонстрационное приложение\", , 15);",
        "\tЕсли ОкноПриложенияBootstrap = Неопределено Тогда",
        "\t\tВызватьИсключение \"bootstrap app window not found\";",
        "\tКонецЕсли;",
        "\tОкноПриложенияBootstrap.Активизировать();",
        "\tКомандныйИнтерфейсBootstrap = ОкноПриложенияBootstrap.ПолучитьКомандныйИнтерфейс();",
        "\tКнопкаРазделаBootstrap = КомандныйИнтерфейсBootstrap.НайтиОбъект(Тип(\"ТестируемаяКнопкаКомандногоИнтерфейса\"), \"Предприятие\", , 15);",
        "\tЕсли КнопкаРазделаBootstrap = Неопределено Тогда",
        "\t\tВызватьИсключение \"bootstrap section button not found\";",
        "\tКонецЕсли;",
        "\tКнопкаРазделаBootstrap.Нажать();",
        "\tКомандныйИнтерфейсBootstrap = ОкноПриложенияBootstrap.ПолучитьКомандныйИнтерфейс();",
        "\tКнопкаФикстурыBootstrap = КомандныйИнтерфейсBootstrap.НайтиОбъект(Тип(\"ТестируемаяКнопкаКомандногоИнтерфейса\"), \"Фикстура протокола TestClient\", , 15);",
        "\tЕсли КнопкаФикстурыBootstrap = Неопределено Тогда",
        "\t\tВызватьИсключение \"bootstrap fixture command button not found\";",
        "\tКонецЕсли;",
        "\tКнопкаФикстурыBootstrap.Нажать();",
        "КонецЕсли;",
        f"МаркерФормыBootstrap = ТестируемоеПриложениеКлиента.ОжидатьОтображениеОбъекта(Тип(\"ТестируемаяФорма\"), {title}, , 15);",
        "Если МаркерФормыBootstrap = Ложь Тогда",
        "\tВызватьИсключение \"bootstrap fixture form marker not found\";",
        "КонецЕсли;",
    ]


def common_recovery_result_block(command: dict[str, Any], status: str, rationale: str) -> list[str]:
    recovery = command.get("recovery_expectation") if isinstance(command.get("recovery_expectation"), dict) else {}
    route = recovery.get("route") or command.get("recovery_expectation") or ""
    markers = recovery.get("expected_markers")
    if not isinstance(markers, list):
        marker = recovery.get("expected_marker") if isinstance(recovery, dict) else None
        markers = [marker] if marker else []
    lines = [
        "РезультатВосстановления = Новый Структура;",
        f"РезультатВосстановления.Вставить(\"status\", {bsl_string(status)});",
        f"РезультатВосстановления.Вставить(\"route\", {bsl_string(route)});",
        "РезультатВосстановления.Вставить(\"live_recovery_executed\", Истина);",
        f"РезультатВосстановления.Вставить(\"known_state_rationale\", {bsl_string(rationale)});",
    ]
    lines += bsl_array("МаркерыВосстановления", markers)
    lines.append("РезультатВосстановления.Вставить(\"expected_recovery_markers\", МаркерыВосстановления);")
    return lines


def write_runner_result_block(
    command: dict[str, Any],
    status: str,
    status_reason_expr: str,
    live_action_executed_expr: str,
    action_result_markers: Iterable[str] | None = None,
    recovery_result_expr: str | None = None,
) -> list[str]:
    markers = list(action_result_markers or [])
    lines = [
        "РезультатРаннера = Новый Структура;",
        f"РезультатРаннера.Вставить(\"schema\", {bsl_string(RUNNER_RESULTS_SCHEMA)});",
        "РезультатРаннера.Вставить(\"run_id\", RunID);",
        f"РезультатРаннера.Вставить(\"scenario\", {bsl_string(V2_SAFE_ACTION_SCENARIO)});",
        f"РезультатРаннера.Вставить(\"case_id\", {bsl_string(command.get('case_id') or command.get('action_id'))});",
        f"РезультатРаннера.Вставить(\"action_id\", {bsl_string(command.get('action_id'))});",
        f"РезультатРаннера.Вставить(\"target_id\", {bsl_string(command.get('target_id'))});",
        f"РезультатРаннера.Вставить(\"target_marker\", {bsl_string(command.get('target_marker'))});",
        f"РезультатРаннера.Вставить(\"allowed_action_family\", {bsl_string(command.get('allowed_action_family'))});",
        f"РезультатРаннера.Вставить(\"status\", {bsl_string(status)});",
        f"РезультатРаннера.Вставить(\"status_reason\", {status_reason_expr});",
        "РезультатРаннера.Вставить(\"candidate_only\", Истина);",
        "РезультатРаннера.Вставить(\"accepted_protocol_mapping\", Ложь);",
        f"РезультатРаннера.Вставить(\"live_action_executed\", {live_action_executed_expr});",
    ]
    lines += bsl_array("МаркерыРаннера", markers)
    lines.append("РезультатРаннера.Вставить(\"action_result_markers\", МаркерыРаннера);")
    if recovery_result_expr:
        lines.append(f"РезультатРаннера.Вставить(\"recovery_result\", {recovery_result_expr});")
    lines += append_json_line_block("РезультатРаннера", "RunnerResultsPath", "РезультатаРаннера")
    return lines


def switch_fixture_page_block(command: dict[str, Any]) -> list[str]:
    markers = command.get("expected_action_result_markers") or []
    lines: list[str] = []
    lines += find_fixture_form_block()
    lines += [
        "ГруппаСтраницКоманды = ТестируемаяФормаКоманды.НайтиОбъект(Тип(\"ТестируемаяГруппаФормы\"), , \"PF_PAGES_MAIN\", 15);",
        "Если ГруппаСтраницКоманды = Неопределено Тогда",
        "\tВызватьИсключение \"pages group PF_PAGES_MAIN not found\";",
        "КонецЕсли;",
        "ТекущаяСтраницаКоманды = Неопределено;",
        "Попытка",
        "\tТекущаяСтраницаКоманды = ГруппаСтраницКоманды.ПолучитьТекущуюСтраницу();",
        "Исключение",
        "\tТекущаяСтраницаКоманды = Неопределено;",
        "КонецПопытки;",
        "РезультатPreviewКоманды = \"pre_read=PF_PAGES_MAIN;current_page=\" + Строка(ТекущаяСтраницаКоманды);",
    ]
    lines += write_event_block(command, "pre_read", "success", "РезультатPreviewКоманды")
    lines += wait_next_second_block()
    lines += write_event_block(command, "action_start", "started", None)
    lines += [
        "СтраницаBКоманды = ТестируемаяФормаКоманды.НайтиОбъект(Тип(\"ТестируемаяГруппаФормы\"), , \"PF_PAGE_B\", 15);",
        "Если СтраницаBКоманды = Неопределено Тогда",
        "\tВызватьИсключение \"page PF_PAGE_B not found\";",
        "КонецЕсли;",
        "СтраницаBКоманды.Активизировать();",
        "ЖивоеДействиеВыполненоКоманды = Истина;",
        "РезультатPreviewКоманды = \"activated=PF_PAGE_B;target=PF_PAGES_MAIN\";",
    ]
    lines += write_event_block(command, "action_end", "success", "РезультатPreviewКоманды", markers)
    lines += wait_next_second_block()
    lines += [
        "ТекущаяСтраницаКоманды = Неопределено;",
        "Попытка",
        "\tТекущаяСтраницаКоманды = ГруппаСтраницКоманды.ПолучитьТекущуюСтраницу();",
        "Исключение",
        "\tТекущаяСтраницаКоманды = Неопределено;",
        "КонецПопытки;",
        "РезультатPreviewКоманды = \"post_read=PF_PAGE_B;current_page=\" + Строка(ТекущаяСтраницаКоманды);",
    ]
    lines += write_event_block(command, "post_read", "success", "РезультатPreviewКоманды", markers)
    lines += wait_next_second_block()
    lines += write_event_block(command, "recovery", "started", None)
    lines += [
        "СтраницаAКоманды = ТестируемаяФормаКоманды.НайтиОбъект(Тип(\"ТестируемаяГруппаФормы\"), , \"PF_PAGE_A\", 15);",
        "Если СтраницаAКоманды = Неопределено Тогда",
        "\tВызватьИсключение \"page PF_PAGE_A not found\";",
        "КонецЕсли;",
        "СтраницаAКоманды.Активизировать();",
        "РезультатPreviewКоманды = \"recovered=PF_PAGE_A\";",
    ]
    lines += common_recovery_result_block(command, "known_state_restored", "live recovery activated fixture page A")
    lines += write_event_block(command, "recovery_read", "success", "РезультатPreviewКоманды", None, "РезультатВосстановления")
    lines += write_runner_result_block(
        command,
        "success",
        bsl_string("live dispatcher executed switch_fixture_page and recovery"),
        "ЖивоеДействиеВыполненоКоманды",
        markers,
        "РезультатВосстановления",
    )
    return lines


def focus_existing_element_block(command: dict[str, Any]) -> list[str]:
    markers = command.get("expected_action_result_markers") or []
    lines: list[str] = []
    lines += find_fixture_form_block()
    lines += [
        "ПолеКоманды = ТестируемаяФормаКоманды.НайтиОбъект(Тип(\"ТестируемоеПолеФормы\"), , \"PF_EDIT_STRING\", 15);",
        "Если ПолеКоманды = Неопределено Тогда",
        "\tВызватьИсключение \"field PF_EDIT_STRING not found\";",
        "КонецЕсли;",
        "ПредставлениеПоляКоманды = \"\";",
        "Попытка",
        "\tПредставлениеПоляКоманды = ПолеКоманды.ПолучитьПредставлениеДанных();",
        "Исключение",
        "\tПредставлениеПоляКоманды = \"\";",
        "КонецПопытки;",
        "РезультатPreviewКоманды = \"pre_read=PF_EDIT_STRING;data=\" + ПредставлениеПоляКоманды;",
    ]
    lines += write_event_block(command, "pre_read", "success", "РезультатPreviewКоманды")
    lines += wait_next_second_block()
    lines += write_event_block(command, "action_start", "started", None)
    lines += [
        "ПолеКоманды.Активизировать();",
        "ЖивоеДействиеВыполненоКоманды = Истина;",
        "РезультатPreviewКоманды = \"activated=PF_EDIT_STRING;data=\" + ПредставлениеПоляКоманды;",
    ]
    lines += write_event_block(command, "action_end", "success", "РезультатPreviewКоманды", markers)
    lines += wait_next_second_block()
    lines += [
        "ПредставлениеПоляКоманды = \"\";",
        "Попытка",
        "\tПредставлениеПоляКоманды = ПолеКоманды.ПолучитьПредставлениеДанных();",
        "Исключение",
        "\tПредставлениеПоляКоманды = \"\";",
        "КонецПопытки;",
        "РезультатPreviewКоманды = \"post_read=PF_EDIT_STRING;data=\" + ПредставлениеПоляКоманды;",
    ]
    lines += write_event_block(command, "post_read", "success", "РезультатPreviewКоманды", markers)
    lines += wait_next_second_block()
    lines += write_event_block(command, "recovery", "started", None)
    lines += [
        "Попытка",
        "\tТестируемаяФормаКоманды.Активизировать();",
        "Исключение",
        "\tЕсли АктивноеОкноКоманды <> Неопределено Тогда",
        "\t\tАктивноеОкноКоманды.Активизировать();",
        "\tКонецЕсли;",
        "КонецПопытки;",
        "РезультатPreviewКоманды = \"recovered=PF_FORM_MAIN\";",
    ]
    lines += common_recovery_result_block(command, "known_state_restored", "live recovery activated the fixture form shell")
    lines += write_event_block(command, "recovery_read", "success", "РезультатPreviewКоманды", None, "РезультатВосстановления")
    lines += write_runner_result_block(
        command,
        "success",
        bsl_string("live dispatcher executed focus_existing_element and recovery"),
        "ЖивоеДействиеВыполненоКоманды",
        markers,
        "РезультатВосстановления",
    )
    return lines


def action_block(command: dict[str, Any]) -> list[str]:
    family = command.get("allowed_action_family")
    if family == "switch_fixture_page":
        return switch_fixture_page_block(command)
    if family == "focus_existing_element":
        return focus_existing_element_block(command)
    raise ValueError(f"unsupported_live_family:{family}")


def guarded_action_block(command: dict[str, Any]) -> list[str]:
    lines = [
        "ЖивоеДействиеВыполненоКоманды = Ложь;",
        "Попытка",
    ]
    lines += ["\t" + line if line else line for line in action_block(command)]
    lines += [
        "\tВыполнено = Выполнено + 1;",
        "Исключение",
        "\tОшибкаКоманды = ОписаниеОшибки();",
    ]
    failure_event = write_event_block(command, "recovery_read", "failed", "ОшибкаКоманды")
    failure_result = write_runner_result_block(
        command,
        "failed",
        "ОшибкаКоманды",
        "ЖивоеДействиеВыполненоКоманды",
        [],
        None,
    )
    lines += ["\t" + line if line else line for line in failure_event]
    lines += ["\t" + line if line else line for line in failure_result]
    lines += [
        "\tОшибок = Ошибок + 1;",
        "КонецПопытки;",
        *wait_next_second_block(),
    ]
    return lines


def live_step_text(commands: list[dict[str, Any]], run_id: str, output_dir: Path, proxy_port: int) -> str:
    lines = [
        f"RunID = {bsl_string(run_id)};",
        f"OutputDir = {bsl_string(str(output_dir))};",
        "EventsPath = OutputDir + \"/safe_action_phase_events.jsonl\";",
        "CaseEventsPath = OutputDir + \"/case_events.jsonl\";",
        "RunnerResultsPath = OutputDir + \"/safe_action_runner_results.jsonl\";",
        "ResultPath = OutputDir + \"/manager_harness_result.json\";",
        f"ProxyPort = {proxy_port};",
        f"КоличествоКоманд = {len(commands)};",
        "Выполнено = 0;",
        "Ошибок = 0;",
        "СтатусЗапуска = \"failed\";",
        "ПричинаСтатуса = \"not_completed\";",
        "ТестируемоеПриложениеКлиента = Неопределено;",
        "Попытка",
        "\tТестируемоеПриложениеКлиента = Новый ТестируемоеПриложение(\"127.0.0.1\", ProxyPort, \"\");",
        "\tТестируемоеПриложениеКлиента.УстановитьСоединение();",
    ]
    lines += ["\t" + line if line else line for line in open_fixture_bootstrap_block()]
    lines += ["\t" + line if line else line for line in wait_next_second_block()]
    for command in commands:
        lines += ["\t" + line if line else line for line in guarded_action_block(command)]
    lines += [
        "\tЕсли Ошибок = 0 Тогда",
        "\t\tСтатусЗапуска = \"ok\";",
        "\t\tПричинаСтатуса = \"all_live_safe_actions_completed\";",
        "\tИначеЕсли Выполнено > 0 Тогда",
        "\t\tСтатусЗапуска = \"partial\";",
        "\t\tПричинаСтатуса = \"some_live_safe_actions_failed\";",
        "\tИначе",
        "\t\tСтатусЗапуска = \"failed\";",
        "\t\tПричинаСтатуса = \"all_live_safe_actions_failed\";",
        "\tКонецЕсли;",
        "Исключение",
        "\tСтатусЗапуска = \"rejected\";",
        "\tПричинаСтатуса = ОписаниеОшибки();",
        "КонецПопытки;",
        "Если ТестируемоеПриложениеКлиента <> Неопределено Тогда",
        "\tПопытка",
        "\t\tТестируемоеПриложениеКлиента.РазорватьСоединение();",
        "\tИсключение",
        "\tКонецПопытки;",
        "КонецЕсли;",
        "РезультатЗапуска = Новый Структура;",
        f"РезультатЗапуска.Вставить(\"schema\", {bsl_string(MANAGER_RESULT_SCHEMA)});",
        "РезультатЗапуска.Вставить(\"run_id\", RunID);",
        f"РезультатЗапуска.Вставить(\"scenario\", {bsl_string(V2_SAFE_ACTION_SCENARIO)});",
        "РезультатЗапуска.Вставить(\"status\", СтатусЗапуска);",
        "РезультатЗапуска.Вставить(\"status_reason\", ПричинаСтатуса);",
        "РезультатЗапуска.Вставить(\"command_count\", КоличествоКоманд);",
        "РезультатЗапуска.Вставить(\"completed_count\", Выполнено);",
        "РезультатЗапуска.Вставить(\"failed_count\", Ошибок);",
        "РезультатЗапуска.Вставить(\"accepted_protocol_mapping\", Ложь);",
        "РезультатЗапуска.Вставить(\"live_action_executed\", Выполнено > 0);",
        "РезультатЗапуска.Вставить(\"raw_outputs_under_runtime\", Истина);",
        "РезультатЗапуска.Вставить(\"phase_events_path\", EventsPath);",
        "РезультатЗапуска.Вставить(\"case_events_path\", CaseEventsPath);",
        "РезультатЗапуска.Вставить(\"runner_results_path\", RunnerResultsPath);",
        "РезультатЗапуска.Вставить(\"finished_at\", Формат(ТекущаяУниверсальнаяДата(), \"ДФ=yyyy-MM-ddTHH:mm:ss\") + \"Z\");",
        "ЗаписьРезультата = Новый ЗаписьJSON;",
        "ЗаписьРезультата.ОткрытьФайл(ResultPath);",
        "ЗаписатьJSON(ЗаписьРезультата, РезультатЗапуска);",
        "ЗаписьРезультата.Закрыть();",
    ]
    return "И я выполняю код встроенного языка\n\"\"\"\n" + "\n".join(lines) + "\n\"\"\"\r\n"


def build_runner(validation_path: Path, output_dir: Path, run_id: str, proxy_port: int) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    validation = read_json(validation_path)
    commands = reviewed_live_commands(validation)

    manifest_path = output_dir / "manager_harness_manifest.json"
    invocation_path = output_dir / "manager_harness_invocation.json"
    step_path = output_dir / "manager_harness_invocation.feature.txt"
    events_path = output_dir / "safe_action_phase_events.jsonl"
    case_events_path = output_dir / "case_events.jsonl"
    runner_results_path = output_dir / "safe_action_runner_results.jsonl"

    manager_manifest = {
        "schema": MANAGER_MANIFEST_SCHEMA,
        "run_id": run_id,
        "scenario": V2_SAFE_ACTION_SCENARIO,
        "source_validation": str(validation_path),
        "dispatcher_mode": "live_manifest_gated_focused_rows",
        "supported_action_families": SUPPORTED_FAMILIES,
        "supported_action_ids": sorted(SUPPORTED_ACTIONS),
        "command_count": len(commands),
        "commands": commands,
        "raw_outputs_under_runtime": True,
        "tcp_marker_policy": "side_channel_only_no_tcp_markers",
        "raw_output_policy": RAW_OUTPUT_POLICY,
    }
    invocation = {
        "schema": "qa-mcp.manager-fixture-v2-safe-action.invocation.v1",
        "run_id": run_id,
        "scenario": V2_SAFE_ACTION_SCENARIO,
        "status": "prepared",
        "invocation_mode": "vanessa_mcp_execute_step_from_text_inline_bsl",
        "dispatcher_mode": "live_manifest_gated_focused_rows",
        "manifest_path": str(manifest_path),
        "manifest_validation_path": str(validation_path),
        "proxy_testclient_port": proxy_port,
        "output_dir": str(output_dir),
        "step_path": str(step_path),
        "phase_events_path": str(events_path),
        "case_events_path": str(case_events_path),
        "runner_results_path": str(runner_results_path),
        "accepted_protocol_mapping": False,
        "raw_outputs_under_runtime": True,
    }

    write_json(manifest_path, manager_manifest)
    write_json(invocation_path, invocation)
    write_jsonl(events_path, [])
    write_jsonl(case_events_path, [])
    write_jsonl(runner_results_path, [])
    step_path.write_text(live_step_text(commands, run_id, output_dir, proxy_port), encoding="utf-8")

    return {
        "manager_harness_manifest": str(manifest_path),
        "manager_harness_invocation": str(invocation_path),
        "manager_harness_step": str(step_path),
        "phase_events": str(events_path),
        "case_events": str(case_events_path),
        "runner_results": str(runner_results_path),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build",), nargs="?", default="build")
    parser.add_argument("--validation", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--proxy-port", required=True, type=int)
    parser.add_argument("--json", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = build_runner(
        args.validation.resolve(),
        args.output_dir.resolve(),
        args.run_id,
        args.proxy_port,
    )
    if args.json:
        print(json.dumps({"status": "ok", "output_files": result}, ensure_ascii=False, indent=2))
    else:
        print("status=ok")
        for key, value in result.items():
            print(f"{key}={value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
