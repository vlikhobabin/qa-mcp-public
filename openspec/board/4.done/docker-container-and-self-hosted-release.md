# qa-mcp suite-reconciliation: контейнеризация Model B → ai-suite-base + serve-http + :58443

## Status
4.done

## Owner
qa-mcp maintainer (компонент whole-product bundle; выравнивание на suite-паттерн)

## OpenSpec Stage
archived

## Source
- Глубокий разбор qa delivery 2026-07-03: qa — полноправный компонент продукта, но
  shipped-путь на **своей схеме** (свои Dockerfile, FastMCP-HTTP, GHCR/GitHub,
  vendored broker), не на suite-паттерне. Хорошо: тот же `mcp`/FastMCP SDK, дефолт
  **stdio** (proxy-wrappable), тот же `ai1c-license` broker, CR-06 hardened, а
  gateway/compose **уже резервируют** `ai-suite-qa` + `AI_SUITE_PROVIDER_QA_URL`
  (`../../deploy/docker/compose.yml:117,183`).
- Root-эпик `../../openspec/board/1.backlog/suite-docker-delivery.md`; мастер-док
  `../../docs/dev-mcp-suite-docker-delivery-architecture.md` (Р1/Р2/Р5/Р6/Р11).
- qa собственный `docs/self-hosted-release-delivery-plan.md` (уже переизобрёл suite-
  манифест/хост/архив/secret-link — дореализовать его Phase 2-3 под :58443).

## Summary
Свести **Model B (thin, реальный Windows-продукт)** к suite-паттерну, **переиспользуя**
qa-специфику (Windows host-agent, TestClient TCP-мост, bootstrap, CR-06, Nuitka
IP-protection). Транспорт/база/license конвергируют механически; единственная
настоящая архитектурная развилка — protected `_bundled/` IP (см. Решение 1).

## Load-bearing решения (ратифицировать в `$opsx-ff`)
1. **Data carve-out (Р5-исключение):** зашифрованный `src/qa_mcp/_bundled/` (~2.2 MB
   протокол-IP: captures/templates; Nuitka+AES-GCM, ключ в `.so`) **остаётся baked в
   code-image** — вынос раскрыл бы крон-жьюэлы (карты 122/123). В расширенном
   манифесте у qa **НЕТ отдельного data-asset** (у qa нет объёмных swap-данных →
   Р5 к нему не применим). Это осознанное исключение из «данные вон из образа».
2. **Transport swap:** `docker/Dockerfile.thin` финальная стадия `FROM ai-suite-base`
   (`../../deploy/docker/Dockerfile.base` — уже несёт `ai-mcp-proxy`+`ai1c-license`);
   **убрать** FastMCP-HTTP-режим и vendored broker (`delivery/broker/…`); `CMD` →
   `ai-mcp-proxy serve-http --provider-id qa-mcp … -- qa-native-mcp` (stdio) на
   **:8080**; раз-placeholder `ai-suite-qa` за gateway route `/qa-mcp/*`. Nuitka
   builder-стадию оставить.
3. **Publish migration:** GHCR/GitHub (`delivery/bootstrap.ps1:16-17`) →
   `releases.aifor1c.ru:58443/qa-mcp/`: реализовать `tools/release/publish_self_hosted.sh`
   (Docker-архив `.tar.zst` + `ai1c.component-release.manifest.v1` + sha256 + secret-
   link) и ретаргетить `bootstrap.ps1`; host-agent `.exe` + bootstrap — release-assets
   рядом с образом. (Завершает qa self-hosted Phase 2-3.)
4. **Scope:** конвергируем **только Model B**; Model A (bookworm/X11/WebKit,
   all-in-container) — вне релизной поверхности; **Windows host-agent остаётся
   внешним host-side asset** (не MCP-провайдер, живёт вне Linux-образа).

## Переиспользуем как есть (qa-специфика, suite-эквивалента нет)
- Windows **host-agent** (Go `.exe` :8001, token+Origin, scheduled-task) — qa-аналог
  suite host-agent-моста для TestClient/desktop.
- **TestClient TCP-мост** `host.docker.internal:15381` + `QA_MCP_REMOTE_CLIENT` +
  loopback-origin находка (карта 119).
- `delivery/bootstrap.ps1` + `windows-agent-runbook.md` (ретаргетить download-base).
- **CR-06** hardening (firewall, token-file, constant-time, Origin allowlist,
  non-root USER, healthcheck, digest-pin). **Nuitka IP-protection** + `verify_protected_image.py`.

## Acceptance (черновик, уточнить в `$opsx-ff`)
- `docker/Dockerfile.thin` финал `FROM ai-suite-base`; qa serve-http через
  `ai-mcp-proxy` на :8080 (`/mcp` `/health` Bearer); vendored broker удалён,
  license-gate проходит через base + deployment-creds.
- `ai-suite-qa` в `deploy/docker/compose.yml` — реальный thin-образ за `/qa-mcp/*`
  (координация с root).
- `_bundled/` остаётся protected/baked; манифест qa без data-asset (carve-out).
- publish на `releases.aifor1c.ru:58443/qa-mcp/` (архив+manifest+sha256+secret-link);
  bootstrap скачивает оттуда, НЕ с GHCR/GitHub; host-agent.exe/bootstrap как assets.
- Model A вне релиза; host-agent — внешний. Секреты/ключи вне git.

## Scope
- qa-mcp: `docker/Dockerfile.thin`, `delivery/`, `tools/release/`, `src/qa_mcp/mcp_server.py`
  (транспорт), self-hosted plan Phase 2-3.
- root (координация): раз-placeholder `ai-suite-qa` в `deploy/docker/compose.yml`,
  release-train учёт qa (пересечение с normalization).
- НЕ входит: Model A конвергенция; host-agent как контейнер.

## Change Set
- `suite-base-proxy-transport`
- `protected-bundle-release-manifest`
- `self-hosted-publish-bootstrap`

## Change 1: `suite-base-proxy-transport`

### Why
qa-mcp model B already exposes a stdio MCP entrypoint, but the thin container still
uses its own FastMCP HTTP mode, port 8000 and vendored broker path instead of the
suite provider base plus `ai-mcp-proxy serve-http`.

### Goal
Make the protected thin image inherit the suite provider base and expose qa-mcp
through the same proxy/gateway-ready HTTP contract as the other suite providers.

### Scope
- Change `docker/Dockerfile.thin` final stage to use the suite base image contract.
- Run `qa-native-mcp` as stdio under `ai-mcp-proxy serve-http` on container port 8080.
- Remove the image-local broker copy from the final image; use the broker supplied by
  the suite base image.
- Keep model B remote TestClient and Windows host-agent behavior intact.
- Coordinate the root `ai-suite-qa` compose slot as a scoped cross-repo handoff.

### Acceptance
- Thin image final stage comes from `ai-suite-base` or an overrideable
  `SUITE_BASE_IMAGE`.
- `/health` is served by `ai-mcp-proxy`; `/mcp` fails closed without a bearer token.
- The final command launches `qa-native-mcp` through the proxy on port 8080.
- Existing model B defaults still point protocol traffic at `host.docker.internal:15381`
  and display traffic at the Windows host-agent when configured.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-07-03-suite-base-proxy-transport/`

### Notes For `$openspec-ff-change`
- Reuse the existing stdio default in `src/qa_mcp/mcp_server.py`; do not add a second
  HTTP implementation.

## Change 2: `protected-bundle-release-manifest`

### Why
The suite Docker architecture requires data to be outside provider code images, but
qa-mcp's small encrypted `_bundled/` corpus is protocol IP and should remain baked
into the protected code image.

### Goal
Ratify the qa-specific P5 carve-out and make release manifests express that qa-mcp
has no separate data asset for `_bundled/`.

### Scope
- Document the `_bundled/` carve-out in qa-mcp delivery docs.
- Keep protected build verification proving `_bundled/` is encrypted in the image.
- Extend the component release manifest model so qa-mcp can explicitly declare no
  separate data asset.
- Keep secrets and `BUNDLED_DATA_KEY` outside git.

### Acceptance
- Release docs say `_bundled/` remains encrypted and baked into the code image.
- Generated component manifests include the protected image asset and no qa data
  asset for `_bundled/`.
- Verification keeps `docker/verify_protected_image.py` as the protected-image gate.

### Depends On
- `suite-base-proxy-transport`

### Related
- `openspec/changes/archive/2026-07-03-protected-bundle-release-manifest/`

### Notes For `$openspec-ff-change`
- This is a delivery-contract change, not a protocol behavior claim.

## Change 3: `self-hosted-publish-bootstrap`

### Why
The current model B release path still depends on GHCR and GitHub Releases, while
the suite target release channel is `releases.aifor1c.ru:58443` with versioned
archives, secret public links, manifests and sha256 verification.

### Goal
Add a local self-hosted publish helper and migrate bootstrap/runbook defaults to the
qa-mcp component release namespace.

### Scope
- Add `tools/release/publish_self_hosted.sh`.
- Generate `ai1c.component-release.manifest.v1`, sha256 sidecars and Docker archives.
- Update `delivery/bootstrap.ps1` to use `-ReleaseBase`, manifest verification and
  `docker load` instead of GHCR/GitHub defaults.
- Update `delivery/README.md`, `delivery/windows-agent-runbook.md` and the self-hosted
  plan with the migrated flow.

### Acceptance
- Bootstrap can run from a secret `https://releases.aifor1c.ru:58443/qa-mcp/...`
  release link without GitHub or GHCR requests.
- Downloaded bootstrap assets and image archive are sha256-verified before execution
  or `docker load`.
- The publish helper stages versioned release assets and emits the manifest plus
  checksums without committing secrets.

### Depends On
- `suite-base-proxy-transport`
- `protected-bundle-release-manifest`

### Related
- `openspec/changes/archive/2026-07-03-self-hosted-publish-bootstrap/`

## Affected Repositories
- qa-mcp (этот репозиторий).
- root — `ai-suite-qa` compose + release-train (координация).

## Related
- `docs/self-hosted-release-delivery-plan.md`; board `4.done/119-*`, `4.done/cr-06-*`, `1.backlog/118-*`.
- `../../docs/dev-mcp-suite-docker-delivery-architecture.md` (Р5/Р6/Р11); `../../deploy/docker/Dockerfile.base`, `compose.yml`.
- `../../meta-mcp/docker/Dockerfile` (эталон serve-http-паттерна).
- `docs/dev-mcp-suite-opsx-runtime-verification.md` (qa = 1C runtime/UI контур).

## Result
Delivered through three archived OpenSpec changes:

- `suite-base-proxy-transport`: protected thin image now inherits `ai-suite-base`,
  runs `qa-native-mcp` under `ai-mcp-proxy serve-http` on container port 8080,
  requires bearer-token MCP access and uses the suite base license broker.
- `protected-bundle-release-manifest`: qa-mcp release manifests explicitly keep
  protected `_bundled/` data encrypted in the image with `data_assets: []`.
- `self-hosted-publish-bootstrap`: self-hosted publisher, manifest/sha256 release
  layout, `ReleaseBase` bootstrap, `docker load` image install and bearer-token
  MCP config are implemented.

Verification retained:

- `uv run pytest -q -ra -m "not live"`: 687 passed.
- `go test ./...` in `host-agent/windows-display-agent`: passed.
- protected image build/verifier and proxy-auth smoke passed for the suite-base
  image.
- publish helper local staging smoke produced manifest, sidecars, bootstrap,
  host-agent executable and real Docker archive under
  `.artifacts/openspec/self-hosted-publish-bootstrap/20260703T101126Z/release-stage/versions/v0.2.3`.
- `openspec validate --all`: 19 passed, 0 failed.

Known gap: Windows model-B E2E requires a real Windows host, interactive 1C
desktop session and activated release link; checklist retained in
`.artifacts/openspec/self-hosted-publish-bootstrap/20260703T101126Z/windows-e2e.md`.

## Next
- Publish scoped commits for qa-mcp and the root `deploy/docker/compose.yml`
  coordination change.

## Log
- 2026-07-03 implemented and archived `suite-base-proxy-transport`,
  `protected-bundle-release-manifest` and `self-hosted-publish-bootstrap`; moved
  card to `4.done`.
- 2026-07-03 fast-forwarded into three qa-owned changes and moved to `2.todo`.
- 2026-07-03 stub создан из глубокого разбора qa: reconciliation Model B к suite-
  паттерну (умеренный графт, не переписывание); 4 решения зафиксированы; qa —
  полноправный компонент + пилот standalone-поставки.
