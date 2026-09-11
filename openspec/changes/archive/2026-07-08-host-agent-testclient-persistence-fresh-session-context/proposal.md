## Why

The bounded-environment host-agent launch fix was proven insufficient on the
real .205 Windows host: `/testclient/launch` can report readiness while the
spawned `1cv8` process exits within seconds. The remaining differentiator is
the child process token/session context inherited from the Task Scheduler
host-agent, so TestClient launch must use a fresh interactive session token.

## What Changes

- Replace direct Windows `exec` spawning for host-agent TestClient launch with
  a `CreateProcessAsUserW` path that obtains the active interactive session
  token and starts the child on `winsta0\\default`.
- Preserve the bounded launch environment metadata and existing readiness
  classification: success still requires a live process and a listening TPort.
- Fail closed with structured launch diagnostics when an interactive user
  session token cannot be obtained or duplicated.
- Keep the Linux/all-in-one launch path unchanged.
- Retain Go unit coverage for session-token launch plumbing where it is
  testable offline, plus a Windows cross-compile check.
- Record the real Windows .205 persistence proof as a qa-mcp provider gap in
  this session because the required host is unavailable; do not claim runtime
  persistence was proven.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: host-agent TestClient launch must use a
  fresh interactive Windows session token on Windows, expose bounded
  launch-context metadata, and fail closed when the token/session launch
  context is unavailable.

## Impact

- Touches Windows host-agent launch code under
  `host-agent/windows-display-agent/`.
- Adds or updates Go tests for launch-context/session plumbing.
- Updates OpenSpec artifacts and the `qa-mcp-windows-host-agent-security` main
  spec after sync.
- Requires the real Windows .205 / [redacted third-party configuration] host for final persistence proof;
  that runtime proof is unavailable in this environment and will be recorded as
  a provider gap owned by `/opt/ai-dev-suite-for-1c/qa-mcp`.
