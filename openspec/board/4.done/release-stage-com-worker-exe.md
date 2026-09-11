# Отгружать ai-com-worker.exe в standalone-релизе qa-mcp

## Status
4.done

## OpenSpec Stage
archived

## Owner
qa-mcp — release pipeline (`tools/release/publish_self_hosted.sh`) + delivery
(`bootstrap.ps1`) + host-agent installer. Дочерняя к COM-мосту (root
`live-com-over-host-bridge`, live-mcp `com-remote-host-bridge-transport`).

## Проблема
COM-мост требует на Windows-хосте `ai-com-worker.exe` (замороженный питон-воркер live-mcp),
который host-agent `exec`-ает по `/com/execute`. Установщик host-agent уже умеет его класть:
`install-windows-host-agent.ps1 -ComWorkerExe <path>` + автопоиск рядом с host-agent exe +
`QA_MCP_COM_WORKER_EXE` в env + `-com-worker` в scheduled task. **НО релиз-пайплайн qa-mcp
его не отгружает:**
- `tools/release/publish_self_hosted.sh` НЕ стейджит `ai-com-worker.exe` как asset (нет в
  списке ассетов/манифесте);
- `delivery/bootstrap.ps1` НЕ качает воркер (только host-agent exe + installer + образ).

Значит для COM-провайдера тестировщику сейчас пришлось бы вручную класть exe/передавать
`-ComWorkerExe`. Закрыть этот gap, чтобы COM-провайдер ставился из коробки.

## Дизайн
`ai-com-worker.exe` производит **live-mcp** (PyInstaller-цель `packaging/pyinstaller/
ai-com-worker.spec` + `scripts/build-com-worker-exe.sh`, только на Windows с pywin32). Эта
карточка — про **qa-mcp сторону**: принять готовый exe как вход, отгрузить его ассетом,
скачать+проверить в bootstrap и передать установщику.

## Change Set
- `stage-and-fetch-com-worker` — `openspec/changes/stage-and-fetch-com-worker/`

## Change Set (`$opsx-do`-исполним)

### Change 1: `stage-and-fetch-com-worker`
Capability: qa release/delivery.
- `tools/release/publish_self_hosted.sh`: параметр `--com-worker-exe <path>` (путь к готовому
  `ai-com-worker.exe`, собранному в live-mcp); если передан — скопировать в version-dir как
  asset, посчитать `.sha256`, включить в `manifest.json` (`ai1c.component-release.manifest.v1`);
  если не передан — предупредить (COM-провайдер не будет установлен из коробки), но не падать
  (обратная совместимость с не-COM релизом);
- `delivery/bootstrap.ps1`: если `ai-com-worker.exe` есть в манифесте — скачать, проверить
  sha256 (`Assert-AssetSha256`), положить рядом с `qa-mcp-host-agent.exe` (или передать
  `-ComWorkerExe`) ДО запуска `install-windows-host-agent.ps1`, чтобы установщик его подхватил;
- тесты: `tools/release/*` (manifest содержит worker asset при переданном флаге; отсутствует
  и не ломает при не переданном) — зеркалить `test_self_hosted_release_scripts.py`/
  `test_component_manifest.py`.

## Acceptance
- `publish_self_hosted.sh --com-worker-exe dist/ai-com-worker.exe …` кладёт exe в релиз +
  sha256 + запись в манифесте; без флага — релиз собирается как раньше (worker опционален).
- `bootstrap.ps1` при наличии worker-asset скачивает+верифицирует+кладёт его так, что
  `install-windows-host-agent.ps1` его находит (авто или `-ComWorkerExe`), и `/com/execute`
  `/health` репортит `available:true`.
- `pytest` qa-mcp зелёный; не-COM релиз-путь не сломан.

## Preconditions / оговорки
- Сам `ai-com-worker.exe` собирается в live-mcp на Windows (вне этой карточки) — здесь он
  вход. Реальная проверка установки — на Windows-боксе.
- Альтернатива, если карточку отложить: на E2E класть exe вручную / `-ComWorkerExe`.

## Scope
- IN: staging worker-asset в publish + download/verify/place в bootstrap + тесты.
- OUT: производство `ai-com-worker.exe` (live-mcp PyInstaller); Go `/com/execute` (уже есть).

## Affected Repositories
- qa-mcp (release + delivery).

## Related
- root `openspec/board/4.done/live-com-over-host-bridge.md`.
- live-mcp `com-remote-host-bridge-transport` (PyInstaller-цель).
- `host-agent/install-windows-host-agent.ps1` (`-ComWorkerExe`, автопоиск).
- `openspec/changes/archive/2026-07-05-stage-and-fetch-com-worker/`.
- scoped OPSX commit (`feat(release): bundle optional COM worker asset`).

## Result
Published in the scoped OPSX commit (`feat(release): bundle optional COM worker asset`).

Released behavior:
- `tools/release/publish_self_hosted.sh --com-worker-exe <path>` stages
  `ai-com-worker.exe`, writes a sha256 sidecar and includes the worker under
  manifest assets.
- Omitting `--com-worker-exe` keeps the existing non-COM release path and emits
  an operator-visible warning.
- `delivery/bootstrap.ps1` detects the optional worker asset in `manifest.json`,
  downloads and verifies it, and passes `-ComWorkerExe` to
  `install-windows-host-agent.ps1`.
- Release smoke coverage now exercises both worker-present and worker-absent
  staging paths.

Residual verification gap: Windows `/com/execute` `/health`
`available:true` proof requires a Windows host plus a live-mcp-built
`ai-com-worker.exe`; this Linux run records it as a provider/environment gap in
the verification matrix.

## Next
- none

## Verify
- `uv run --with pytest pytest tests/test_self_hosted_release_scripts.py tests/test_component_manifest.py` — passed, 7 tests.
- `uv run --with pytest --with pyyaml pytest` — passed, 707 tests.
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/check_suite_source_of_truth_drift.py` — passed, 0 findings.
- `uv run --with pytest --with pyyaml pytest -m smoke` — passed, 2 tests.
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py ... --mode preflight` — passed.
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/opsx_matrix_evidence_checker.py ... --mode archive` — passed.
- `openspec validate qa-mcp-self-hosted-release --strict` — passed.
- `openspec validate --all` — passed.
- `git diff --check` — passed.

## Archive
- `openspec/changes/archive/2026-07-05-stage-and-fetch-com-worker/`
- `.artifacts/openspec/stage-and-fetch-com-worker/20260705T200134Z/linux-release-tests.log`
- `.artifacts/openspec/stage-and-fetch-com-worker/20260705T200134Z/matrix-preflight.json`
- `.artifacts/openspec/stage-and-fetch-com-worker/20260705T200134Z/matrix-archive-gate.json`

## Log
- 2026-07-05 карточка создана: закрыть gap доставки `ai-com-worker.exe` в standalone-релизе
  (сейчас publish/bootstrap его не несут; установщик host-agent уже готов его принять).
- 2026-07-05T00:00:00Z `$opsx-ff`: created apply-ready OpenSpec artifacts for
  `stage-and-fetch-com-worker` and moved card to `2.todo`.
- 2026-07-05T20:12:01Z `$opsx-do`: implemented release/bootstrap worker asset
  handling, synced `qa-mcp-self-hosted-release`, archived the change, and moved
  card to `4.done`.
- 2026-07-05T20:12:01Z `$opsx-pub`: committed with message
  `feat(release): bundle optional COM worker asset`.
