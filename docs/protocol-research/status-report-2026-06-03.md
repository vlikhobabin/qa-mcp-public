# Protocol Research Status Report

> **⚠ HISTORICAL (2026-06-03) — superseded.** An early protocol-decode snapshot, kept for provenance. For current
> state see `../qa-mcp-tool-reference.md` + `../program-102-native-superset-handoff.md` and the README banner.

Дата среза: 2026-06-03.

Этот отчет фиксирует фактическое состояние проекта `qa-mcp` после первых
циклов исследования native 1C TestManager/TestClient TCP-протокола. Оценка
сделана относительно цели: заменить Vanessa manager Python-реализацией,
которая может напрямую выполнять тестовые объекты и методы платформы 1C через
запущенный `/TESTCLIENT`.

## Executive Summary

Главный результат достигнут: доказано, что Python-код может напрямую говорить
с `/TESTCLIENT` без запуска 1C в режиме `/TestManager`. Мы прошли стадию
пассивного sniffing и получили первый воспроизводимый read-only Python manager
для ограниченной поверхности активного окна, активной формы и деталей двух
`EditField` элементов.

Как полная замена Vanessa проект пока находится на ранней стадии. Грубая
инженерная оценка:

- `6-8%` от полной замены Vanessa как runtime manager.
- `3-4%`, если считать только accepted protocol surface.
- `25-30%` по снижению исследовательского риска, потому что bootstrap,
  replayability, dynamic fields и прямой Python session API уже доказаны.

Эти проценты не являются метрикой покрытия API. Это рабочая оценка зрелости:
сколько уже можно использовать как подтвержденное знание и насколько снят риск
невозможности прямого взаимодействия с TestClient.

## Что Фактически Сделано

Собран Windows-native lab:

- запуск `/TESTCLIENT`;
- запуск Vanessa/TestManager через подготовленную manager base;
- TCP proxy для чистого application-level capture;
- capture/replay/probe tooling под `tools/protocol-research/`;
- raw runtime output под игнорируемым `runtime/protocol-research/`.

Получен и сохранен базовый capture:

- capture id: `20260602-084433`;
- `106` manager-to-client chunks;
- `107` client-to-manager chunks;
- compact evidence:
  `docs/protocol-research/evidence/captures/20260602-084433/`.

Расшифрована критичная часть bootstrap:

- TestClient preface: `53 f5 c6 1a 7b`;
- live ACK GUID после третьего кадра;
- подстановка ACK GUID в manager frame 4 и последующие binary frames;
- sequence в `uint16_le`;
- manager-generated nonce blocks и их echo в ответах;
- ManagedForm GUID в ASCII и UTF-16LE формах.

Построена template-модель manager frames:

- templates для frames `8..106`;
- dynamic fields: `ack_guid`, `sequence`, `nonce`,
  `managed_form_guid_ascii`, `managed_form_guid_utf16le`;
- template evidence:
  `docs/protocol-research/evidence/templates/20260602-frames08-106-utf16-managedform/`.

Реализован прямой Python manager API:

- package boundary: `src/qa_mcp/protocol/`;
- reusable entrypoint: `TestClientSession`;
- read-only methods:
  - `get_initial_ui_context`;
  - `get_active_window_context`;
  - `get_active_form_context`;
  - `get_form_summary`;
  - `get_form_element_details`.

Подтвержден короткий read-only schedule:

- full path: `1..106`;
- short path: `1..17,101..106`;
- TestClient принимает jump от frame 17 к frame 101;
- frames `31..100` можно пропустить для текущего element-detail query;
- compact probe evidence:
  `docs/protocol-research/evidence/python-manager-probe/short-element-details-20260602-151206/`.

Создан evidence/corpus pipeline:

- `protocol_corpus_runner.py`;
- `compare_corpus_runs.py`;
- normalizer evidence;
- accepted mapping reports;
- explicit gap rows for unsupported fixture families;
- safe-action evidence contract.

## Что Принято Как Рабочее Протокольное Знание

Accepted mappings сейчас ограничены двумя case ids:

| Case id | Status | Evidence |
| --- | --- | --- |
| `active-window-context` | accepted | repeated normalized hashes plus direct Python-manager probe |
| `active-form-context` | accepted | repeated normalized hashes plus direct Python-manager probe |

Accepted mapping evidence:
`docs/protocol-research/evidence/accepted-mappings/expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted/`.

Полезные, но еще не accepted descriptors:

| Descriptor | Current state | Reason |
| --- | --- | --- |
| `initial-ui` | partial | bootstrap context, not a standalone accepted mapping |
| `form-summary` | partial | probe path works, but no standalone accepted corpus row |
| `form-element-details` | incomplete_hash | useful direct probe exists, repeated reviewed request hashes are incomplete |
| `typed-input-field-readonly` | incomplete_hash | shares element-detail shape; operation join remains ambiguous |

Safe UI action layer не принят:

- `safe-activate-existing-window` captured as a candidate;
- classification: `pending`;
- missing action frame range, request frames, normalized hash and replay/probe
  proof;
- accepted safe-action mappings are empty.

Controlled fixture families не приняты:

- `Button`;
- `Table`;
- `CommandBar`;
- `Page`;
- `Label`;
- `CheckBox`.

Для них есть fixture plan и source candidates, но нет live wire evidence с
frame range, normalized hash и accepted replay/probe status.

## Насколько Далеко До Замены Vanessa

Если `100%` означает возможность выполнить любой тестовый код платформы 1C в
части объектов и методов, предназначенных для тестирования, то текущий прогресс
невелик. Мы закрыли не ширину API, а самую рискованную первую развилку:
доказали, что прямой manager вообще возможен.

Текущая зрелость по слоям:

| Layer | Estimate | Comment |
| --- | ---: | --- |
| Transport/session bootstrap for lab platform | 45-55% | Основные dynamic fields найдены, но frames `1..3` еще частично captured-derived |
| Read-only active window/form | 60-70% | Есть accepted mappings для текущей платформы и lab form |
| Read-only element details | 25-35% | Probe работает, accepted evidence еще неполное |
| Cross-element read-only coverage | 5-10% | Большинство element families пока fixture gaps |
| Safe non-mutating actions | 1-3% | Scope определен, первый capture не принят |
| Mutating actions/input/commands | 0-1% | Осознанно не начинали без recovery model |
| Error/timeout/recovery semantics | 0-5% | Пока почти не покрыто |
| Version/client-mode portability | 0-5% | Все доказательства привязаны к текущему Windows lab |

Итоговая оценка как замены Vanessa: `6-8%`.

## Скорость Прогресса

За период 2026-06-02 и 2026-06-03 выполнены десятки коротких OpenSpec/corpus
циклов и сформированы основные инфраструктурные артефакты:

- 7 reviewed corpus runs;
- 5 corpus comparison/classification runs;
- 4 compact Python-manager probe evidence directories;
- 3 accepted-mapping publication directories, из которых реальный accepted set
  есть только для read-only active window/form;
- 26 archived OpenSpec changes на момент среза.

Прогресс был быстрым в фазе снятия первичного риска: handshake, replay,
template rendering и Python session API появились за короткий период. После
этого скорость accepted coverage ожидаемо снизилась, потому что каждое новое
утверждение требует не просто capture, а повторяемой связки:

capture -> frame range -> dynamic-field normalization -> stable hash ->
replay/probe -> compact evidence.

Это замедляет delivery, но защищает проект от ложных protocol mappings.

## Оценка Текущего Подхода

Текущий подход эффективен для исследовательской фазы:

- он доказал возможность прямого Python manager;
- он отделяет wire evidence от semantic assumptions;
- он не повышает probe success до accepted mapping без reviewed hashes;
- он сохраняет gap rows вместо скрытого непокрытия.

Слабые места подхода:

- текущая активная форма слишком бедная: фактически два `EditField`;
- fixture discovery есть, но runner пока не умеет открыть нужную fixture form;
- evidence-gating создает заметную операционную нагрузку;
- safe-action traffic пока трудно отделять от фонового refresh;
- bootstrap все еще зависит от captured frames для ранних handshake шагов;
- pytest/dev environment должен быть установлен явно, иначе локальная проверка
  пропускает тесты.

Вывод: подход не нужно менять радикально. Нужно сменить фокус с одиночных
ручных открытий на контролируемый fixture-driven corpus.

## Рекомендованный Следующий Маршрут

1. Закрыть `form-element-details` как accepted mapping.

   Нужны повторные current comparison inputs, в которых `101..106` имеют
   ненулевые request bytes, stable normalized hash и accepted direct probe для
   той же operation shape.

2. Сделать управляемую fixture form в рабочей TestClient базе.

   Форма должна содержать `Button`, `Table`, `CommandBar`, `Page`, `Label`,
   `CheckBox`, `EditField` с уникальными response markers. Это важнее, чем
   новые action experiments, потому что без стабильной поверхности мы будем
   исследовать случайную демо-форму.

3. Расширить read-only dictionary по element families.

   Цель: свойства видимости, доступности, caption/value, структуры таблиц,
   страниц, command bar metadata. Без clicks, input и command execution.

4. Только после этого возвращаться к safe UI actions.

   Порядок: `focus_element`, `activate_window`, `switch_page`, `expand_menu`.
   Для каждой строки нужен separated action frame range и replay/probe proof.

5. Затем исследовать mutation layer.

   Текстовый ввод, выбор значения, нажатие кнопки и команда формы требуют
   отдельной rollback/recovery стратегии и контролируемой демо-базы.

## Ближайшие Инженерные Задачи

- Установить dev dependencies и сделать `pytest` обязательной локальной
  проверкой, а не опциональным пропуском.
- Добавить fresh live package smoke для `TestClientSession`, потому что
  текущая package promotion была verified offline.
- Исправить fixture targeting: runner должен уметь открыть выбранную форму,
  а не только анализировать текущий dashboard.
- Сформировать corpus manifest для controlled read-only fixture form.
- Повторить expanded-readonly capture так, чтобы element-detail rows получили
  accepted request-hash evidence.

## Evidence Pointers

- `docs/protocol-research/evidence-index.md`
- `docs/protocol-research/evidence/captures/20260602-084433/`
- `docs/protocol-research/evidence/templates/20260602-frames08-106-utf16-managedform/`
- `docs/protocol-research/evidence/python-manager-probe/short-element-details-20260602-151206/`
- `docs/protocol-research/evidence/accepted-mappings/expanded-readonly-20260602-193802-vs-20260602-195407-probe-accepted/`
- `docs/protocol-research/evidence/readonly-element-hash-resolution/20260603-incomplete-hash-with-extracted-request-evidence/`
- `docs/protocol-research/evidence/corpus-comparison/safe-action-20260603-134132/`
