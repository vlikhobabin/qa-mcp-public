# Standalone Windows bridge runbook

Этот runbook относится только к открытому bridge из `host-agent/`. Он не
устанавливает COM worker, BSL supervisor, agent CLI, Team/onboarding или
произвольный platform executor.

## Подготовка

1. Соберите и проверьте source-bound bundle командой
   `./bin/ai-build-windows-host-agent build`/`verify`.
2. На Windows сохраните токен только в ACL-защищённом файле.
3. Убедитесь, что пользовательская desktop session интерактивна, нужная версия
   1C установлена, а точная TestClient база доступна.
4. До запуска запишите PID/listener/task/Docker inventory. Не выводите
   credentials, connection strings, UI text или screenshots.

## Установка

```powershell
powershell -ExecutionPolicy Bypass -File .\install-windows-host-agent.ps1 `
  -ExePath .\qa-mcp-host-agent.exe `
  -BindAddress 0.0.0.0 `
  -RemoteAddress 192.168.65.0/24 `
  -TestClientRelayAddress 0.0.0.0:15382 `
  -PlatformCatalog 'C:\Program Files\1cv8'
```

Проверьте с заголовком `X-QA-MCP-Agent-Token`:

- `GET /v1/capabilities`: `api_major=1`, полный required capability set;
- `GET /health`: только desktop и TestClient relay state;
- удалённые product routes возвращают `404`.

Container получает `QA_MCP_HOST_AGENT=host.docker.internal:8001` и тот же
token через ignored secret configuration. Python-клиент обязан завершить
handshake до lifecycle/display вызова и не делает fallback на старые routes.
TestClient запускается только через `/testclient/launch`; полученный owned
`lifecycle_id`/PID/TPort обязателен для window-list, screenshot, UIA и input.
Явный window selector не даёт отдельной authority и не может подменить target.
Все эти handlers используют общий authenticated concurrency limit; N+1 должен
получить `429 execution-capacity-exhausted` до driver/process work.

## Native qualification

Используйте exact SHA-256 release executable. Докажите launch/status/relay,
реальный `TestClientSession.read_initial()` из standalone container, window
list, bounded type/click, screenshot SHA, visible-list UIA и exact stop.
Отдельно проверьте incompatible major, missing capability, wrong target,
locked/disconnected desktop, failed launch и повторный cleanup. Санитизированное
evidence не содержит UI text, raw screenshot, credentials или command line.

Cleanup разрешён только для exact-owned lifecycle PID/handle, scheduled task,
stage, tunnel и listeners текущего запуска. После cleanup сравните unrelated
1C/Docker inventory с preflight. Обычный `-Uninstall` без повторной передачи
relay address обязан прочитать owned relay port из install env и удалить его
точное firewall rule до удаления install state.
