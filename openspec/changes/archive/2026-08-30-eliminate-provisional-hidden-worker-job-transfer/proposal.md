## Why

The unpublished S2 lifecycle duplicated its job handle from the worker into
the controller before the controller authenticated or admitted the response.
Cancellation in that interval could leave an unknown controller handle and
keep the exact child alive. Cleanup also discarded terminate failures and
accepted non-signaled wait statuses.

## What Changes

- Publish only the worker-local job handle in the authenticated atomic response.
- Let the controller duplicate from the exact worker and record the local
  handle before any cancelable admission work.
- Make cancellation at response/temp/duplicate boundaries converge before the
  controller returns, and report every terminate/wait failure.
- Keep the dormant authority, exact eight-path source scope and `300`-line
  production ceiling unchanged.

## Capabilities

### New Capabilities
- none.

### Modified Capabilities
- `qa-mcp-hidden-worker-lifecycle`: Replace provisional remote ownership with
  controller-initiated exact ownership and fail-closed cleanup status.

## Impact

Only the dormant Windows host-agent lifecycle, its focused tests, the existing
capability spec and sanitized delivery evidence change. There is no existing
non-test caller, public API, wire/profile/UI/input change, live 1C claim,
Docker mutation or runtime migration.
