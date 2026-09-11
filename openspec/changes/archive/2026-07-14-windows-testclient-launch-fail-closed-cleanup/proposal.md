## Why

Independent review found two fail-open Windows launch paths: an omitted platform version selects the newest installed build, and request cancellation can kill the registration PowerShell process before its `finally` removes the transient task. Both contradict the source-bound launch and exact-ownership cleanup contracts.

## What Changes

- Require a non-empty exact four-component `platform_version` before any process resolution.
- Add an idempotent Go-owned exact-task unregister fallback with a bounded context independent of the canceled request.
- Keep cleanup fail-closed and exact-name scoped, with focused contract tests and Windows cross-build coverage.
- Remove the changed-surface unused Python import reported by review.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `qa-mcp-tool-endpoint-contract`: Remote TestClient launch rejects an omitted platform version.
- `qa-mcp-windows-host-agent-security`: Transient launch task cleanup remains exact and bounded on cancellation and error paths.

## Impact

This affects the Windows host-agent launch implementation and tests plus one Python lifecycle cleanup. It requires offline Go/Python verification and a Windows cross-build, but no live 1C action, infobase mutation, capture, Vanessa, EDT or metadata snapshot.
