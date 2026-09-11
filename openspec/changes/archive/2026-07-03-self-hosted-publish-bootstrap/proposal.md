## Why

qa-mcp's model B release path still pulls a container from GHCR and assets from
GitHub Releases. The suite release architecture has moved to a self-hosted
release host, versioned Docker archives, secret public links, component manifests
and sha256 verification.

## What Changes

- Add `tools/release/publish_self_hosted.sh` for local qa-mcp release staging and
  upload to the self-hosted component namespace.
- Generate a versioned Docker archive, sha256 sidecars and
  `ai1c.component-release.manifest.v1`.
- Update `delivery/bootstrap.ps1` to accept `-ReleaseBase`, download
  `manifest.json`, verify sha256, `docker load` the image archive and run the
  loaded image tag.
- Update delivery README/runbook/self-hosted docs to make
  `https://releases.aifor1c.ru:58443/qa-mcp/<release-link-id>/` the canonical
  component release path.

## Capabilities

### New Capabilities
- `qa-mcp-self-hosted-release`: qa-mcp can be published and installed from the
  AI for 1C self-hosted component release host without GitHub/GHCR dependency.

### Modified Capabilities
- none

## Impact

Touches release tooling, PowerShell bootstrap, delivery docs and Windows model B
operator flow. It does not change protocol frame semantics. Windows-native E2E is
the final release proof; local delivery verifies manifest parsing, sha256 checks,
script syntax and offline tests.
