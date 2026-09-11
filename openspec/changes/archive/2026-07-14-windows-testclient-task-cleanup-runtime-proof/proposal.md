## Why

Independent review confirmed the Windows cleanup source fix but found its
retained T4 artifact predates that fix. The current common test also validates
helper strings without proving that production launch call sites still invoke
the cleanup boundary. Publication therefore lacks a source-bound Windows-native
proof for cancellation and cleanup-failure fallback behavior.

## What Changes

- Introduce a testable exact-task cleanup guard used by both production cleanup
  call sites.
- Add behavioral and source-call-site tests that turn red if explicit or
  deferred production cleanup is removed.
- Add an opt-in Windows-native scheduled-task integration scenario covering
  canceled-parent cleanup and fail-closed fallback retry.
- Preserve true solo startup when no registry URL is configured; the host token
  becomes the default bridge token only for enabled registration.
- Build a current source-bound host-agent artifact and retain normal T4 launch,
  Windows integration and exact cleanup evidence under one immutable root.

## Capabilities

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: exact transient task cleanup remains
  connected to production launch paths and is proven on Windows from the same
  source revision as the delivered host-agent artifact; absent registry URL
  still selects disabled solo registration.

## Impact

This affects the Windows host-agent cleanup implementation/tests, release
evidence and the QA delivery cards/manifests. It creates and removes only
randomly named QA-owned scheduled tasks and an exact staged test executable;
it does not mutate an infobase or publish a release.
