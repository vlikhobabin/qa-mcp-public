# Host-agent для командной топологии: саморегистрация в bridge-реестре + супервизия локального bsl-agent

## Status
4.done (external review cycle 2: go; published; five Windows/live criteria
CLOSED on the 2026-07-12 supervised .201 stand pass — all AC verified)

## OpenSpec Stage
archived after cycle-2 fix-and-reverify

## Change Set
1. `openspec/changes/archive/2026-07-11-bridge-self-registration-client/`
2. `openspec/changes/archive/2026-07-11-native-helper-supervision-bsl-agent/`

## Owner
qa-mcp (host-agent). Парные карточки:
- root `openspec/board/1.backlog/team-t2-team-server-profile-and-multi-user.md`
  Change 3 — **registry-сервис** и схема контракта
  `ai1c.bridge-registration.v1` в `deploy/docker/schemas/` (серверная
  половина; общий контракт);
- bsl-mcp `openspec/board/1.backlog/team-t3-workstation-local-bsl-agent.md`
  — бинарь bsl-agent + контракт запуска/health (Change 3 там);
- root `openspec/board/1.backlog/team-t3-git-build-server-and-thin-workstation.md`
  Change 3 — wiring обоих кусков в процедуру станции.

## Source
- Дизайн-документ (root) `docs/dev-mcp-suite-team-topology-architecture.md`,
  **decision-freeze #6**: выбрана **динамическая саморегистрация** (не
  статический реестр — пилот 20–30 разработчиков + DHCP). Новый аддитивный
  контракт **`ai1c.bridge-registration.v1`** (тело = существующий
  `ai1c.windows-host-bridge.discovery.v1`): host-agent при старте + по
  **heartbeat (30 с)** POST-ит `{user, достижимый endpoint, per-dev токен,
  discovery-тело, ttl}`; **TTL 90 с**; протухшие записи истекают; рестарт
  registry → самовосстановление из heartbeat; **анти-подмена** (host-agent
  регистрирует только своего пользователя); fail-closed резолюция
  потребителями по `X-AI-Suite-User`. Ноль per-dev конфигурации у оператора
  team-server.
- **Decision-freeze #5**: локальный bsl-agent живёт **под управлением
  host-agent** — процесс-супервизия на стороне host-agent (эта карточка),
  бинарь и контракт — bsl-mcp-карточка.
- Заземление: host-agent 0.1.4; прецедент супервизии нативного помощника —
  `ai-com-worker.exe` (COM Variant A); контракт
  `ai1c.windows-host-bridge.discovery.v1` существует.

## Problem
В команде серверные потребители bridge (qa/admin/live/agentic-rag +
маршрутизация к локальному bsl-agent) должны резолвить «какой bridge-эндпоинт
обслуживает пользователя X». Реестр (root T2) наполняется ТОЛЬКО
саморегистрацией host-agent — клиента саморегистрации не существует. Для
станции W-B (freeze #5) host-agent должен управлять локальным bsl-agent —
супервизии нет.

## Goal
Станция после установки host-agent **сама** появляется в реестре team-server
и поддерживает присутствие heartbeat'ом (оператор ничего не вносит руками);
локальный bsl-agent живёт под host-agent (запуск/health/автоперезапуск) и
отвечает на диагностические запросы.

## Non-goals
- Registry-сервис и схема контракта — root T2 Change 3 (здесь — клиент).
- Windows-сборка bsl-agent и его workspace-режим — bsl-mcp-карточка.
- Федерация аккаунтов Forgejo ↔ `X-AI-Suite-User` — позже (за границей v1).
- Изменения протокола TestClient / UI-инструментов qa-mcp.
- Инсталляционная процедура станции целиком — root T3 Change 3.

## Contract guardrails
- Токены (per-dev, gateway) не попадают в логи/evidence — существующая
  redaction-модель host-agent распространяется на новые пути.
- **Анти-подмена**: host-agent регистрирует только пользователя из конфига
  станции; смена user — только рестарт с новым конфигом, не на лету.
- **Соло-режим неприкосновенен**: без сконфигурированного registry — ноль
  сетевых запросов, ноль ошибок, поведение host-agent не меняется.
- Полный pytest-набор компонента зелёный в каждом change.

---

## Change 1: `bridge-self-registration-client` (freeze #6)
Клиент саморегистрации в host-agent.

Scope:
- При старте + каждые 30 с (конфиг) POST на registry-эндпоинт team-server:
  `{user, достижимый endpoint (host:port с учётом выбранного интерфейса),
  per-dev токен, discovery-тело (ai1c.windows-host-bridge.discovery.v1),
  ttl}` по контракту `ai1c.bridge-registration.v1`.
- Конфиг: env/файл станции (registry URL, user, токен, интервал heartbeat).
- Поведение: ре-регистрация после рестарта host-agent; после рестарта registry
  следующий heartbeat восстанавливает запись; сетевые ошибки → ретрай на
  следующем heartbeat, host-agent не падает и bridge-функции не деградируют.
- Без registry-конфига — выключено (соло).

Критерии приёмки (PASS/FAIL):
- [x] AC1.1 Против fixture-registry (мок по схеме) или живого root
      T2-сервиса: запись появляется при старте; heartbeat продлевает TTL
      (наблюдаемо); останов host-agent → запись истекает ≤ TTL. **PASS:**
      fixture validates raw JSON against an independent frozen
      `ai1c.bridge-registration.v1` schema; a `ttl_seconds`→`ttl` drift is
      rejected, and startup/heartbeat/TTL expiry tests pass.
- [x] AC1.2 Рестарт registry → запись восстановлена в течение одного
      heartbeat-интервала без действий оператора. **Закрыто на .201 2026-07-12:**
      mock-registry (`ai1c.bridge-registration.v1`), heartbeat 2s; стоп mock →
      `state=error`/`registry-unavailable` (host-agent жив); рестарт mock в
      07:47:37.93 → REGISTER в 07:47:38.68 (0.75s < heartbeat), `state=registered`,
      `last_success` двинулся. Реестр самовосстановился из heartbeat.
- [x] AC1.3 Анти-подмена: несоответствие user/токена → отказ сервера
      обработан корректно (лог без секретов, без падения); user не
      переопределяется без рестарта с новым конфигом (тест).
- [x] AC1.4 Недоступный registry → host-agent жив, bridge-функции работают;
      соло-режим (нет конфига) → ноль запросов к registry (тест).
      **Закрыто на .201 2026-07-12:** `-registry-url http://127.0.0.1:59999`
      (недоступен) → host-agent жив (`HA-EXITED=False`, `/health` отвечает),
      `registration.state=error/registry-unavailable`, `attempt_count=4`
      (ретраит). Соло-режим (ноль запросов) — Linux-покрытие.
- [x] AC1.5 Токены не в логах/evidence (grep-тест); полный pytest-набор
      компонента зелёный.

## Change 2: `native-helper-supervision-bsl-agent` (wiring freeze #5)
Супервизия локального bsl-agent по образцу com-worker.

Scope:
- Запуск bsl-agent с конфигом (путь бинаря, рабочая копия, syntax-helper —
  по контракту bsl-mcp Change 3), health-проба, **автоперезапуск при падении**
  (с backoff), останов вместе с host-agent.
- Статус локального bsl-agent в doctor-инструментах (`qa_mcp_doctor`:
  отдельная секция — состояние, версия, счётчик рестартов).
- Маршрутизация диагностических запросов через host-agent к локальному
  bsl-agent (endpoint из контракта).

Критерии приёмки:
- [x] AC2.1 Host-agent поднимает bsl-agent по конфигу; health виден в doctor
      (evidence). **Закрыто на .201 2026-07-12:** host-agent
      `0.1.6-bsl-supervision` поднял `bsl-agent.exe 0.4.170`; `/health` →
      `bsl_agent {state:"ready", version:"0.4.170",
      protocol:"ai1c.bsl-agent-workstation-http.v1", restart_count:0}` (блок,
      который читает `qa_mcp doctor` `_bsl_agent_check`).
- [x] AC2.2 Kill процесса bsl-agent → автоперезапуск ≤ конфигурируемого
      интервала; счётчик рестартов в статусе (тест/evidence). **Закрыто на .201
      2026-07-12:** `taskkill /IM bsl-agent.exe` (PID 21256, child host-agent
      21008) → супервизор перезапустил → `state=ready`, `restart_count 0→1`.
- [x] AC2.3 Диагностический запрос через host-agent → ответ локального
      bsl-agent (сцепка со сценарием bsl-mcp AC2.1–AC2.2). **Закрыто на .201
      2026-07-12:** `POST /bsl/diagnostics` (token) → `HTTP 200`, проксировано в
      bsl-agent → «Тип 'NoSuchTypeXYZ' не найден» (range line:1 char:1–23).
- [x] AC2.4 Без сконфигурированного bsl-agent host-agent работает как раньше
      (соло / не-W-B станция) — регрессии нет (тест).
- [x] AC2.5 Полный pytest-набор компонента зелёный (com-worker, окна,
      TestClient — не регрессировали).

---

## Definition of Done
1. Все AC отмечены со ссылками на evidence в карточке.
2. Сквозной стенд-кейс воспроизводим ревьюером: станция появилась в реестре
   **сама** + локальная диагностика через host-agent отвечает.
3. Соло-режим не изменён (негативные тесты AC1.4/AC2.4).
4. Полный pytest-набор зелёный на финальном состоянии.
5. Ни один Non-goal не реализован «заодно».

## Reviewer checks
- Токен-grep по логам/evidence — пусто.
- Соло-режим: ноль сетевых запросов к registry без конфига (тест существует).
- User неизменяем на лету (анти-подмена).
- Пути com-worker/TestClient/окон не регрессировали (pytest).

## Related
- Root T2 Change 3 (registry-сервис + `ai1c.bridge-registration.v1` в
  `deploy/docker/schemas/`), bsl-mcp workstation-карточка (контракт),
  root T3 Change 3 (процедура станции), дизайн-док freeze #5/#6,
  `ai1c.windows-host-bridge.discovery.v1`.
- `openspec/changes/archive/2026-07-11-bridge-self-registration-client/`
- `openspec/changes/archive/2026-07-11-native-helper-supervision-bsl-agent/`

## Verify
- PASS: the registration fixture validates raw request JSON with an independent
  frozen v1 schema; the explicit field-drift negative test fails closed.
- PASS: registry recovery is bounded by one 250 ms heartbeat plus 100 ms
  scheduler tolerance (below two heartbeats), and authenticated `/window_list`
  remains functional while RegistrationClient reports `registry-unavailable`.
- PASS: fake-helper replacement launch is bounded by the configured 250 ms
  backoff plus 100 ms process-reaping/scheduler tolerance (below two backoffs),
  with readiness checked separately and restart count incremented.
- PASS: focused regressions passed, including 10 repeated runs; all host-agent
  Go tests and race tests passed; `go vet` and Windows AMD64 cross-build passed;
  full pytest passed 803; suite drift passed with 0 findings; smoke passed 3;
  strict OpenSpec, matrix preflight/archive and diff checks passed.
- Provider gaps at delivery (`unverifiable`, not PASS): AC1.2, AC1.4, AC2.1,
  AC2.2, AC2.3. **All five CLOSED on the 2026-07-12 supervised Windows-stand pass
  (.201)** — see `## Windows-stand pass (2026-07-12)`. Evidence roots are recorded
  in the delivery manifest.

## Windows-stand pass (2026-07-12)

Supervised run on .201 (`HISTORICAL-LAB-HOST`). `qa-mcp-host-agent.exe`
(`0.1.6-bsl-supervision`) cross-built from tracked Go source; supervised
`bsl-agent.exe 0.4.170` over the bundled demo10413 dump (syntax-helper
8.3.27.2130). All five deferred Windows/live criteria verified:

- AC2.1: `/health` → `bsl_agent {state:"ready", version:"0.4.170",
  protocol:"ai1c.bsl-agent-workstation-http.v1", restart_count:0}` after
  supervised launch.
- AC2.2: `taskkill bsl-agent.exe` → auto-restart, `restart_count 0→1`, ready.
- AC2.3: `POST /bsl/diagnostics` → HTTP 200 round-trip → "Тип 'NoSuchTypeXYZ'
  не найден".
- AC1.4: `-registry-url` unreachable → host-agent alive (`/health` served),
  `registration.state=error/registry-unavailable`, keeps retrying.
- AC1.2: mock `ai1c.bridge-registration.v1` registry, heartbeat 2 s; stop → error;
  restart → re-registration 0.75 s later (< heartbeat), `state=registered`,
  `last_success` advanced.
- Evidence (sanitized, gitignored):
  `.artifacts/openspec/team-host-agent-self-registration-and-bsl-supervision/2026-07-12-windows-stand/windows-stand-evidence.md`.

## Archive
- `openspec/changes/archive/2026-07-11-bridge-self-registration-client/`
- `openspec/changes/archive/2026-07-11-native-helper-supervision-bsl-agent/`

## Result
Cycle-1 R1--R3 and failed AC1.1 are resolved in the Linux fixture/offline
scope. Both changes are reverified, specs are idempotently synced, and changes
are re-archived. Decision-freeze #1--#8 and Р24--Р27 remain unchanged. AC1.2,
AC1.4 and AC2.1--AC2.3 stay `unverifiable` pending the real Windows stand.
Independent external review cycle 2 returned a valid, fresh `result: go` with
those five criteria honestly retained as `unverifiable`; the scoped delivery
is published from the manifest-owned file set.

## Next
No further action. The five deferred Windows/team-server stand proofs were
collected on the 2026-07-12 supervised .201 pass (all PASS); card fully verified.

## Log
- 2026-07-10 карточка создана из decision-freeze #6 (динамическая
  саморегистрация bridge) + wiring freeze #5 (супервизия локального
  bsl-agent) — обе доработки host-agent собраны в одну qa-mcp-карточку.
- 2026-07-11 OPSX FF: созданы apply-ready `bridge-self-registration-client`
  и `native-helper-supervision-bsl-agent`; decision-freeze #1--#8 и Р24--Р27
  не переоткрывались; offline verification/runtime provider-gap boundary
  зафиксирован в design/tasks.
- 2026-07-11 OPSX DO: оба change реализованы test-first, offline verification
  зелёная, specs synced, changes archived; Windows/live evidence оставлено
  provider gaps по прямому указанию оператора. Commit/push не выполнялись.
- 2026-07-11 safety stop: `awaiting external review`; implementing session did
  not create or run a reviewer and did not invoke `$opsx-pub`.
- 2026-07-11 external review cycle 1: `result=no-go`; R1 blocker found the
  producer-coupled registry fixture, R2 found non-enforced heartbeat/restart
  timing bounds, and R3 found no existing bridge-operation assertion during
  registry failure. Card and both changes moved back to active lifecycle for
  rescue; Windows/live evidence remains explicitly out of scope.
- 2026-07-11 OPSX DO rescue: added independent JSON Schema fixture validation
  with a RED wire-drift regression, enforced heartbeat and helper-restart
  timing bounds, and exercised `/window_list` during active registry failure.
  Full Go/Python/OpenSpec/matrix floor passed; canonical specs were already
  synced; both changes re-archived. Stopped `awaiting external review` cycle 2;
  no reviewer, publish, commit or push was run.
- 2026-07-11 external review cycle 2: fresh `result=go`; all Linux/offline
  findings are resolved and AC1.2, AC1.4, AC2.1--AC2.3 remain explicit
  `unverifiable` Windows-stand gaps. `$opsx-pub` used the delivery manifest,
  retained runtime evidence outside git, and published the scoped card-owned
  implementation, specs, archives, tests, and documentation.
- 2026-07-12 supervised Windows-stand pass on .201 (`HISTORICAL-LAB-HOST`):
  `qa-mcp-host-agent.exe 0.1.6-bsl-supervision` cross-built from source,
  supervised `bsl-agent.exe 0.4.170` over the demo10413 dump. Closed all five
  deferred criteria — AC2.1 (launch+health), AC2.2 (kill→restart, count 0→1),
  AC2.3 (diagnostic round-trip), AC1.4 (unavailable registry→alive), AC1.2
  (mock registry restart→re-reg ≤ heartbeat). Sanitized evidence under gitignored
  `.artifacts/.../2026-07-12-windows-stand/`. Card record updated in place; no
  code change, no publish scope change.
