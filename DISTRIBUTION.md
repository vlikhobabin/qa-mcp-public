# Локальный дистрибутив ChangeRail

Помимо runtime-копии поддержано подключение общего рабочего checkout командами
`attach-inventory`, `attach`, `detach`. Режим `--development` открывает тесты
через ссылки. Контракт и восстановление описаны в
[shared-source.md](https://github.com/vlikhobabin/changerail/blob/v2.0.0-rc.3/docs/shared-source.md).
Copy-install поверх подключённых ссылок запрещён.

Этот комплект содержит общий native runtime. Версия `2.0.0-rc.3`
обозначает предварительную версию для испытаний перед стабильным выпуском.
Поле `provenance.upstream_commit` в `distribution.json` обозначает историческую
базу исходника, а не Git-коммит этого выпуска. Точные release commit и tree
записаны в отдельном asset `release-provenance.json`; SHA-256 каждого файла
и совокупный hash идентифицируют точные байты кандидата. Публикация и release tag
не выполняются командами этого комплекта.

Ядро, адаптеры OpenSpec/Codex/pytest, схемы, навыки и выбранные README вместе
с этим документом входят в один архив. Каталог `docs/` и корневой README
остаются в исходном репозитории: для первого запуска используйте
[quickstart](https://github.com/vlikhobabin/changerail/blob/v2.0.0-rc.3/docs/quickstart.md),
для эксплуатации — [руководство оператора](https://github.com/vlikhobabin/changerail/blob/v2.0.0-rc.3/docs/operations.md).
Тесты ChangeRail/OpenSpec, тестовые launchers и фикстуры также остаются
в исходном репозитории ChangeRail. Runtime-архив их не устанавливает;
разработчик может открыть их через `attach --development`.
Профиль `.changerail/profile.toml`, продуктовые файлы, локальные
настройки Codex, credentials, runtime evidence и `node_modules` в архив не входят.
Установщик не редактирует профиль проекта и не запускает модель, тесты продукта,
bootstrap зависимостей, commit или push.

## Сборка и проверка

```sh
./bin/chrl-dist build /tmp/changerail-native-candidate.tar.gz
./bin/chrl-dist verify /tmp/changerail-native-candidate.tar.gz
```

Сборка использует явную выборку из `distribution.json`, фиксирует порядок файлов,
режим исполнимости и детерминированные метаданные tar/gzip. Повторная сборка
неизменного исходника совпадает побайтно. Существующий архив не перезаписывается.
Проверка читает ограниченные по размеру обычные файлы; ссылки, traversal,
дубликаты и несовпадение hash отклоняются. Проверка integrity не заменяет доверие
к источнику архива: источник кандидата и полученный SHA-256 следует проверять отдельно.

## Установка и обычное обновление

Цель — корень Git-репозитория с игнорируемым `.runtime/`. В новом проекте сначала
добавьте `.runtime/` в `.gitignore`; создайте отдельный проектный профиль.

Команды ниже используют доступный checkout инструмента; замените путь своим.
Текущий каталог не влияет на выбор потребителя, поскольку цель передана явно.

```sh
chrl_source=/path/to/changerail
python3 "$chrl_source/distribution.py" install \
  /tmp/changerail-native-candidate.tar.gz /opt/example-project --dry-run
python3 "$chrl_source/distribution.py" install \
  /tmp/changerail-native-candidate.tar.gz /opt/example-project
```

Lock `.changerail/distribution-lock.json` содержит версию, происхождение и hash
каждого установленного файла. Обычное обновление сначала проверяет всю предыдущую
выборку. Изменённый или удалённый локально файл блокирует установку. Идентичная
повторная установка ничего не записывает. Профиль проекта остаётся отдельным.
Вся замена проверяется до первой записи; замещаемые и удаляемые файлы сохраняются
под `.runtime/changerail/distribution/<archive-sha256>/before/`, рядом с audit.
Установщик удерживает тот же `.runtime/changerail/delivery.lock`, что и runner,
на протяжении проверки и замены. Живой writer или второй установщик блокирует
операцию, включая dry-run и явно разрешённое сохранение истории. Dry-run может
создать только каталог lock и сам lock; исходники и receipts он не меняет.
Запись каждого файла атомарна. При перехваченной ошибке установка восстанавливает
прежние bytes, режимы и lock, удаляет созданные файлы и сохраняет audit
`rolled_back`. Если восстановление невозможно, audit сообщает `rollback_failed`.
При SIGKILL или отключении питания audit может остаться `prepared`: файловая
система не предоставляет транзакцию на весь комплект. Автоматический повтор
такой попытки запрещён. Audit-каталог сохраняет владельца попытки даже после
`rolled_back`; поддерживаемой команды автоматического восстановления или очистки
попытки нет. Не удаляйте audit и не редактируйте lock ради повтора. Сначала
сохраните backup и фактическое состояние, затем выполните разбор по
[аварийному runbook](https://github.com/vlikhobabin/changerail/blob/v2.0.0-rc.3/docs/operations.md#незавершённая-установка-или-подключение).

Любой неучтённый сохранённый run блокирует замену кода; совпадения только
`execution_contract` недостаточно для совместимости frozen process. Точное
повторное применение того же payload допустимо для текущего native run.
Исторические runs сохраняются без записи и не получают нового права resume.
Инвентаризация читает только непосредственные `run.json` из контуров ChangeRail
`runs`, `delivery-runs`, `ff-runs` и `offline-finalizations`; продуктовые runtime
каталоги остаются вне этой операции.

Для обновления после новых доставок оператор может явно перевести точные
сохранённые runs в читаемую историю. Это решение не выводится из одного поля
`completed`: сначала завершите или остановите соответствующие процессы и
проверьте inventory. Разрешение связано с текущим lock, новым архивом и hash
всех runs; старые hash установленных исходников остаются обязательными.

```sh
python3 "$chrl_source/distribution.py" history /tmp/changerail-next.tar.gz \
  /opt/example-project --output /tmp/update-history.json
python3 "$chrl_source/distribution.py" install /tmp/changerail-next.tar.gz \
  /opt/example-project --history /tmp/update-history.json --dry-run
python3 "$chrl_source/distribution.py" install /tmp/changerail-next.tar.gz \
  /opt/example-project --history /tmp/update-history.json
```

Ранее сохранённая история не может исчезнуть или измениться при таком переходе.
Разрешение истории не обходит delivery lock и не разрешает продолжение старых runs.

Для stopped native run с точным drift принятого Next есть отдельный
[plan restoration](https://github.com/vlikhobabin/changerail/blob/v2.0.0-rc.3/docs/operations.md#восстановление-принятого-next):
prepare связывает lineage, прежний проверенный payload и точный target archive,
apply выполняет установку под тем же разрешением и восстанавливает Next.
Только этот ограниченный переход даёт право продолжить поддержанную installed
lineage; он не переводит read-only историю обратно в исполняемую. Незавершённый
restoration intent блокирует обычные installer и shared-source writers до
согласования того же apply.

## Первое принятие прежней локальной реализации

Это отдельная hash-bound операция. Подготовьте явный список принадлежащих старому
ChangeRail файлов: по одному относительному пути на строку. В него можно включить
старые тесты ChangeRail для удаления после сохранения backup. Не включайте
продуктовые файлы, профиль, runtime, `node_modules` или секреты.

```sh
python3 "$chrl_source/distribution.py" inventory /tmp/changerail-native-candidate.tar.gz \
  /opt/example-project --paths-file /tmp/predecessor-paths.txt \
  --retain-history-read-only --output /tmp/adoption.json
python3 "$chrl_source/distribution.py" install /tmp/changerail-native-candidate.tar.gz \
  /opt/example-project --adoption /tmp/adoption.json --dry-run
python3 "$chrl_source/distribution.py" install /tmp/changerail-native-candidate.tar.gz \
  /opt/example-project --adoption /tmp/adoption.json
```

Перед применением проверьте `adoption.json` и dry-run: разрешение связано с точным
целевым каталогом, архивом и hash каждого predecessor-файла. Опция
`--retain-history-read-only` явно фиксирует сохранённые `run.json` как историю;
она не изменяет receipts, не возобновляет доставку и не переносит review allowance.
Изменение run после подготовки inventory блокирует применение.
Отдельного `--force` нет.

## OpenSpec

Комплект включает pinned `package.json`, lockfile и локальный wrapper OpenSpec.
Зависимости не упаковываются и не загружаются автоматически. При наличии tarballs
в локальном npm cache оператор выполняет `tools/openspec/bootstrap.sh --offline`.
При отсутствии зависимости wrapper завершает работу с диагностикой; сетевого
fallback нет. Для проекта проверяются локальный профиль, OpenSpec config,
доступность CLI командой `./bin/chrl wiring`. Обновление проверяет хеши файлов;
полный набор тестов ChangeRail в потребителе не запускается и не входит в его CI.

Разработка и проверка ChangeRail выполняются в исходном репозитории, из каталога
корня checkout. Следующая команда предназначена только для этого исходника:

```sh
python3 -m pytest -q tools/changerail/tests/test_distribution.py
```
