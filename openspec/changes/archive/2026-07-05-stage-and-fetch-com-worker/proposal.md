## Why

The Windows COM bridge needs `ai-com-worker.exe` on the host, but the qa-mcp
self-hosted release currently publishes only the host-agent, installer,
bootstrap script, runbooks and image archive. This leaves COM-capable installs
dependent on manual worker placement even though the host-agent installer can
already accept the worker.

## What Changes

- Add an optional `--com-worker-exe <path>` input to the qa-mcp self-hosted
  publish helper.
- When the input is provided, stage `ai-com-worker.exe`, write its `.sha256`
  sidecar and include it in `manifest.json` assets.
- When the input is omitted, keep existing non-COM release staging behavior and
  emit a warning that COM worker delivery is not bundled.
- Update Windows `bootstrap.ps1` to detect a worker asset in the manifest,
  download and verify it with the existing sha256 path, and pass it to the
  host-agent installer before scheduled-task setup.
- Add focused release/bootstrap tests for both optional-worker and legacy
  non-worker flows.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-self-hosted-release`: self-hosted releases may carry the optional
  COM worker executable asset, and bootstrap installs it when the manifest
  declares it.

## Impact

- Touches release tooling under `tools/release/`, Windows delivery bootstrap
  under `delivery/`, and focused release tests.
- Does not change protocol capture/replay tooling, Python manager runtime
  protocol semantics, MCP provider setup, OpenSpec workflow, or lab runtime
  configuration.
- Does not produce `ai-com-worker.exe`; that remains a live-mcp Windows
  PyInstaller artifact supplied as an input.
- Linux-only verification can cover staging, manifest and script contracts.
  End-to-end `/com/execute` health proof still requires a Windows host with the
  live-mcp-built worker executable.
