## 1. Publish Helper

- [x] 1.1 Add `tools/release/publish_self_hosted.sh` with version, staging, optional upload and public-link activation arguments.
- [x] 1.2 Build/stage host-agent assets and protected thin image archive.
- [x] 1.3 Generate sha256 sidecars and `ai1c.component-release.manifest.v1`.
- [x] 1.4 Fail closed when protected-image verification or required local gates fail.

## 2. Bootstrap

- [x] 2.1 Replace GHCR/GitHub defaults with `-ReleaseBase` self-hosted downloads.
- [x] 2.2 Download and parse `manifest.json`.
- [x] 2.3 Verify sha256 before executing scripts or loading Docker archives.
- [x] 2.4 Load the Docker archive and run the manifest image tag.
- [x] 2.5 Configure `AI1C_MCP_PROXY_HTTP_TOKEN` and print bearer-token MCP config.

## 3. Docs

- [x] 3.1 Update `docs/self-hosted-release-delivery-plan.md`.
- [x] 3.2 Update `delivery/README.md`.
- [x] 3.3 Update `delivery/windows-agent-runbook.md`.
- [x] 3.4 Mark the old GitHub/GHCR path as legacy/fallback only.

## 4. Verification

- [x] 4.1 Run `uv run pytest -q -ra -m "not live"`.
- [x] 4.2 Run `go test ./...` in `host-agent/windows-display-agent`.
- [x] 4.3 Run publish helper local dry-run or staging smoke.
- [x] 4.4 Run PowerShell parse/static checks when `pwsh` is available.
- [x] 4.5 Record Windows model B E2E as retained evidence or a project/provider gap.
- [x] 4.6 Run `openspec validate self-hosted-publish-bootstrap --strict`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | release helper, manifest, bootstrap hash verification | dry-run/staging plus checksum verification | helper output, manifest, sha256 sidecars | `.artifacts/openspec/self-hosted-publish-bootstrap/20260703T101126Z/verification-summary.md` | done | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Full server activation not run; local staging smoke exercised the release layout. |
| QA/TestClient runtime | Windows bootstrap model B E2E | retained Windows E2E checklist after publish | host-agent health, TestClient TCP, tools/list, read-only form/list output | `.artifacts/openspec/self-hosted-publish-bootstrap/20260703T101126Z/windows-e2e.md` | n/a | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows host, interactive 1C desktop session, release server activation or PowerShell runtime in this Linux pass. | Must run after publishing a real release link on a Windows host. |
| Managed form layout | read-only form/list smoke | form descriptor/list-read scenario after bootstrap | form descriptor/list output | `.artifacts/openspec/self-hosted-publish-bootstrap/20260703T101126Z/windows-e2e.md` | n/a | `/opt/ai-dev-suite-for-1c/qa-mcp` | Depends on the Windows model-B E2E target and a real infobase. | Must retain form/list output during Windows E2E. |
