# Инвентаризация тестов qa-mcp — 2026-09-10

Снимок обновлён после выполнения [плана T0–T5](test-improvement-plan.md) и
переноса четырёх subprocess-проверок выбора тестов при подготовке оркестратора.
[Отчёт о результатах](test-improvement-results.md) содержит назначения групп,
решения по повторам, исходные и итоговые измерения, сохранённые ошибки и ограничения.
[JSON-инвентарь](test-inventory.json) содержит хеш каждого Python/Go test-файла,
количество случаев, зависимости, контуры и совпадения тел функций.
Сбор инвентаря не выполняет тесты. Полного прогона и тестов ChangeRail не было.

## Состав

- Python: **1631 случай в 88 файлах с тестовыми случаями**.
- `offline`: **1617** случаев.
- `integration`: **14** случаев.
- Живые Linux/Windows 1C pytest: **0 зарегистрированных случаев**; это пробел runtime evidence, не successful proof.
- Go host-agent: **200 тестовых функций в 28 файлах**; **34** в Windows-only файлах. Числа не раскрывают Go subtests. Windows-only не означает обязательный живой запуск 1С.

История чисел: из прежних 2924 Python-случаев убраны 1276 ChangeRail и 27
board-helper. Продуктовая база составляла 1621 случай; девять проверок выбора
тестов дали снимок **1630 / 84 файла** на 2026-09-09. T0–T5 добавил один контроль
изоляции нового построителя: **1631 / 87 файлов**. Два остальных новых test-файла
получены переносом 11 прежних случаев из integration в offline. Существующие
продуктовые случаи при T0–T5 не удалялись.

Подготовка оркестратора сохранила все девять selector cases: пять чистых остались
offline, четыре с настоящими Git/pytest процессами перенесены в integration.
Добавлен один test-файл и общий builder; общее число случаев не изменилось.

## Решения и актуальность

| Наблюдение | Результат |
| --- | --- |
| 638 исторических финализаторных случаев повторяли Git/pytest цепочку | Это ChangeRail; его тесты исключены ранее, 11 CHRL-FIX карточек отменены |
| Два файла границы операций дают 408 + 116 = 524 случая | Все сохранены, включая точные 40 public URL cells: это требования текущих контрактов |
| `_encoded`, `_nested_arrays`, `_tar_bytes` совпадали между файлами | Общие `tests/support/boundary_inputs.py` и `tests/support/archives.py`; три группы дублирования устранены |
| Семь оставшихся совпадений — вложенные fake/handler методы | Оставлены локально: совпадение тела не гарантирует одинаковые замыкания |
| Повторялись profile/observation/env блоки | Три основных потребителя используют `TargetProfileInputs`; физические файлы и context/session/ledger остаются отдельными |
| `_settings`, `_context`, `_resolution` встречаются в разных файлах | Различающиеся небольшие wrappers сохранены. Общие mutable fixtures не введены; дополнительный lifecycle-кандидат относится к сохранённому FIX-02 |
| Bootstrap-тесты повторяли алгоритм выбора версии | Копия алгоритма удалена; проверки честно ограничены статическими declarations/wiring, не Windows execution |
| Документация проверялась по буквальным версиям и словам | Версии сверяются с двумя существующими baseline manifests; бессодержательные проверки двух слов удалены |
| Cleanup-тест ожидал успешный attach без target observation | Исправлена подготовка: задано ранее допущенное attachment; тест проверяет detach и отсутствие сигнала процессу |
| 11 чистых проверок находились в integration | Перенесены в два offline-файла без изменения тел; shell syntax, subprocess и builds оставлены отдельно |
| Четыре selector cases выполняли Git/pytest в offline | Перенесены в `tests/integration/test_test_selection_processes.py`; пять чистых selector cases оставлены offline, builder общий |
| Две artifact builds проверяют воспроизводимость | Обе сохранены. В T0–T5 этот неизменённый тест явно deselected, не объявлен пройденным |
| Release fixture строит настоящий host-agent | Session fixture переиспользуется; в каждом исходном/итоговом integration запуске выполнялась одна сборка |
| Часть corpus-тестов зависит от ignored captures | Skip означает отсутствие данных, а не runtime qualification |

Предыдущая инвентаризация также исправила hermetic screenshot-проверки,
перенесла реальный Xvfb в integration и переименовала локальный MCP subprocess
из `test_mcp_server_live.py` в `tests/integration/test_mcp_stdio.py`. Они не
являются живыми тестами 1С. Эта работа не меняла их повторно.

## Измерения и выбор

Итоговые затронутые пакеты: 550 boundary/context, 5 bootstrap/docs,
25 offline delivery/archive/selection и 7 integration — **587 различных
успешных случаев**. Точные команды, длительности pytest и команды целиком,
а также неуспешные предыдущие попытки приведены в [отчёте](test-improvement-results.md).
Сбор всех 1631 случаев для инвентаря — только collection.

408 core cases занимают около 0,70 с суммарного setup/call/teardown; 116 public
cases — около 8,47 с. Вся итоговая boundary/context команда с 550 случаями
заняла 22,42 с, pytest сообщил 17,50 с. Это измерения выбранных групп, а не
всего набора. Ускорение от переноса helpers/profile не подтверждено; уменьшены
повторы кода и улучшена классификация проверок.

Обычный выбор учитывает изменённые модули и затронутых потребителей,
раздельно offline/integration. Проверено, что изменения трёх общих support-модулей
выбирают все их текущие потребители. Крупный `mcp_server.py` сохраняет широкую
область зависимостей; её нельзя скрывать произвольным исключением тестов.
Полный набор допустим только перед закрытием эпика или по явному соглашению.
Правила: [test-policy.md](test-policy.md).

## Файлы Python

| Файл | Случаи | Функции test_* | Контур |
| --- | ---: | ---: | --- |
| `tests/integration/test_mcp_stdio.py` | 1 | 1 | integration |
| `tests/integration/test_screenshot_xvfb.py` | 1 | 1 | integration |
| `tests/integration/test_self_hosted_release_scripts.py` | 6 | 6 | integration |
| `tests/integration/test_windows_host_agent_artifact.py` | 2 | 2 | integration |
| `tests/test_assert_wait.py` | 13 | 13 | offline |
| `tests/test_autofill.py` | 12 | 12 | offline |
| `tests/test_bootstrap_platform_selection.py` | 3 | 3 | offline |
| `tests/test_bootstrap_synth.py` | 11 | 11 | offline |
| `tests/test_bundled_versions.py` | 22 | 19 | offline |
| `tests/test_capture_metadata.py` | 3 | 3 | offline |
| `tests/test_clean_tool_surface.py` | 2 | 2 | offline |
| `tests/test_com_host.py` | 5 | 5 | offline |
| `tests/test_compare_corpus_runs.py` | 14 | 14 | offline |
| `tests/test_compare_probe_reference.py` | 9 | 9 | offline |
| `tests/test_component_manifest.py` | 2 | 2 | offline |
| `tests/test_config.py` | 7 | 7 | offline |
| `tests/test_corpus_gate.py` | 4 | 4 | offline |
| `tests/test_coverage_report.py` | 4 | 4 | offline |
| `tests/test_data_layer_extras.py` | 10 | 10 | offline |
| `tests/test_delivery_config.py` | 3 | 3 | offline |
| `tests/test_direct_execute_receipt.py` | 28 | 9 | offline |
| `tests/test_display_backend.py` | 31 | 29 | offline |
| `tests/test_doctor.py` | 19 | 19 | offline |
| `tests/test_element_ref.py` | 15 | 15 | offline |
| `tests/test_form_descriptor.py` | 61 | 61 | offline |
| `tests/test_form_value_parser.py` | 16 | 16 | offline |
| `tests/test_free_startup.py` | 1 | 1 | offline |
| `tests/test_gates.py` | 12 | 12 | offline |
| `tests/test_host_agent_installer_contract.py` | 7 | 7 | offline |
| `tests/test_imports.py` | 1 | 1 | offline |
| `tests/test_lifecycle.py` | 29 | 29 | offline |
| `tests/test_manager_fixture_v1_report.py` | 12 | 12 | offline |
| `tests/test_manager_fixture_v2_safe_action_report.py` | 4 | 4 | offline |
| `tests/test_manager_handshake_drift.py` | 2 | 2 | offline |
| `tests/test_mcp_server.py` | 172 | 118 | offline |
| `tests/test_measure.py` | 9 | 9 | offline |
| `tests/test_multi_version_delivery_docs.py` | 2 | 2 | offline |
| `tests/test_mutation_render.py` | 3 | 3 | offline |
| `tests/test_native_mutation.py` | 9 | 9 | offline |
| `tests/test_native_write.py` | 69 | 69 | offline |
| `tests/test_native_xtest.py` | 21 | 21 | offline |
| `tests/test_navigation.py` | 21 | 21 | offline |
| `tests/test_odata.py` | 7 | 7 | offline |
| `tests/test_open_source_delivery.py` | 6 | 6 | offline |
| `tests/test_platform_support.py` | 13 | 13 | offline |
| `tests/test_positive_core_operation_boundary.py` | 408 | 42 | offline |
| `tests/test_positive_operation_boundary_integration.py` | 116 | 14 | offline |
| `tests/test_promote_member.py` | 2 | 2 | offline |
| `tests/test_protocol_contract.py` | 3 | 3 | offline |
| `tests/test_protocol_corpus_runner.py` | 6 | 6 | offline |
| `tests/test_protocol_extracted_helpers.py` | 5 | 5 | offline |
| `tests/test_protocol_primitives.py` | 4 | 4 | offline |
| `tests/test_protocol_session.py` | 6 | 6 | offline |
| `tests/test_protocol_tool_wrappers.py` | 4 | 4 | offline |
| `tests/test_public_repository_readiness.py` | 24 | 24 | offline |
| `tests/test_regression_harness.py` | 18 | 15 | offline |
| `tests/test_replay.py` | 2 | 2 | offline |
| `tests/test_reporting.py` | 8 | 8 | offline |
| `tests/test_runtime_target_adapter.py` | 48 | 25 | offline |
| `tests/test_runtime_target_contract.py` | 3 | 3 | offline |
| `tests/test_runtime_target_test_support.py` | 1 | 1 | offline |
| `tests/test_scenario_actions.py` | 18 | 18 | offline |
| `tests/test_scenario_gherkin.py` | 18 | 18 | offline |
| `tests/test_scenario_runner.py` | 39 | 39 | offline |
| `tests/test_scope_tracker.py` | 4 | 4 | offline |
| `tests/test_screenshot.py` | 6 | 6 | offline |
| `tests/test_self_hosted_release_contract.py` | 8 | 8 | offline |
| `tests/test_session_run_action.py` | 3 | 3 | offline |
| `tests/test_shared_core_extension.py` | 13 | 10 | offline |
| `tests/test_smoke_gen.py` | 4 | 4 | offline |
| `tests/test_standalone_host_bridge.py` | 8 | 3 | offline |
| `tests/test_standalone_http_delivery.py` | 4 | 4 | offline |
| `tests/test_step_library.py` | 5 | 5 | offline |
| `tests/test_target_bound_evidence_cleanup.py` | 25 | 12 | offline |
| `tests/test_target_bound_lifecycle_admission.py` | 42 | 16 | offline |
| `tests/test_telemetry_bridge.py` | 4 | 4 | offline |
| `tests/test_test_selection.py` | 9 | 8 | offline |
| `tests/test_testclient_relay_transport.py` | 5 | 4 | offline |
| `tests/test_v2_safe_action_live_runner.py` | 2 | 2 | offline |
| `tests/test_v2_safe_action_proof_summary.py` | 1 | 1 | offline |
| `tests/test_v2_safe_action_tooling.py` | 7 | 7 | offline |
| `tests/test_verify_open_image_archive.py` | 5 | 5 | offline |
| `tests/test_versioning.py` | 13 | 13 | offline |
| `tests/test_window_list.py` | 6 | 6 | offline |
| `tests/test_windows.py` | 6 | 6 | offline |
| `tests/test_windows_host_agent_artifact_contract.py` | 3 | 3 | offline |
| `tests/test_workspace_proof_receipts.py` | 11 | 7 | offline |

## Совпадения тел функций

- `tests/test_doctor.py:276:fake_run`; `tests/test_doctor.py:310:fake_run`
- `tests/test_doctor.py:340:com_probe`; `tests/test_doctor.py:371:com_probe`
- `tests/test_mcp_server.py:360:fake_run`; `tests/test_mcp_server.py:379:fake_run`
- `tests/test_native_mutation.py:97:poll`; `tests/test_native_mutation.py:123:poll`
- `tests/test_native_write.py:56:recv`; `tests/test_native_write.py:532:recv`
- `tests/test_native_write.py:424:recv`; `tests/test_native_write.py:480:recv`
- `tests/test_positive_operation_boundary_integration.py:157:handler`; `tests/test_positive_operation_boundary_integration.py:481:handler`

Статическое совпадение тела не доказывает семантическую избыточность.
Полная карта зависимостей и Go-инвентарь находятся в JSON.
