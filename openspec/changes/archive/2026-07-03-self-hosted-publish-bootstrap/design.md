## Context

The current bootstrap accepts `-Image` and `-DistBase`, downloads host-agent
assets from GitHub Releases, pulls a GHCR image, and prints an unauthenticated
HTTP MCP config. The target channel serves component release directories under:

`https://releases.aifor1c.ru:58443/qa-mcp/<release-link-id>/`

Each release directory contains `manifest.json`, bootstrap/install scripts,
host-agent executable, docs and a Docker archive.

## Design

### Publish Helper

`tools/release/publish_self_hosted.sh` should:

- Require `--version vX.Y.Z` and a release link id or generate one.
- Load release secrets from an ignored env file such as `.ai1c/release.env` when
  present; never print `BUNDLED_DATA_KEY`.
- Run local gates:
  - `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-fail-under=60`
  - `go test ./...` in `host-agent/windows-display-agent`
  - protected image build and `docker/verify_protected_image.py` when Docker is
    available.
- Build `qa-mcp-host-agent.exe`.
- Save the thin image as `qa-mcp-thin-<version>.tar`, compress to `.tar.zst` when
  `zstd` is available, and generate sha256 sidecars.
- Stage `manifest.json`, bootstrap, install script, host-agent exe, README and
  runbook under a local release staging directory before upload.
- Upload to `/srv/ai1c-releases/qa-mcp/versions/<version>/` and activate one public
  link under `/srv/ai1c-releases/qa-mcp/public/<release-link-id>/` when server
  options are provided. A local-only dry run should remain possible.

### Bootstrap

`delivery/bootstrap.ps1` should:

- Prefer `-ReleaseBase` over `-DistBase`; keep `-DistBase` only as a legacy alias
  if needed for compatibility.
- Download `manifest.json` first.
- Verify sha256 for every downloaded asset before executing install scripts or
  loading the Docker archive.
- Load the image archive with `docker load` and use the manifest image tag for
  `docker run`.
- Generate or accept an MCP proxy token and pass it as
  `AI1C_MCP_PROXY_HTTP_TOKEN`.
- Print MCP client config with `Authorization: Bearer <token>` and the existing
  `http://127.0.0.1:<McpPort>/mcp/` URL.

### Windows E2E

The final release proof remains a Windows run on a licensed 1C host:

- host-agent `/health`
- container-to-host-agent `/version`
- container-to-TestClient TCP
- MCP `tools/list`
- at least one read-only form/list tool call

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `tools/release/publish_self_hosted.sh`, release server staging, bootstrap downloads | local dry-run/staging and sha256 verification | helper dry-run output, manifest, sha256 sidecars | `.artifacts/openspec/self-hosted-publish-bootstrap/<run-id>/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient runtime | Windows model B bootstrap and E2E | Windows release-run checklist after publish | retained Windows E2E summary | `.artifacts/openspec/self-hosted-publish-bootstrap/<run-id>/windows-e2e.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Managed form layout | Read-only form/list proof during E2E | QA/TestClient read-only smoke after bootstrap | form descriptor/list read output in Windows E2E bundle | `.artifacts/openspec/self-hosted-publish-bootstrap/<run-id>/windows-e2e.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |

## Risks

- PowerShell bootstrap hash verification must fail closed. Mitigation: verify before
  executing installers or loading images.
- No code-signing yet. Mitigation: HTTPS, secret public link and sha256 manifest are
  explicit v1 controls; signing remains future hardening.
- A full Windows E2E requires an operator-provided Windows host and 1C infobase.
  If unavailable during this delivery, record a provider/project gap before archive.
