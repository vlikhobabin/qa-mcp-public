## Why

Project launch and attach still expose legacy target resolution and can create a
session from endpoint reachability alone. Admission must use the resolved
profile and establish exact identity before any later read, display or cleanup.

## What Changes

- Bind project-mode launch, attach and status to the provider profile.
- Record immutable target, session, generation, ownership and lifecycle identity
  in attachment state.
- Block caller retargeting, unavailable targets and unproven observations before
  Apache, Xvfb, platform, host-agent or protocol side effects.
- Validate the raw remote launch observation before normalization: positive
  integer PID/TPort and an explicit non-empty `lifecycle_id` are required in
  `client_target`, and the top-level result, client target and lifecycle handle
  must agree exactly before a session exists.
- Preserve unbound standalone lifecycle compatibility.

## Capabilities

### New Capabilities
- `qa-mcp-target-bound-testclient-lifecycle`: Project-target admission for
  TestClient launch, attach and status.

### Modified Capabilities
- None.

## Impact

Python MCP lifecycle and offline lifecycle tests change. Existing protocol
mappings are reused; no protocol-research claim, capture, Vanessa MCP or
EDT/meta snapshot is required. An exact-wheel Windows offline admission check
is required here; native live runtime certification remains deferred to
OSS-04F.
