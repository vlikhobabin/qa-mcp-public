# read_list_grid/column: читать правильную таблицу формы + честная диагностика (P1)

## Status
4.done

## OpenSpec Stage
archived

## Owner
qa-mcp — MCP list-reading tools (`read_list_grid`, `read_list_column`). Источник:
фидбэк тестировщика `openspec/board/1.backlog/qa-mcp-install-test-report.md` §5, §7 (P1).

## Проблема (воспроизведено тестировщиком на стандартной БСП)
На форме списка `Справочник.Валюты` (DemoSSL, БСП 3.1.5, платформа 8.3.27.2130) UI и
host-agent `/screenshot` показывают **4 строки**, но `read_list_grid` возвращает
`row_count=0`, `rows=[]`, `table="Список"` и **опасно врёт** в `reason`: «0 rows … the
list is genuinely empty». Это ложь: список не пуст.

**Диагноз (из отчёта):**
- `read_list_grid`/`read_list_column`, вероятно, используют **жёстко зашитое имя таблицы
  `Список`**, а фактическая таблица формы списка справочника называется по объекту —
  `Валюты`.
- `read_form_descriptor(open_link="e1cib/list/Справочник.Валюты", enumerate_live=true)`
  **корректно** видит форму `Валюты` и в элементах `{ "kind":"Table", "name":"Валюты" }`.
- Обход работает: `read_table_cell(open_link=..., table="Валюты", column="НаименованиеПолное")`
  → `"Доллар США"`; `column="Код"` → `"840"`. Значит окно найдено, display bridge жив,
  данные в UI есть, база не пуста — дефект локализован в list/grid-инструментах.

## Ожидаемое поведение
- `read_list_grid`/`read_list_column` НЕ должны предполагать имя таблицы `Список`. Резолвить
  таблицу **через descriptor**: если у формы одна таблица — брать её; если несколько —
  выбирать основную таблицу списка (или принимать явный параметр `table`).
- Добавить необязательный параметр `table` (как у `read_table_cell`) для явного указания.
- **Честная диагностика:** если таблица не найдена / прочитана не та таблица —
  диагностировать это ОТДЕЛЬНЫМ статусом. НЕ утверждать «genuinely empty», пока не
  подтверждено, что читалась правильная таблица непустой формы. `reason` должен различать
  «таблица не разрешена / имя не совпало» и «форма реально пуста после refresh».

## Change Set (`$opsx-do`-исполним)

### Change 1: `list-read-table-resolution`
Capability: qa list-reading.
- в `read_list_grid`/`read_list_column`: убрать хардкод `Список`; резолвить таблицу через
  form descriptor (single-table → та таблица; multi → основная таблица списка), принять
  опциональный `table`;
- честный диагностический вывод (отдельный код при неразрешённой/неверной таблице; не
  «genuinely empty» без подтверждения правильной таблицы);
- тесты: на форме списка справочника (имя таблицы = имя объекта, не `Список`) grid читает
  строки; на форме, где таблица действительно `Список` — регресс не сломан; диагностика
  различает «wrong/unresolved table» vs «truly empty».

## Acceptance
- Мин. сценарий из отчёта §8: `read_list_grid(open_link="e1cib/list/Справочник.Валюты",
  columns=["НаименованиеПолное","Код","Наименование","Курс","Кратность"], max_rows=10,
  refresh=true)` возвращает **≥1 строку** (первая: `Доллар США`/`840`/`USD`), НЕ пустой
  список и НЕ «genuinely empty».
- `read_list_column` симметрично читает колонку.
- Диагностика при неразрешённой таблице честная (не «empty»).
- `go test`/`pytest` qa-mcp зелёные; регресс форм с таблицей `Список` не сломан.

## Preconditions / оговорки
- Проверка на реальной 1С — на Windows-боксе (TestClient). Юнит/логику резолва таблицы —
  локально.

## Scope
- IN: table-resolution + честная диагностика в `read_list_grid`/`read_list_column`.
- OUT: `read_table_cell`/`read_form_descriptor` current-form GUID (отдельная карточка
  ергономики); host-agent UTF-8 (отдельная карточка).

## Affected Repositories
- qa-mcp.

## Related
- `openspec/board/1.backlog/qa-mcp-install-test-report.md` §5, §7 (P1), §8 (repro).
- Обход-эталон: `read_table_cell(open_link, table='Валюты', column=...)`.
- `openspec/changes/archive/2026-07-05-list-read-table-resolution/`
- Delivery commit: `f9fd77ac217d3811d1c63978843d6efcc71fe6fc`

## Verify
- `openspec validate list-read-table-resolution --strict` — passed 2026-07-05T19:05:02Z.
- Matrix preflight — passed, 2026-07-05T19:23:42Z.
- `uv run pytest tests/test_form_descriptor.py -q` — 52 passed, 2026-07-05T19:21:56Z.
- `uv run pytest -q` — 700 passed, 2026-07-05T19:22:42Z.
- `uv run pytest -m smoke -q` — N/A in this repo: 700 deselected, 2026-07-05T19:21:56Z.
- Matrix archive gate — passed, retained under `.artifacts/openspec/list-read-table-resolution/20260705T1913Z/`.
- `openspec validate qa-mcp-tool-endpoint-contract --strict` — passed 2026-07-05T19:23:42Z.
- `openspec validate --all` — passed after archive, 19 items, 2026-07-05T19:23:42Z.
- `git diff --check` — passed.

## Archive
- `openspec/changes/archive/2026-07-05-list-read-table-resolution/`

## Result
Implemented and archived. `read_list_grid` and `read_list_column` now resolve the list table through the descriptor or an explicit `table` parameter, retarget the replay table segment, and return `list-table-*` diagnostics instead of claiming a wrong-table zero as genuinely empty.

## Next
- publish with `$opsx-pub openspec/board/4.done/list-read-correct-table-and-diagnostics.md`
- optional Windows/DemoSSL smoke can still be run against the tester's exact `Справочник.Валюты` contour for product acceptance evidence.

## Log
- 2026-07-05 карточка создана из отчёта тестировщика (P1). Главный продуктовый дефект
  standalone-релиза v0.2.3: list/grid читают хардкод-таблицу `Список` и ложно рапортуют
  пустой список для непустой формы.
- 2026-07-05T19:05:08Z `$opsx-ff`: created apply-ready OpenSpec artifacts and moved card to `2.todo`.
- 2026-07-05T19:15:37Z `$opsx-do`: implemented, verified, synced spec and archived `list-read-table-resolution`.
- 2026-07-05T19:26:00Z `$opsx-pub`: committed scoped delivery as `f9fd77ac217d3811d1c63978843d6efcc71fe6fc`.
