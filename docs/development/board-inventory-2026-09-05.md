# Инвентаризация доски после миграции ChangeRail

Дата: 2026-09-05. Основание: опубликованный upstream `8e94a21` и миграция
`f39e071`. Инвентаризация сопоставляет карточки с опубликованной Git-историей,
их Result/Next, преемниками и действующими ограничениями. Новых продуктовых
реализаций, runtime-проверок, verdict или переводов в done она не создаёт.

## Состав и готовность

На доске 226 карточек: 3 backlog, 11 todo, 4 inprogress, 192 done и 16 canceled.
Одноимённых дубликатов между колонками нет. Все 18 карточек из незавершённых
колонок рассмотрены ниже. Текущий admission возвращает `SPLIT_REQUIRED` для
каждой: старое размещение в todo не заменяет Delivery Budget и новый план.
Для исторических источников этот ответ не означает, что их нужно снова
декомпозировать или запускать.

| Фактическая категория | Количество | Действие |
| --- | ---: | --- |
| Исторические NO-GO / заменённые планы | 10 | Сохранить историю; исключить из очереди исполнения |
| Заблокированная runtime-квалификация | 3 | Не возобновлять без нового основания и отдельной runtime-авторизации |
| Родительские roadmap / release-gate записи | 2 | Поддерживать сводку; не передавать runner |
| Будущие истории / эпики | 3 | Планировать ограниченные карточки по зависимостям |

## Все незавершённые карточки

| Карточка | Колонка | Факт и следующий шаг |
| --- | --- | --- |
| [OSS-08](../../openspec/board/1.backlog/oss-08-publish-qa-mcp-github-ghcr-release-train.md) | backlog | Следующая история выпуска. OSS-03, OSS-05 и OSS-07-R1 опубликованы. Нужна декомпозиция: шесть acceptance-групп и Python/GHCR/Windows не укладываются в текущий admission. |
| [OSS-09](../../openspec/board/1.backlog/oss-09-cut-over-qa-mcp-public-stable-and-downstream.md) | backlog | Не начата; блокируется выпуском OSS-08 и отдельно принадлежащей downstream-работой. I16 уже фиксирует допустимый вариант omission. |
| [Runtime Proxy QA](../../openspec/board/1.backlog/product-v1-runtime-proxy-qa-execution.md) | backlog | Отдельный эпик, не часть публикации миграции. Нужны ограниченный первый этап и межкомпонентные договорённости. |
| [OSS-00](../../openspec/board/2.todo/oss-00-open-source-standalone-and-shared-core-roadmap.md) | todo | Roadmap. Обновлена сводка I16/OSS-07-R1 и направление на OSS-08; сам эпик не исполняется runner. |
| [OSS-04D](../../openspec/board/2.todo/oss-04d-propagate-target-session-operation-identity.md) | todo | Исторические исчерпанные NO-GO, не восстановление. Дальнейшая цепочка ограниченных преемников уже завершилась опубликованным R8. |
| [OSS-04D-R3](../../openspec/board/2.todo/oss-04d-r3-implement-typed-operation-evidence-boundary.md) | todo | Исчерпанная реализация; запрет повторной доставки. R4-R1 и дальнейшие преемники опубликованы. |
| [OSS-04D-R5](../../openspec/board/2.todo/oss-04d-r5-implement-core-operation-boundary.md) | todo | Исчерпанный NO-GO; stash только для истории. Цепочка R5-R2 → A4 → R7 → A5 → R8 завершена. |
| [OSS-04D-R5-R1](../../openspec/board/2.todo/oss-04d-r5-r1-investigate-exhausted-core-operation-boundary.md) | todo | Исчерпанное исследование; заменено R5-R2 и последующей опубликованной цепочкой. |
| [OSS-04D-A3](../../openspec/board/2.todo/oss-04d-a3-authorize-operation-boundary-integration.md) | todo | Авторизация заменена до доставки из-за NO-GO R5. Не является действующим разрешением; преемники A4/A5 опубликованы. |
| [OSS-04D-R6](../../openspec/board/2.todo/oss-04d-r6-integrate-operation-boundary-public-paths.md) | todo | План заменён до реализации. Фактическая интеграция принадлежит опубликованному R8. |
| [OSS-04E](../../openspec/board/2.todo/oss-04e-bind-testclient-lifecycle-admission.md) | todo | Исчерпанный NO-GO. Исправление принадлежит опубликованному OSS-04E-R1; старая карточка не очередь на ревью. |
| [OSS-06](../../openspec/board/2.todo/oss-06-stabilize-external-processor-open-flow.md) | todo | Родительская запись. I16 закрывает развилку выпуска через omission; runtime-квалификация дочерних карточек остаётся незавершённой. |
| [OSS-06-S4-R1](../../openspec/board/2.todo/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle.md) | todo | Заблокирована квалификация после I11. Offline-исправление не доказывает S3/S4/S5 и cleanup-матрицу. |
| [OSS-06-S7](../../openspec/board/2.todo/oss-06-s7-admit-hidden-direct-execute-public-route.md) | todo | Заблокирована I13 и S4-R1. I16 позволяет выпуск без S7; прежнее apply-ready не даёт нового права на доставку. |
| [OSS-06-S1](../../openspec/board/3.inprogress/oss-06-s1-extract-hidden-desktop-process-foundation.md) | inprogress | Исторический финальный NO-GO по доказательствам. Замена S1-R1 уже опубликована; повторная доставка исходной карточки запрещена. |
| [OSS-06-S5](../../openspec/board/3.inprogress/oss-06-s5-extract-prompt-admission-action.md) | inprogress | Исчерпанная остановленная реализация. Преемник S5-R1 опубликован; исходные native-ограничения и неуспешная cleanup-линия сохраняются. |
| [OSS-06-I13](../../openspec/board/3.inprogress/oss-06-s4-r1-i13-certify-published-i11-observation-lifecycle-evidence.md) | inprogress | `NOT-VERIFIABLE`; I15 не получил admission receipt и не запустил кандидата. I16 не завершает и не разрешает повтор I13. |
| [OSS-07](../../openspec/board/3.inprogress/oss-07-prepare-qa-mcp-public-repository-readiness.md) | inprogress | Неизменяемый исходный финальный NO-GO по записи преемника. Собственные Next/Stage устарели: повтор cycle 3 не требуется и не разрешён. Публикация принадлежит OSS-07-R1. |

## Опорные опубликованные результаты

- [OSS-04D-R8](../../openspec/board/4.done/oss-04d-r8-integrate-positive-operation-boundary-public-paths.md),
  commit `0bc7f45`: положительная интеграция границы операций.
- [OSS-04E-R1](../../openspec/board/4.done/oss-04e-r1-replace-exhausted-lifecycle-admission.md),
  commit `83d88eb`: замена lifecycle admission.
- [OSS-06-S1-R1](../../openspec/board/4.done/oss-06-s1-r1-certify-hidden-desktop-process-foundation.md),
  commit `8b329a2`, и
  [OSS-06-S5-R1](../../openspec/board/4.done/oss-06-s5-r1-replace-prompt-fingerprint-with-addressed-admission.md),
  commit `3a0e0f6`: опубликованные замены старых S1/S5.
- [I16](../../openspec/board/4.done/oss-06-s4-r1-i16-record-stable-profile-omission-after-i15.md),
  commit `10598ef`: omission из стабильной поверхности, без runtime-сертификации.
- [OSS-07-R1](../../openspec/board/4.done/oss-07-r1-replace-public-readiness-disclosure-and-evidence-integrity.md),
  commit `8e94a21`: опубликованная замена public-readiness payload.

Это проверка наличия опубликованных результатов, а не новое независимое ревью
их исходных payload. Некоторые финализированные карточки содержат старые
формулировки «awaiting review» перед завершающей записью публикации. История
done/canceled и её старые метрики не переписывались.

## Исправленные указатели и оставшиеся границы

Сверены 17 неразрешавшихся точных ссылок на карточки и две относительные
Markdown-ссылки. Ссылки на существующие карточки направлены в их фактические
колонки. Три межкомпонентных указателя теперь явно называют владельца и slug,
чтобы не трактоваться как карточки qa-mcp. В OSS-08/09 нормализован Depends On;
исчерпанный OSS-07 перенесён из обязательных зависимостей OSS-08 в Related.
Roadmap и OSS-06 больше не предлагают публиковать уже опубликованную I16 или
запускать прежний OSS-07.

Карточки не перемещались автоматически: это сохраняет пути неизменяемой
NO-GO-линии и не подменяет незавершённость статусом done/canceled. Четыре
inprogress по-прежнему блокируют обычный запуск runner. До реальной доставки
нужно отдельно определить представление исторических и приостановленных
карточек вне единственной активной полосы, затем принять ограниченный план.
Нельзя просто снять gate или объявить эти четыре карточки завершёнными.

Следующий содержательный этап — ограниченное планирование OSS-08. Runtime
квалификация I13/S4-R1/S7, публичный релиз и миграционный пилот не запускались.

Проверка инвентаризации: таблица покрывает ровно все 18 незавершённых карточек;
неразрешавшихся точных и относительных Markdown-ссылок больше нет; все три
Depends On у OSS-08 ведут в существующие опубликованные карточки `4.done`.
Десять тестов board helpers, local wiring, whitespace и public audit с I2
прошли. Legacy-файлы, продуктовый код и колонки done/canceled не изменялись.
