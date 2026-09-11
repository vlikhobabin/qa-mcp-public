## Why

`launch_test_client` is the operator-facing lifecycle tool, but in
remote-client mode it currently returns `local-boot-disabled-remote-client`
because the 1C GUI process must run on the Windows host. That leaves the agent
unable to recover when the host TestClient is missing or has exited.

## What Changes

- Add a host-agent-mediated TestClient launch path for remote-client mode.
- Extend the Windows host-agent with an authenticated, detached TestClient
  launch/status boundary that starts `1cv8 ENTERPRISE ... /TESTCLIENT -TPort`.
- Wire `launch_test_client` in remote-client mode to call the host-agent path,
  wait for the target TPort, remember the attached endpoint, and return
  PID/port/status metadata.
- Preserve local Linux/Xvfb launch behavior for non-remote-client contours.
- Improve the remote-client fallback diagnostic so a missing host-agent path
  returns the exact runnable host command with the resolved TPort, user and
  connection string, while redacting the password value.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `qa-mcp-tool-endpoint-contract`: `launch_test_client` no longer behaves as a
  local-only tool in remote-client mode when host-agent launch is configured;
  it must launch or re-establish the host TestClient through the host-agent and
  keep structured fallback diagnostics.
- `qa-mcp-windows-host-agent-security`: the host-agent gains an authenticated,
  detached TestClient launch/status endpoint with bounded command construction,
  launch metadata and fail-closed validation.

## Impact

- Touches Python manager/MCP lifecycle code in `src/qa_mcp/mcp_server.py`,
  `src/qa_mcp/protocol/lifecycle.py`, and remote host-agent client code.
- Touches Windows host-agent Go code under `host-agent/windows-display-agent/`.
- Touches host-agent and remote-client documentation.
- Does not add native TestClient protocol frame claims, raw protocol captures,
  1C metadata changes, BSL changes, Vanessa MCP dependencies, EDT/meta
  snapshots or live business-data mutation. Verification is offline Python/Go
  coverage, OpenSpec validation, matrix evidence, and a retained Windows-host
  runtime gap or smoke transcript depending on host availability.
