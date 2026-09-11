# Робастность и UTF-8 по фидбэку тестировщика (P2/P3)

## Status
4.done

## Owner
qa-mcp — host-agent (Go, `/window_list`), MCP tools (form/attachment), delivery
(`bootstrap.ps1` + runbooks). Источник:
`openspec/board/1.backlog/qa-mcp-install-test-report.md` §3.4, §3.5, §4.1, §7 (P2/P3).

## OpenSpec Stage
archived

## Change Set
- `host-agent-window-list-utf8` — `openspec/changes/archive/2026-07-05-host-agent-window-list-utf8/`
- `form-read-current-form-and-stale-attachment` — `openspec/changes/archive/2026-07-05-form-read-current-form-and-stale-attachment/`
- `bootstrap-mcp-path-and-runbook` — `openspec/changes/archive/2026-07-05-bootstrap-mcp-path-and-runbook/`

## Проблема (из отчёта тестировщика)
Установка standalone qa-mcp v0.2.3 рабочая, но три класса шероховатостей мешают
автоматизации:
1. **host-agent `/window_list` отдаёт русские заголовки окон в mojibake** (`ÐÐµÑÑÐ¸Ñ 3.1.5 …`),
   при этом PowerShell `Get-Process 1cv8 | Select MainWindowTitle` показывает нормальный
   заголовок. Следствие: автосопоставление окна по русскому заголовку ненадёжно, пришлось
   использовать ASCII-фрагмент `3.1.5` через `-WindowTitle`. Тот же класс UTF-8-проблемы,
   что чинили в COM-passthrough — проверить кодировку ответа host-agent целиком.
2. **MCP-инструменты требуют `open_link` для live ManagedForm GUID, но неочевидно.** Без
   `open_link`: `read_form_descriptor` → `attached-descriptor-empty` /
   `managed_form_guid_ascii template field requires a live ManagedForm GUID`;
   `read_table_cell` → та же ошибка. С `open_link` — оба работают. Плюс: `attached=true`
   сохраняется при `listening=false` (после смерти/остановки TestClient контейнер держит
   stale attachment) → инструменты отвечают на мёртвый endpoint.
3. **bootstrap печатает `http://127.0.0.1:8000/mcp/`** (trailing slash), а сервер отвечает
   только на `/mcp` (`/mcp/` → `{"error":"not_found"}`). Плюс runbook-шероховатости:
   `-Password ""` отвергается (пустой пароль → параметр надо ОПУСКАТЬ), Docker Desktop мог
   быть не запущен, ручные PowerShell-вызовы кириллицы нужно слать UTF-8-байтами.

## Change Set (`$opsx-do`-исполним)

### Change 1: `host-agent-window-list-utf8`
Capability: qa host-agent bridge.
- `/window_list` (Go host-agent) возвращать русские заголовки **корректным UTF-8 JSON**
  (сейчас mojibake — проверить чтение `GetWindowTextW`/перекодировку, аналогично тому, что
  делали для COM UTF-8 passthrough); Go-тест на не-ASCII заголовок.
- Улучшить автоопределение окна: если заголовок не найден или найден fallback
  `Клиент тестирования` — предупреждать и предлагать `-WindowTitle`; рассмотреть матч по
  PID запущенного `1cv8.exe`, а не только по тексту.

### Change 2: `form-read-current-form-and-stale-attachment`
Capability: qa runtime UI reads.
- `read_form_descriptor`/`read_table_cell` на уже открытой текущей форме: либо уметь
  получить live ManagedForm GUID активной формы (без `open_link`), либо сделать `open_link`
  обязательным в схеме для этих режимов, либо давать внятную ошибку «cannot infer current
  ManagedForm GUID; pass open_link» (не глухой `managed_form_guid_ascii template field …`);
- инвалидация stale attachment: если `listening=false`, инструменты должны считать
  attachment недействительным (не отвечать на мёртвый endpoint) и давать action-hint
  («restart qa-mcp-testclient scheduled task»); `test_client_status`/`attach_test_client`
  могли бы предлагать/уметь рестарт.

### Change 3: `bootstrap-mcp-path-and-runbook`
Capability: qa delivery/runbook (сложить в change с capability, напр. delivery docs).
- `delivery/bootstrap.ps1`: печатать URL без завершающего слэша (`/mcp`, не `/mcp/`) — или
  научить сервер принимать оба;
- runbook (`delivery/README.md`/`windows-agent-runbook.md`): пустой пароль → **опускать**
  `-Password` (не `""`); проверка что Docker Desktop запущен (`docker info`); пример
  ручного PowerShell-вызова с UTF-8-байтами (`[System.Text.Encoding]::UTF8.GetBytes`);
  guidance по `-WindowTitle`.

## Acceptance
- `host-agent /window_list` возвращает русский заголовок как валидный UTF-8 (Go-тест +
  ручная проверка на боксе); автоопределение окна БСП стабильнее (не требует ASCII-обхода).
- `read_form_descriptor`/`read_table_cell` на текущей форме: либо работают без `open_link`,
  либо дают понятную инструктивную ошибку; stale `attached=true`/`listening=false` больше не
  ведёт к ответам на мёртвый endpoint.
- bootstrap печатает рабочий `/mcp`; runbook покрывает пустой пароль / Docker Desktop /
  UTF-8-байты / WindowTitle.
- `go test` (host-agent) + `pytest` (qa) зелёные.

## Preconditions / оговорки
- Реальная проверка window_list/формы — на Windows-боксе; UTF-8-логику и схемы — локально.

## Scope
- IN: window_list UTF-8 + автоопределение окна; form-read current-form/attachment robustness;
  bootstrap `/mcp` + runbook.
- OUT: `read_list_grid` table-resolution (отдельная карточка P1); `ai-com-worker.exe` staging
  (отдельная карточка).

## Affected Repositories
- qa-mcp (host-agent Go + MCP tools + delivery/runbook).

## Related
- `openspec/board/1.backlog/qa-mcp-install-test-report.md` §3.4, §3.5, §4.1, §5.5, §5.6, §7.
- `openspec/changes/archive/2026-07-05-host-agent-window-list-utf8/`
- `openspec/changes/archive/2026-07-05-form-read-current-form-and-stale-attachment/`
- `openspec/changes/archive/2026-07-05-bootstrap-mcp-path-and-runbook/`

## Verify
- `go -C host-agent/windows-display-agent test ./...` — passed.
- `GOOS=windows GOARCH=amd64 go -C host-agent/windows-display-agent test -c -o /tmp/qa-mcp-host-agent-window-list-utf8.test.exe .` — passed.
- `uv run --with pytest pytest tests/test_mcp_server.py -k "stale_attached_endpoint or stale_attachment_does_not_block_explicit_endpoint or without_open_link_returns_actionable_guid_error"` — passed.
- `uv run --with pytest pytest tests/test_self_hosted_release_scripts.py` — passed.
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py --mode archive ...` for all three changes — passed.
- `uv run --with pytest --with pyyaml pytest` — passed.
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/check_suite_source_of_truth_drift.py` — passed.
- `uv run --with pytest --with pyyaml pytest -m smoke` — N/A, no tests selected (`705 deselected / 0 selected`).
- `openspec validate --all` and `git diff --check` — passed.

## Archive
- `openspec/changes/archive/2026-07-05-host-agent-window-list-utf8/`
- `openspec/changes/archive/2026-07-05-form-read-current-form-and-stale-attachment/`
- `openspec/changes/archive/2026-07-05-bootstrap-mcp-path-and-runbook/`

## Publish
- Commit: this commit (`fix(qa-mcp): harden tester feedback paths`)

## Result
Delivered: host-agent JSON responses now declare UTF-8 and cover Russian `/window_list`
titles; bootstrap warns on weak generic window-title fallback; form-read tools return
`open-link-required` instead of raw ManagedForm GUID template errors; stale attachments
return `stale-attached-testclient` with recovery guidance; bootstrap/runbooks use `/mcp`,
document blank-password omission, Docker readiness, UTF-8 PowerShell bytes and
`-WindowTitle`.

## Next
- none

## Log
- 2026-07-05 карточка создана из отчёта тестировщика (P2/P3): window_list mojibake,
  form-read зависимость от `open_link` + stale attachment, bootstrap `/mcp/` slash + runbook.
- 2026-07-05T19:33:26Z OPSX ff: moved to `2.todo`, created three apply-ready change artifact sets.
- 2026-07-05T19:33:26Z OPSX do: implemented, verified, synced specs and archived all three changes.
- 2026-07-05T19:33:26Z OPSX pub: committed as `fix(qa-mcp): harden tester feedback paths`.
