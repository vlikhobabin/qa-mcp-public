# Host-agent display-мост: F5 keymap + version-handshake + cp866-вывод

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Source
- Whole-product full-10 E2E на Windows-боксе (historical-user, 2026-07-05): qa-mcp
  (Linux-контейнер, `QA_MCP_REMOTE_CLIENT=1`) успешно attach + `read_list_grid`
  Валюты (10 строк EUR/USD/Рубли) на demo10413 TestClient через host-agent
  display-мост — но всплыли три дефекта моста.
- Находки **H**, **I**, **L**.

## Summary
Три независимых дефекта host-agent (windows-display-agent), выявленных живым
E2E-прогоном:

- **H (version-handshake):** работающий host-agent `/version` =
  `0.1.0-platform-execute`, а qa-mcp пинит `HOST_AGENT_VERSION="0.1.0-card124"`
  (`protocol/display_backend.py`). `RemoteAgentBackend.handshake()` требует
  `version == expected_version` → mismatch → `DisplayBackendError` → любой
  keystroke падает как «no reachable display backend». В E2E обойдено env
  `QA_MCP_HOST_AGENT_EXPECTED_VERSION=0.1.0-platform-execute`, но пин и строка
  версии билда рассогласованы.
- **I (keymap F5):** `driver_windows.go::virtualKey` содержит `f4` (0x73), но
  **нет `f5`** (и прочих F1–F3/F6–F12). `_force_list_refresh` шлёт `F5` →
  `virtualKey("f5")` = (0,false) → keystroke не доставлен → «F5 keystroke failed
  (no reachable display backend); list not force-refreshed». Динамический список
  не может быть принудительно обновлён (в E2E список набрался поллингом, но
  холодный dynlist, которому нужен F5, не обновится).
- **L (cp866-вывод):** `/platform/execute` возвращает stdout/stderr ibcmd,
  декодируя OEM-байты (cp866) как UTF-8 lossy → русский вывод платформенных
  команд превращается в `�`-мусор (ASCII вроде version/UUID не страдает).

## Fix
- **H:** выровнять строку версии host-agent билда с `HOST_AGENT_VERSION` ЛИБО
  сделать проверку версии терпимой (набор допустимых/semver-совместимая),
  оставив опциональный `QA_MCP_HOST_AGENT_EXPECTED_VERSION` override.
- **I:** добавить `f1`–`f12` (VK 0x70–0x7B) в `virtualKey` keymap; регресс-тест
  на резолв F5.
- **L:** декодировать вывод дочернего процесса по его кодовой странице (OEM/
  console CP, напр. GetConsoleOutputCP/cp866) перед укладкой в JSON, либо
  отдавать сырые байты как base64 с указанием кодировки, чтобы русский текст был
  восстановим.

## Acceptance
- **H:** qa-mcp display-backend handshake проходит с текущим host-agent билдом
  без env-override (совпадающая/совместимая версия); mismatch по-прежнему
  диагностируется честно.
- **I:** `virtualKey("f5")` резолвит 0x74; `_force_list_refresh` доставляет F5;
  тест на набор функциональных клавиш.
- **L:** русский stdout/stderr платформенной команды через `/platform/execute`
  читаем (корректная кодировка), не `�`-мусор; ASCII-вывод не сломан.
- qa attach + read остаются рабочими.

## Scope
- Component-local (qa-mcp): host-agent Go (`driver_windows.go`,
  `platform_exec.go`) + Python `protocol/display_backend.py` (version) + тесты.
- Out of scope: admin read-only bridge routing (карта admin-mcp); classic
  file-IB семантика (находка K).

## Safety
- Read-only display/observability путь. `/platform/execute` mutation-boundary и
  allowlist неизменны. Никаких новых способностей — только keymap/кодировка/версия.

## Affected Repositories
- qa-mcp.

## Change Set
1. `host-agent-function-key-map` — F1–F12 в `virtualKey` (cap
   `qa-mcp-windows-host-agent-security`), archive:
   `openspec/changes/archive/2026-07-05-host-agent-function-key-map/`.
2. `host-agent-version-handshake-align` — выравнивание/толерантность версии
   (cap `qa-mcp-windows-host-agent-security`), archive:
   `openspec/changes/archive/2026-07-05-host-agent-version-handshake-align/`.
3. `host-agent-oem-output-decode` — корректная кодировка вывода `/platform/execute`
   (cap `qa-mcp-windows-host-agent-security`), archive:
   `openspec/changes/archive/2026-07-05-host-agent-oem-output-decode/`.

## Change 1: `host-agent-function-key-map`

### Why
`virtualKey` не знает `f5` → `_force_list_refresh` не может обновить dynlist.

### Goal
`f1`–`f12` резолвятся в корректные VK; F5 доставляется.

### Scope
- Добавить VK 0x70–0x7B в `driver_windows.go::virtualKey`; тест.

### Acceptance
- `virtualKey("f5")` = (0x74,true); регресс на набор F-клавиш.

### Depends On
- none

### Notes For `$openspec-ff-change`
- Modified capability: `qa-mcp-windows-host-agent-security`.

## Change 2: `host-agent-version-handshake-align`

### Why
Пин `HOST_AGENT_VERSION` рассогласован со строкой версии платформ-execute билда
(`0.1.0-platform-execute`) → handshake падает без env-override.

### Goal
Handshake проходит с текущим билдом без override; mismatch честно диагностируется.

### Scope
- Выровнять версию билда с пином ЛИБО допустимый набор/semver-совместимая
  проверка в `display_backend.py`; сохранить override-env. Тест.

### Acceptance
- Без `QA_MCP_HOST_AGENT_EXPECTED_VERSION` handshake проходит; реальный mismatch
  всё ещё ошибка.

### Depends On
- none

### Notes For `$openspec-ff-change`
- Modified capability: `qa-mcp-windows-host-agent-security`.

## Change 3: `host-agent-oem-output-decode`

### Why
`/platform/execute` декодит cp866-вывод как UTF-8 lossy → русский текст нечитаем.

### Goal
Русский stdout/stderr платформенных команд восстановим (корректная кодировка или
base64+encoding-метка).

### Scope
- Декод по OEM/console CP в `platform_exec.go` (или сырые байты+encoding); тест.

### Acceptance
- Русский вывод читаем; ASCII не сломан.

### Depends On
- none

### Notes For `$openspec-ff-change`
- Modified capability: `qa-mcp-windows-host-agent-security`.

## Related
- `openspec/changes/archive/2026-07-05-host-agent-function-key-map/`
- `openspec/changes/archive/2026-07-05-host-agent-version-handshake-align/`
- `openspec/changes/archive/2026-07-05-host-agent-oem-output-decode/`

## Verify
- `go test ./...` in `host-agent/windows-display-agent` — passed
- `uv run pytest tests/test_display_backend.py` — passed, 14 tests
- `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-function-key-map.test.exe .` — passed
- `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-version-handshake-align.test.exe .` — passed
- `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-oem-output-decode.test.exe .` — passed
- `uv run --with pytest --with pyyaml pytest` — passed, 692 tests
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/smoke_suite_source_of_truth_drift.py` — passed
- `uv run --with pytest --with pyyaml pytest -m smoke` — N/A, no tests selected in this component
- matrix preflight and archive checks for all three changes — passed
- `openspec validate qa-mcp-windows-host-agent-security --strict` — passed
- `openspec validate --all` — passed
- `git diff --check` — passed

## Archive
- `openspec/changes/archive/2026-07-05-host-agent-function-key-map/`
- `openspec/changes/archive/2026-07-05-host-agent-version-handshake-align/`
- `openspec/changes/archive/2026-07-05-host-agent-oem-output-decode/`

## Result
Delivered three host-agent display bridge fixes: F1-F12 key resolution, bounded
host-agent version compatibility, and CP866 fallback decode for platform
stdout/stderr. Published by the scoped `$opsx-pub` commit for this card.

## Next
- none

## Log
- 2026-07-05T07:50:07Z artifacts prepared; card moved to `2.todo`.
- 2026-07-05T07:59:08Z implementation verified; changes archived; card moved to `4.done`.
- 2026-07-05T08:04:42Z scoped publish commit created.
