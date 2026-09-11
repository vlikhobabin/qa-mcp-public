# Client Fixture Processor Roadmap

Дата среза: 2026-06-09.

Этот документ фиксирует план развития клиентской внешней обработки/обработки
в базе `vanessa_client` для исследования native 1C TestClient protocol.
Речь идет только о функциональности самой обработки, а не о полном
Python/MCP/EDT конвейере.

## Цель

Обработка должна стать контролируемой TestClient fixture-поверхностью:
стабильная форма, стабильные элементы, стабильные маркеры `PF_*`, локальное
состояние и воспроизводимое поведение. Python-конвейер, TestManager harness,
TCP proxy, normalizer и replay/probe остаются вне обработки.

## Принципы

- Добавлять широкую поверхность контролов как можно раньше, чтобы не
  возвращаться к обработке за каждым новым семейством элементов.
- Держать V1 безопасной: максимум read-only поверхности и минимум поведения.
- Все элементы, значения, заголовки и состояния должны иметь уникальные
  `PF_*` маркеры для связи UI surface с frame ranges и corpus evidence.
- Все действия должны быть локальными, resettable и не зависеть от
  прикладных документов, справочников, регистров или внешних сервисов.
- Сокеты, TCP parsing, raw protocol decoding и accepted protocol mappings не
  реализуются внутри обработки.

## Версии Обработки

| Версия | Назначение | Оценка покрытия обработки |
| --- | --- | ---: |
| V1 | Широкая read-only/control fixture surface: основные контролы, маркеры, таблицы, страницы, команды, начальное состояние | 50-60% |
| V2 | Safe action surface: фокус, активация, переключение страниц, раскрытие групп/меню, выбор строки без бизнес-мутаций | 70-75% |
| V3 | Mutation sandbox: ввод, checkbox toggle, inert button click, локальный reset/rollback, проверяемые счетчики действий | 85-90% |
| V4 | Диалоги, предупреждения, ошибки, ожидания и recovery cases для сложных UI-сценариев | 95-100%; fixture-local/candidate-only delivered |

## V1: Control Surface

V1 должна создать почти полный каталог контролов, но только как стабильную
read-only и metadata-readable поверхность.

Ожидаемый состав:

- основная форма с маркерами `PF_FORM_MAIN` и `PF_FIXTURE_VERSION`;
- `EditField` variants: строка, число, дата, read-only, disabled;
- `CheckBox` variants: checked/unchecked/read-only/disabled;
- `RadioButton` или поле выбора со стабильным набором значений;
- `Button` variants: enabled, disabled, default, inert;
- `CommandBar` с обычной командой, disabled command и popup/group;
- `Table` с 2-3 стабильными строками и несколькими типами колонок;
- `Label`/decoration с уникальным текстом;
- `Group` variants: обычная, disabled, hidden planned marker;
- `Pages` с минимум двумя страницами и уникальными page markers;
- локальное состояние формы: `PF_LAST_ACTION`, `PF_ACTION_COUNTER`,
  `PF_SELECTED_ROW_MARKER`;
- команда `PF_RESET_STATE`, но в V1 она нужна прежде всего как future hook.

V1 не принимает protocol mappings для кликов, ввода и переключения страниц.
Эти элементы существуют для чтения свойств и подготовки будущих версий.

## V2: Safe Actions

V2 добавляет безопасные UI-действия без изменения бизнес-данных:

- установка фокуса на контрол;
- активация окна/формы;
- переключение страниц;
- раскрытие группы, popup или меню;
- выбор строки в локальной таблице;
- изменение только transient/local UI state;
- side markers до/после действия для будущей корреляции evidence.

V2 не выполняет бизнес-команды и не записывает данные.

## V3: Mutation Sandbox

V3 добавляет контролируемые мутации только внутри локального состояния формы:

- ввод текста в fixture-поле;
- изменение числа/даты в fixture-поле;
- toggle checkbox;
- inert button click;
- команды, меняющие только `PF_LAST_ACTION` и счетчики;
- reset/rollback всех локальных изменений;
- проверяемые expected markers после каждого действия.

V3 не пишет прикладные объекты и не зависит от бизнес-данных.

## V4: Dialogs And Recovery

V4 закрывает сложные UI-сценарии:

- предупреждения и вопросы;
- модальные формы/диалоги;
- ожидаемые ошибки;
- длительная операция с прогрессом/ожиданием;
- cancel/retry/recovery paths;
- негативные сценарии с фиксируемым результатом;
- восстановление формы в исходное состояние после каждого сценария.

V4 завершает план функциональности обработки. Дальнейшие изменения должны
быть точечными расширениями под новые классы платформенного API, а не
перепроектированием fixture-поверхности.

Состояние на 2026-06-09: V4 доставлена как fixture-local поверхность с
детерминированными `PF_V4_*` маркерами warning/question/modal lifecycle,
expected-error и bounded-wait сценариев. Runtime proof и manifest evidence
сохранены в `docs/protocol-research/evidence/client-fixture-v4-dialog-recovery/`.
Accepted protocol mappings для V4 не публикуются из этой поставки и остаются
заблокированы до V4-specific replay, direct Python-manager probe или typed
contract proof.

## Board Cards

План разбит на пять карточек в `openspec/board/`; часть карточек может быть
перемещена в `2.todo/` или `4.done/` по мере доставки:

- `01-2026-06-04-client-fixture-v1-control-surface.md`;
- `02-2026-06-04-client-fixture-v2-safe-actions.md`;
- `03-2026-06-04-client-fixture-v3-mutation-sandbox-surface.md`;
- `70-2026-06-08-client-fixture-v3-mutation-evidence-promotion.md`;
- `04-2026-06-04-client-fixture-v4-dialog-recovery.md`.
