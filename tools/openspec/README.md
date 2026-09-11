# Локальная зависимость OpenSpec

Manifest и npm lockfile закрепляют **неизменённый OpenSpec 1.3.1**. `bin/openspec`
использует эту установку для канонической валидации и native lifecycle ChangeRail.
Уже зафиксированный run не может незаметно перейти на другую установку или процесс.

## Установка в выбранном проекте

Нужны Node.js >=20.19.0 и npm. Установку выполняет оператор отдельно от доставки,
в корне проекта-потребителя:

```sh
cd /opt/example-project
./tools/openspec/bootstrap.sh --offline
./bin/openspec --project /opt/example-project --version
```

Путь `/opt/example-project` произволен. При подключении общего исходника через
ссылки запускайте bootstrap по **пути потребителя**: `node_modules` создаётся
в его `tools/openspec`, а не в checkout инструмента. Установка в ChangeRail
нужна отдельно при разработке и проверке самого инструмента.

Bootstrap явно устанавливает закреплённое дерево из существующего npm cache,
пропускает lifecycle scripts и отключает audit/funding/update notifications.
`npm ci` заменяет только `node_modules` этой установки, не устанавливает глобальные
зависимости и отклоняет symlink в качестве каталога `node_modules`. Если tarballs
не закешированы, операция завершается ошибкой. Для первоначального сетевого
получения пакетов оператор может отдельно выполнить:

```sh
npm --prefix /opt/example-project/tools/openspec ci \
  --ignore-scripts --no-audit --no-fund \
  --logs-dir /opt/example-project/tools/openspec/npm-logs
/opt/example-project/bin/openspec --project /opt/example-project --version
```

Это отдельное решение об установке зависимостей; обычная доставка никогда
не выполняет такую команду автоматически. Сохраняйте `node_modules` и npm logs
в локальном Git ignore потребителя.

## Как wrapper выбирает проект

При первом аргументе `--project <каталог>` wrapper выбирает зависимости
`<каталог>/tools/openspec`, переходит в этот каталог проекта и передаёт оставшиеся
аргументы upstream CLI. Например, команда из любого рабочего каталога:

```sh
/opt/example-project/bin/openspec --project /opt/example-project \
  validate --specs --strict --no-interactive
```

Без `--project` рабочий каталог вызывающего процесса сохраняется. Зависимости
выбираются из `CHRL_PROJECT_ROOT`, если он установлен, иначе относительно пути
запущенного `bin/openspec`. Поэтому запуск wrapper инструмента из другого проекта
без явного выбора может совместить чужую зависимость и текущий cwd. Для работы
с определённым потребителем используйте `--project`; не полагайтесь на случайное
состояние окружения. Сам bootstrap флага `--project` не имеет.

Wrapper запускает только установленный
`tools/openspec/node_modules/@fission-ai/openspec/bin/openspec.js`, проверяет имя
и версию пакета и расположение entrypoint внутри локального дерева. При отсутствии
или несовпадении установки он завершается ошибкой. Он не вызывает `npx`,
не скачивает пакеты, не ищет глобальный OpenSpec и не использует cache как runtime
fallback. Набор зависимостей задаётся lockfile; для восстановления выполните
явную переустановку. Проверка при запуске не является аудитом целостности каждого
файла установленных зависимостей.

## Сеть и обновления

`OPENSPEC_TELEMETRY=0`, `DO_NOT_TRACK=1` и `CI=true` отключают telemetry upstream
1.3.1. Автоматическая настройка shell completions отключена, install scripts
пропускаются. Wrapper не обновляет OpenSpec и не генерирует агентские инструкции
автоматически; явно вызванные native-команды сохраняют свои штатные эффекты.

Переменные окружения и offline-установка npm не обеспечивают полную сетевую
изоляцию: Node, ОС и модельные сессии остаются самостоятельными границами доступа.
Registry URL в lockfile фиксируют происхождение пакетов и не требуют обращения
к registry при каждом запуске.

Обновление upstream требует изменения точного pin, пересоздания lockfile при явной
подготовке зависимостей, обновления compatibility check и проверки контрактов
адаптера. Не создавайте форк upstream schemas ради изменения статусов board.

## Проверка при разработке

Тесты wrapper принадлежат исходному репозиторию ChangeRail и не устанавливаются
в runtime-копии потребителей. При изменении wrapper запускайте из checkout
ChangeRail `node --test tools/openspec/test-wrapper.mjs`. Development-подключение
может открыть эти тесты через ссылки; runtime-архив их исключает.

При первоначальной изолированной проверке **2026-09-06** lockfile был сформирован
командой `npm install --package-lock-only --offline --ignore-scripts --no-audit
--no-fund`; registry download не потребовался. Offline-bootstrap установил 74
пакета из cache, CLI вернул `1.3.1`, прошли восемь Node contract tests и проверки
синтаксиса shell/JavaScript. Тест пустого cache получил ожидаемую ошибку npm.

Это историческое наблюдение, не результат проверки текущего checkout. Актуальные
результаты находятся в CI соответствующего commit и release notes. Тесты wrapper
не доказывают успешную модельную доставку, полную целостность установки или
отсутствие сетевых пакетов на уровне ОС.
