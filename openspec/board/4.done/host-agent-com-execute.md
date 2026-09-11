# host-agent: операция `/com/execute` (проброс live COM на Windows-хост)

## Status
4.done

## OpenSpec Stage
archived

## Owner
qa-mcp — Windows host-agent (`host-agent/windows-display-agent/`, Go). Дочерняя
карточка root-координации `live-com-over-host-bridge` (контракт `windows-host-bridge`
класс `com_execute`). Парная реализация: live-mcp `com-remote-host-bridge-transport`.

## Source
- Релизный блокер: live-mcp в контейнере не может открыть файловую 1С-базу без
  Apache/OData. Решение — COM через тот же host-agent, что уже несёт `/platform/execute`
  и `/agent/complete`. См. root `openspec/board/1.backlog/live-com-over-host-bridge.md`.
- Прецедент: `/agent/complete` (`agent_cli.go`) — тот же паттерн allowlisted-операции
  (контейнер шлёт семантику, хост строит exec, `withAuth`, killgroup, fail-closed).

## Проблема
`V83.COMConnector` — Windows-only; live-mcp (Linux-контейнер) должен исполнять COM на
Windows-хосте. host-agent — единственный установленный на хосте компонент (Р6 «один
мост»). Нужна новая операция, которая принимает live-mcp `WorkerRequest` (JSON),
исполняет **замороженный питон-воркер live-mcp** `ai-com-worker.exe` и возвращает
`WorkerResponse` (JSON) без потерь.

## Дизайн
Новый handler `/com/execute`, зарегистрированный в `Handler()` (`main.go`) под
существующим `withAuth` (токен `X-QA-MCP-Agent-Token` + origin-allowlist + rate-limit +
sha-pin — переиспользуются). Handler:
1. `decodeJSON` тела (лимит поднять при необходимости — тело мало, но НЕ ограничивать
   ОТВЕТ воркера).
2. Валидация: `operation` ∈ allowlist `{ping, connect_check, execute_query,
   metadata_snapshot, guarded_posting_smoke}`; `guarded_posting_smoke` (единственная
   мутирующая) — gate по operator-intent, как `platform_command_execute` в
   `platform_exec.go` (иначе fail-closed).
3. `context.WithTimeout` (default/max как у platform), `exec.Command` на **фиксированный**
   установленный `ai-com-worker.exe --worker` (путь: install-dir рядом с
   `qa-mcp-host-agent.exe`, переопределяем env, напр. `QA_MCP_COM_WORKER_EXE`), `Stdin` =
   тело `WorkerRequest` (как `ComWorkerClient` кормит локальный subprocess),
   `configureProcessGroup` + `killProcessGroup` по timeout (как `runPlatformProcess`/
   `runCommandWithPromptOutput`).
4. **Полный UTF-8 passthrough:** воркер пишет `ensure_ascii=False`/`encoding=utf-8` →
   читать stdout как UTF-8 и вернуть **как есть** телом ответа. **НЕ** применять
   `maxPlatformOutputRunes=8192` truncation и **НЕ** применять CP866-fallback
   `decodePlatformOutput` (они порежут/испортят JSON результата запроса).
5. Ответ: пробросить `WorkerResponse` воркера (`{ok,requestId,result}` /
   `{ok:false,requestId,error:{code,message}}`). Если воркер не найден / упал до вывода /
   выдал не-JSON — обернуть secret-safe fail-closed (`writeError`).
6. **Безопасность:** тело `WorkerRequest` несёт `connection.password` (пароль инфобазы) и
   пути — **не логировать тело** (как `agent_cli` не логирует `prompt`); bounded/redacted
   диагностика в лог.

**Разделение ответственности:** контейнер НЕ шлёт путь/argv воркера — хост исполняет
фиксированный установленный exe. Никакой инъекции.

`/health` расширить COM-подпробой: присутствует ли `ai-com-worker.exe`, (опц.)
зарегистрирован ли `V83.COMConnector` — чтобы контейнер fail-closed'ил заранее (зеркалит
`platformCatalogHealth`/`agentCLIHealth`). Bump `AgentVersion` + sha-pin.

Windows-специфику (если понадобится вызов реестра для проверки регистрации ProgID)
держать за `//go:build windows` + `//go:build !windows` заглушкой, как `driver_windows.go`
/`driver_stub.go`; сам handler/exec — платформо-нейтральны (Linux-тестируемы через
fake-worker-стаб).

## Протокол (совпадает с live-mcp `WorkerRequest`/`WorkerResponse`)
Request `POST /com/execute` (тот же токен):
```json
{ "requestId":"<uuid>", "operation":"execute_query",
  "connection":{"connectionId":"demo10413","infobasePath":"C:\\1C_BASES\\demo10413",
    "username":"<user>","password":"<secret>","progId":"V83.COMConnector","timeoutSeconds":20},
  "payload":{"queryText":"...","parameters":{},"maxRows":1000}, "timeout_seconds":60 }
```
Response: `{ "ok":true, "requestId":"...", "result":{...} }` / fail-closed
`{ "ok":false, "requestId":"...", "error":{"code":"...","message":"..."} }`.

## Change Set (`$opsx-do`-исполним)
- `host-agent-com-execute-endpoint` — `openspec/changes/host-agent-com-execute-endpoint/`

### Change 1: `host-agent-com-execute-endpoint`
Capability (qa-mcp host-agent bridge). Реализовать всё выше:
- `main.go`: регистрация `/com/execute` в `Handler()`; новый файл `com_exec.go`
  (handler + exec-раннер с UTF-8 passthrough + allowlist + mutation-gate), по образцу
  `agent_cli.go`/`platform_exec.go` (типизированная ошибка `comExecError{status,code,detail}`,
  тонкий handler);
- `/health` COM-подпроба; `AgentVersion` bump + sha-pin в container-side
  `COMPATIBLE_HOST_AGENT_VERSIONS` (`src/qa_mcp/protocol/display_backend.py`, если версия
  сверяется);
- `install-windows-host-agent.ps1`: класть/находить `ai-com-worker.exe` (артефакт
  собирается в live-mcp), передавать путь (env/флаг) host-agent'у;
- тесты (Go, Linux-исполнимы через fake `ai-com-worker` стаб, печатающий заранее заданный
  `WorkerResponse`): valid-read-op→result проброшен целиком (в т.ч. большой UTF-8, не
  обрезан), unknown-operation→400, worker-missing→fail-closed, guarded_posting_smoke-без-
  intent→fail-closed, timeout→killgroup+504, invalid-token→401;
- README/`delivery/*` дельта: как устанавливается воркер и включается COM-провайдер.

> ≥1-capability: операция моста — часть host-bridge capability qa-mcp; schema-gate ок.

## Acceptance
- `/com/execute` под `withAuth`; allowlist operation; gate guarded_posting_smoke;
  полный UTF-8 результат воркера проброшен без truncation/перекодировки; тело (с паролем)
  не в логах; killgroup+timeout; `/health` репортит доступность COM-воркера.
- Все перечисленные тесты зелены (`go test ./...` в `windows-display-agent`).
- Демон собирается `GOOS=windows GOARCH=amd64 go build -ldflags "-H windowsgui"`.

## Preconditions / оговорки
- `ai-com-worker.exe` производится **live-mcp** (PyInstaller-цель в парной карточке) и
  отгружается вместе с host-agent; эта карточка потребляет его как установленный артефакт
  (тесты — через стаб, реальный exe связывается на install/E2E).
- Реальная COM-проверка (V83.COMConnector, x64, лицензия внешнего соединения) — на
  greenfield-боксе historical-user (см. root acceptance).

## Scope
- IN: handler `/com/execute`, exec-раннер (UTF-8 passthrough), allowlist+gate, `/health`
  подпроба, установка воркера инсталлятором, Go-тесты.
- OUT: сам питон-воркер и его заморозка (live-mcp); host-side пул COM-соединений
  (оптимизация позже); контракт-схемы/compose-wiring (root-карточка).

## Affected Repositories
- qa-mcp (host-agent Go + инсталлятор + тесты).

## Related
- root `openspec/board/1.backlog/live-com-over-host-bridge.md` (контракт + wiring).
- live-mcp `com-remote-host-bridge-transport` (парная реализация + `ai-com-worker.exe`).
- `host-agent/windows-display-agent/{main.go,agent_cli.go,platform_exec.go,
  process_group_windows.go}` (образцы).
- `openspec/changes/archive/2026-07-05-host-agent-com-execute-endpoint/`
- `.artifacts/openspec/host-agent-com-execute-endpoint/verification-summary.md`

## Archive
- `openspec/changes/archive/2026-07-05-host-agent-com-execute-endpoint/`

## Result
Implemented, verified and archived `host-agent-com-execute-endpoint`: host-agent
now exposes authenticated `/com/execute`, runs only the configured
`ai-com-worker.exe --worker`, validates the COM operation allowlist and guarded
posting operator intent, preserves UTF-8 worker JSON without platform-output
truncation/CP866 fallback, reports `com_worker` health, updates the installer
and docs, and bumps host-agent compatibility.

## Next
- none

## Log
- 2026-07-05T16:58:21Z OPSX pub: scoped commit prepared with message
  `feat(host-agent): add COM worker execute bridge`; final hash is recorded in
  the publish summary.
- 2026-07-05T16:58:21Z OPSX do: implemented `/com/execute`, passed Go/Python/OpenSpec
  validation, retained matrix evidence, archived
  `openspec/changes/archive/2026-07-05-host-agent-com-execute-endpoint/`, and
  moved card to `4.done`.
- 2026-07-05T16:45:48Z OPSX ff: created apply-ready change artifacts for
  `host-agent-com-execute-endpoint` and moved card to `2.todo`.
- 2026-07-05 карточка создана из root-координации `live-com-over-host-bridge` (Вариант A).
  Объём = 1 Go-handler `com_exec.go` (зеркало `agent_cli.go`, но полный UTF-8 passthrough)
  + `/health` подпроба + установка воркера. COM-инфраструктуры в host-agent сейчас нет
  (grep пустой) — операция чисто проксирующая, воркер несёт всю COM-логику.
