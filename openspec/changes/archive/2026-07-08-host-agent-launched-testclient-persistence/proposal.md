## Why

The remote host-agent launch path now constructs the right 1C `/TESTCLIENT`
command, but on the .205 Windows host the child process exits within seconds
when it inherits the long-running scheduled-task host-agent context. The launch
tool must either deliver a usable client or report a precise not-ready result;
today it can over-report readiness and leave downstream protocol tools chasing
an unavailable TPort.

## What Changes

- Repair the Windows host-agent TestClient spawn context by constructing a
  bounded child environment with explicit user-profile directories instead of
  blindly inheriting the scheduled-task agent environment.
- Make `/testclient/launch` wait for process liveness and TPort reachability
  during the launch window and return structured early-exit or not-listening
  diagnostics instead of `ok:true` success for an unusable client.
- Keep `/testclient/status` honest by reporting process liveness when a PID is
  supplied alongside TPort state.
- Tighten Python remote-client launch handling so `launch_test_client` does not
  report `attached:true` unless the host-agent result and container TPort probe
  agree that the client is usable.
- Preserve the existing Linux/all-in-one launch path and keep runtime proof
  requirements explicit: the real Windows .205 persistence proof is required
  for acceptance, but is recorded as a provider gap in this session because the
  host is unavailable.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: host-agent TestClient launch and status
  endpoints must use a bounded GUI child environment and return honest
  readiness/liveness classifications.
- `qa-mcp-tool-endpoint-contract`: `launch_test_client` in remote-client mode
  must propagate host-agent not-ready/early-exit diagnostics and only attach
  after real liveness is established.

## Impact

- Touches Windows host-agent Go launch/status code under
  `host-agent/windows-display-agent/`.
- Touches Python MCP remote-client lifecycle handling in `src/qa_mcp/mcp_server.py`
  and the remote host-agent client in `src/qa_mcp/protocol/display_backend.py`.
- Adds focused offline Go and pytest coverage for readiness classification,
  early-exit handling, launch-context environment construction, and unchanged
  local/Linux launch behavior.
- Requires live Windows .205 / [redacted third-party configuration] runtime persistence proof for final
  runtime acceptance. That proof is not available in this session and must be
  recorded as a qa-mcp provider gap, not fabricated.
