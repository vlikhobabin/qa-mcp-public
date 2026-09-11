# Отчет по установке и тестированию qa-mcp на Windows

## Board Status

Status: `4.done` / retained install-test evidence.

This report was triaged on 2026-07-06. Its actionable findings were split into
delivery cards and delivered:

- P1 list/grid table resolution: `openspec/board/4.done/list-read-correct-table-and-diagnostics.md`
  (`f9fd77a`).
- P2/P3 robustness, UTF-8, stale attachment and `/mcp` runbook fixes:
  `openspec/board/4.done/tester-feedback-robustness-and-utf8.md`
  (`f43e699`).
- Related host-agent display bridge findings: `openspec/board/4.done/host-agent-display-bridge-e2e-findings.md`.

No remaining item in this report should be executed from backlog. Keep it as
evidence of the 2026-07-05 Windows install test.

Дата проверки: 2026-07-05  
Релиз: `https://releases.aifor1c.ru:58443/qa-mcp/r-20260705-d855a405954d9c9d3395cb25`  
Версия qa-mcp из bootstrap: `v0.2.3`  
MCP server: `qa-native-manager 1.28.1`  
Образ: `qa-mcp-thin:v0.2.3`

## 1. Окружение

- ОС: Windows x64, build `22631`.
  - `Get-ComputerInfo` показывает `WindowsProductName = Windows 10 Pro`, `WindowsVersion = 2009`, `OsBuildNumber = 22631`.
  - По номеру сборки это Windows 11 23H2, но API/PowerShell отображает имя как Windows 10.
- Docker Desktop:
  - CLI: `Docker version 29.6.1`.
  - После ручного запуска Docker Desktop `docker info` стал отвечать.
  - Docker backend: WSL2, `Operating System: Docker Desktop`, `OSType: linux`, `Architecture: x86_64`.
- Установленные платформы 1С:
  - `C:\Program Files\1cv8\8.3.27.1786\bin\1cv8.exe`
  - `C:\Program Files\1cv8\8.3.27.2130\bin\1cv8.exe`
- Использованная платформа:
  - `C:\Program Files\1cv8\8.3.27.2130\bin\1cv8.exe`
  - Версия `8.3.27.2130`, то есть поддерживаемая runbook.
- Информационная база:
  - `C:\Users\User\Documents\1C\DemoSSL`
  - Пользователь: `Администратор`
  - Пароль: пустой
- Порты:
  - MCP: `8000`
  - host-agent: `8001`
  - TestClient: `15381`

## 2. Что прошло успешно

Установка bootstrap в целом завершилась успешно.

Команда запуска:

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\qa-mcp\bootstrap.ps1" `
  -Infobase "C:\Users\User\Documents\1C\DemoSSL" `
  -User "Администратор" `
  -PlatformExe "C:\Program Files\1cv8\8.3.27.2130\bin\1cv8.exe"
```

После диагностики заголовка окна был выполнен повторный запуск с явным `WindowTitle`:

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\qa-mcp\bootstrap.ps1" `
  -Infobase "C:\Users\User\Documents\1C\DemoSSL" `
  -User "Администратор" `
  -PlatformExe "C:\Program Files\1cv8\8.3.27.2130\bin\1cv8.exe" `
  -WindowTitle "3.1.5"
```

Проверки, которые прошли:

- `docker info` отвечает.
- Контейнер `qa-mcp` запущен и healthy.
- `host-agent` отвечает на `/version`.
- `tools/list` возвращает `63` инструмента.
- `attach_test_client` возвращает `attached=true`, `listening=true`.
- `infobase_info` возвращает:
  - `kind=thick`
  - `listening=true`
  - `platform_root=/opt/1cv8/x86_64/8.3.27.2130`
- Codex MCP-конфиг добавлен штатной командой:

```powershell
codex mcp add qa-mcp --url "http://127.0.0.1:8000/mcp" --bearer-token-env-var QA_MCP_BEARER_TOKEN
```

`codex mcp get qa-mcp` показывает:

- `enabled: true`
- `transport: streamable_http`
- `url: http://127.0.0.1:8000/mcp`
- `bearer_token_env_var: QA_MCP_BEARER_TOKEN`

Прямая проверка `tools/list` через этот URL подтвердила `63` инструмента, включая `attach_test_client` и `read_list_grid`.

## 3. Трудности при установке

### 3.1. Docker Desktop был установлен, но не запущен

Первичная проверка:

```powershell
docker --version
docker info
```

Результат:

- `docker --version` вернул `Docker version 29.6.1`.
- `docker info` вернул ошибку:

```text
ERROR: Error response from daemon: Docker Desktop is unable to start
```

Решение:

- Пользователь вручную запустил Docker Desktop.
- После этого `docker info` стал отвечать, установка была продолжена.

### 3.2. Пустой пароль нельзя передавать как `-Password ""`

Первая команда установки содержала:

```powershell
-Password ""
```

Bootstrap завершился ошибкой:

```text
Missing an argument for parameter 'Password'. Specify a parameter of type 'System.String' and try again.
```

Решение:

- При пустом пароле параметр `-Password` не передавался вообще.
- После этого bootstrap запустился успешно.

Предложение:

- Либо принять `-Password ""`, либо явно описать в runbook, что для пустого пароля параметр нужно опускать.

### 3.3. Расхождение между runbook и выводом bootstrap по пути MCP

Runbook говорит использовать:

```text
http://127.0.0.1:<McpPort>/mcp
```

Bootstrap напечатал:

```text
http://127.0.0.1:8000/mcp/
```

Проверка показала:

- `POST http://127.0.0.1:8000/mcp/` возвращает:

```json
{"error": "not_found"}
```

- `POST http://127.0.0.1:8000/mcp` работает, `initialize` проходит успешно.

Предложение:

- Исправить текст bootstrap: печатать `/mcp` без завершающего slash.
- Либо научить сервер принимать оба варианта.

### 3.4. Заголовок окна 1С определяется неустойчиво

При первом запуске bootstrap вывел:

```text
окно: Клиент тестирования
```

Но фактическое окно 1С имело заголовок:

```text
Версия 3.1.5 / Демонстрационная конфигурация "Библиотека стандартных подсистем", редакция 3.1
```

Из-за этого host-agent/display bridge сначала не мог корректно отправить F5 для обновления списка.

Симптом в `read_list_grid`:

```json
{
  "row_count": 0,
  "list_refresh": {
    "refresh": true,
    "method": "none",
    "poll_outcome": "timeout",
    "note": "F5 keystroke failed (no reachable display backend); list not force-refreshed"
  },
  "reason": "0 rows — a refresh was requested but no display backend was reachable..."
}
```

Решение:

- Bootstrap был перезапущен с:

```powershell
-WindowTitle "3.1.5"
```

После этого F5 начал доходить:

```json
{
  "list_refresh": {
    "refresh": true,
    "method": "f5",
    "poll_outcome": "stable"
  }
}
```

Предложение:

- Улучшить автоопределение окна.
- Если заголовок не найден или найден fallback `Клиент тестирования`, выводить предупреждение и предлагать `-WindowTitle`.
- Возможно, использовать PID запущенного `1cv8.exe`, а не только текстовый заголовок окна.

### 3.5. Mojibake в `window_list` host-agent

`host-agent /window_list` возвращал русские заголовки окон в mojibake, например:

```text
ÐÐµÑÑÐ¸Ñ 3.1.5 / ÐÐµÐ¼Ð¾Ð½ÑÑÑÐ°ÑÐ¸Ð¾Ð½Ð½Ð°Ñ...
```

При этом `Get-Process 1cv8 | Select MainWindowTitle` в PowerShell показывал нормальный русский заголовок.

Последствие:

- Автоматическое сопоставление окна по русскому заголовку ненадежно.
- Пришлось использовать ASCII-фрагмент `3.1.5`.

Предложение:

- Проверить кодировку ответа `window_list`.
- Для Windows отдавать строки в корректном UTF-8 JSON.

## 4. Трудности при тестировании MCP-инструментов

### 4.1. TestClient может перестать слушать порт, а контейнер хранит stale attachment

Позже во время проверки выяснилось:

- `Get-Process 1cv8` не находил процесс.
- `Get-NetTCPConnection -LocalPort 15381 -State Listen` ничего не возвращал.
- MCP-инструменты отвечали:

```json
{
  "error": "attached-testclient-unavailable",
  "detail": "attached TestClient endpoint host.docker.internal:15381 is not listening during descriptor",
  "attached_endpoint": {
    "attached": true,
    "listening": false
  }
}
```

То есть в контейнере оставалось `attached=true`, но фактически TestClient уже не слушал.

Решение:

```powershell
Start-ScheduledTask -TaskName "qa-mcp-testclient"
```

После запуска:

- порт `15381` снова слушал;
- `1cv8.exe` снова появился;
- `attach_test_client` снова вернул `attached=true`, `listening=true`.

Предложение:

- Инструменты должны явно инвалидировать attachment, если `listening=false`.
- `attach_test_client` или `test_client_status` могли бы предлагать/уметь перезапускать TestClient.
- В E2E runbook стоит добавить проверку `test_client_status` и/или `Get-NetTCPConnection` перед list/read тестами.

### 4.2. PowerShell может отправить кириллицу в JSON не как UTF-8

При первом вызове:

```json
{
  "open_link": "e1cib/list/Справочник.Валюты"
}
```

в ответе MCP было:

```json
{
  "nav_link": "e1cib/list/??????????.??????"
}
```

Решение:

- Отправлять тело запроса как UTF-8 bytes:

```powershell
$bytes = [System.Text.Encoding]::UTF8.GetBytes($body)
Invoke-RestMethod ... -Body $bytes -Headers @{ "Content-Type" = "application/json; charset=utf-8" }
```

После этого `nav_link` стал корректным:

```json
{
  "nav_link": "e1cib/list/Справочник.Валюты"
}
```

Предложение:

- В runbook для ручных PowerShell-вызовов добавить пример с UTF-8 bytes.

## 5. Основная найденная проблема: `read_list_grid` / `read_list_column`

### 5.1. Симптом

Список валют визуально содержит 4 строки:

- `Доллар США`, код `840`, симв. код `USD`
- `Евро`, код `978`, симв. код `EUR`
- `Российский рубль`, код `643`, симв. код `RUB`
- `Условная единица`, симв. код `YE`, помечена на удаление

При этом `read_list_grid` возвращает:

```json
{
  "table": "Список",
  "nav_link": "e1cib/list/Справочник.Валюты",
  "row_count": 0,
  "rows": [],
  "list_refresh": {
    "refresh": true,
    "method": "f5",
    "poll_outcome": "stable"
  },
  "reason": "0 rows after a forced list refresh + poll-until-stable and a clean-state sweep — the list is genuinely empty (refreshed)."
}
```

Это неверно: список не пустой.

### 5.2. Подтверждение через screenshot host-agent

Через `host-agent /screenshot` был получен снимок окна 1С. На нем виден список `Валюты` с 4 строками.

Значит:

- окно найдено;
- display bridge работает;
- данные в UI есть;
- проблема не в пустой базе.

### 5.3. `read_form_descriptor` видит правильную форму и элементы

Вызов:

```json
{
  "name": "read_form_descriptor",
  "arguments": {
    "open_link": "e1cib/list/Справочник.Валюты",
    "enumerate_live": true,
    "gherkin": false
  }
}
```

Результат:

```json
{
  "opened": "Валюты",
  "element_count": 59,
  "elements": [
    { "kind": "Table", "name": "Валюты" },
    { "kind": "EditField", "name": "НаименованиеПолное" },
    { "kind": "EditField", "name": "Код" },
    { "kind": "EditField", "name": "Наименование" },
    { "kind": "EditField", "name": "Курс" },
    { "kind": "EditField", "name": "Кратность" },
    { "kind": "EditField", "name": "Ссылка" }
  ]
}
```

Ключевой факт:

- Реальная таблица формы называется `Валюты`.
- `read_list_grid` в ответе пишет `table: "Список"` и, вероятно, пытается читать несуществующую или неправильную таблицу.

### 5.4. Рабочий обход через `read_table_cell`

Если явно передать `open_link`, фактическое имя таблицы и внутреннее имя колонки, чтение работает:

```json
{
  "name": "read_table_cell",
  "arguments": {
    "open_link": "e1cib/list/Справочник.Валюты",
    "table": "Валюты",
    "column": "НаименованиеПолное"
  }
}
```

Результат:

```json
{
  "opened": "Валюты",
  "table": "Валюты",
  "column": "НаименованиеПолное",
  "value": "Доллар США"
}
```

Также:

```json
{
  "name": "read_table_cell",
  "arguments": {
    "open_link": "e1cib/list/Справочник.Валюты",
    "table": "Валюты",
    "column": "Код"
  }
}
```

Результат:

```json
{
  "value": "840"
}
```

### 5.5. `read_table_cell` без `open_link` падает

Если вызывать `read_table_cell` на уже открытой форме без `open_link`, результат:

```json
{
  "ok": false,
  "error": "invalid-arguments",
  "phase": "table_read",
  "detail": "managed_form_guid_ascii template field requires a live ManagedForm GUID"
}
```

Если добавить `open_link`, тот же инструмент работает.

Предложение:

- Если текущая форма уже открыта, `read_table_cell` должен уметь получить live ManagedForm GUID.
- Или ошибка должна явно говорить: "передайте open_link".

### 5.6. `read_form_descriptor` без `open_link` тоже падает на текущей форме

Вызов:

```json
{
  "name": "read_form_descriptor",
  "arguments": {
    "enumerate_live": true,
    "gherkin": false
  }
}
```

Результат:

```json
{
  "ok": false,
  "error": "attached-descriptor-empty",
  "phase": "descriptor",
  "detail": "managed_form_guid_ascii template field requires a live ManagedForm GUID",
  "diagnostic": "attached endpoint was reachable and the descriptor call returned no opened form, fields or elements"
}
```

С `open_link` этот же инструмент работает.

Предложение:

- Аналогично: либо научиться читать текущую активную форму, либо документировать обязательность `open_link` для надежного чтения descriptor.

## 6. Проверка `read_record`

Вызов по ссылке пользователя:

```json
{
  "name": "read_record",
  "arguments": {
    "record_type": "Справочник.Валюты",
    "ref": "8c3608002700700111e1ca6cc5f6a3f2"
  }
}
```

Результат успешный:

```json
{
  "opened": "USD (Валюта)",
  "fields": {
    "НаименованиеПолное": "Доллар США",
    "Код": "840",
    "Наименование": "USD",
    "Наценка": "0",
    "ОсновнаяВалюта": "",
    "ФормулаРасчетаКурса": ""
  },
  "field_count": 10,
  "element_count": 37
}
```

Вывод:

- Доступ к 1С, TestClient, `e1cib/data/...`, чтение карточки и шаблоны карточек работают.
- Проблема локализована не в установке и не в базе, а в чтении списков/table grid.

## 7. Предполагаемые дефекты продукта

### P1. `read_list_grid` / `read_list_column` неверно возвращают пустой список

Факты:

- UI показывает 4 строки.
- host-agent screenshot показывает 4 строки.
- `read_form_descriptor(open_link=...)` видит форму и таблицу `Валюты`.
- `read_table_cell(open_link=..., table='Валюты', column=...)` читает значение первой строки.
- `read_list_grid` возвращает `row_count=0` и `table="Список"`.

Вероятная причина:

- `read_list_grid`/`read_list_column` используют жестко заданное имя таблицы `Список`.
- Для формы `Справочник.Валюты` фактическое имя таблицы `Валюты`.

Ожидаемое поведение:

- Либо инструмент должен принимать параметр `table`.
- Либо должен сначала делать descriptor и выбирать таблицу автоматически.
- Либо должен использовать таблицу из descriptor, если она одна.

### P1. `read_list_grid` формирует неверный диагностический вывод

Сейчас инструмент пишет:

```text
0 rows after a forced list refresh ... the list is genuinely empty
```

Это неверно и опасно для агента: список не пустой.

Ожидаемое поведение:

- Если таблица не найдена или прочитана не та таблица, диагностировать это отдельно.
- Не утверждать "genuinely empty", пока не подтверждено, что читается правильная таблица.

### P2. Инструменты зависят от `open_link` для ManagedForm GUID, но это неочевидно

Без `open_link`:

- `read_form_descriptor` падает с `managed_form_guid_ascii template field requires a live ManagedForm GUID`.
- `read_table_cell` падает с такой же ошибкой.

С `open_link`:

- оба инструмента работают.

Ожидаемое поведение:

- Либо поддержать чтение текущей активной формы.
- Либо сделать `open_link` обязательным в схеме для этих режимов.
- Либо дать понятную ошибку: "cannot infer current ManagedForm GUID; pass open_link".

### P2. `attached=true` может сохраняться при `listening=false`

Когда TestClient умер/остановился:

```json
{
  "attached": true,
  "listening": false
}
```

Ожидаемое поведение:

- Инструменты должны явно считать attachment недействительным.
- Хорошо бы давать action hint: "restart qa-mcp-testclient scheduled task".

### P3. Некорректный trailing slash в bootstrap output

Bootstrap печатает `/mcp/`, но сервер отвечает только на `/mcp`.

Ожидаемое поведение:

- Печатать `/mcp`.
- Или принимать оба URL.

### P3. Проблемы кодировки `window_list`

Русские заголовки окон возвращаются в mojibake.

Ожидаемое поведение:

- Возвращать корректный UTF-8 JSON.
- Это особенно важно для автоопределения `WindowTitle`.

## 8. Минимальный сценарий воспроизведения основной проблемы

1. Установить qa-mcp по runbook с платформой `8.3.27.2130`.
2. Запустить DemoSSL:

```powershell
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\qa-mcp\bootstrap.ps1" `
  -Infobase "C:\Users\User\Documents\1C\DemoSSL" `
  -User "Администратор" `
  -PlatformExe "C:\Program Files\1cv8\8.3.27.2130\bin\1cv8.exe" `
  -WindowTitle "3.1.5"
```

3. Проверить descriptor списка:

```json
{
  "name": "read_form_descriptor",
  "arguments": {
    "open_link": "e1cib/list/Справочник.Валюты",
    "enumerate_live": true,
    "gherkin": false
  }
}
```

Ожидаемый результат:

```json
{
  "opened": "Валюты",
  "elements": [
    { "kind": "Table", "name": "Валюты" }
  ]
}
```

4. Проверить `read_table_cell`:

```json
{
  "name": "read_table_cell",
  "arguments": {
    "open_link": "e1cib/list/Справочник.Валюты",
    "table": "Валюты",
    "column": "НаименованиеПолное"
  }
}
```

Фактический успешный результат:

```json
{
  "value": "Доллар США"
}
```

5. Проверить `read_list_grid`:

```json
{
  "name": "read_list_grid",
  "arguments": {
    "open_link": "e1cib/list/Справочник.Валюты",
    "columns": ["НаименованиеПолное", "Код", "Наименование", "Курс", "Кратность"],
    "max_rows": 10,
    "refresh": true
  }
}
```

Фактический неверный результат:

```json
{
  "table": "Список",
  "row_count": 0,
  "rows": [],
  "reason": "0 rows after a forced list refresh ... the list is genuinely empty"
}
```

Ожидаемый результат:

- 4 строки списка валют.
- Минимум первая строка:

```json
{
  "НаименованиеПолное": "Доллар США",
  "Код": "840",
  "Наименование": "USD"
}
```

## 9. Общий вывод

Установка qa-mcp в целом рабочая: Docker, host-agent, контейнер, TestClient, MCP tools/list, attach, infobase_info и чтение карточки записи через `read_record` работают.

Главная проблема обнаружена в инструментах чтения списков:

- `read_list_grid`
- `read_list_column`

Они возвращают пустой список для формы, где реальные строки есть. Диагностика показывает, что они читают таблицу `Список`, хотя фактическая таблица формы называется `Валюты`. Рабочий обход через `read_form_descriptor` + `read_table_cell(open_link, table='Валюты', column=...)` подтверждает, что данные доступны и проблема локализована в list/grid-инструментах.
