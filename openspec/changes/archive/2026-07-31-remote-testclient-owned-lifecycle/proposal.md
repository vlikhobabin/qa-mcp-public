## Why

Remote-client mode can launch a Windows-host TestClient through the host-agent,
but the returned MCP handle is treated as unowned and `stop_test_client` is
still blocked as a local-only tool. The same qa-mcp provider must own cleanup
for processes it launches remotely, otherwise agents can create host processes
that they cannot stop.

## What Changes

- Add a provider-owned remote lifecycle handle for host-agent-launched
  TestClients.
- Route `stop_test_client` in remote-client mode through the configured
  host-agent instead of returning `local-boot-disabled-remote-client`.
- Add an authenticated host-agent stop endpoint that stops only the exact
  provider-owned launched process and returns an idempotent typed final state.
- Preserve attach-only behavior for manually started TestClients:
  `attach_test_client` remains unowned and cannot be stopped by qa-mcp.
- Cover launch, attach, stop, repeated stop, PID-only refusal, mismatched-handle
  refusal and unsupported lifecycle-stop host-agent refusal with offline Python
  and Go tests; retain Windows host-agent integration proof when the Windows
  host is reachable, or record a runtime provider gap.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-tool-endpoint-contract`: remote-client `launch_test_client` and
  `stop_test_client` lifecycle semantics change for host-agent-owned clients.
- `qa-mcp-windows-host-agent-security`: host-agent TestClient lifecycle endpoint
  requirements expand from launch/status to exact-process stop and idempotent
  final-state reporting.

## Impact

- Python manager/MCP code: `src/qa_mcp/mcp_server.py` and the remote display
  backend.
- Windows host-agent: `/testclient/stop` endpoint, exact launched-process
  tracking, and process termination/refusal behavior.
- Tests: focused `tests/test_mcp_server.py`, `tests/test_display_backend.py`,
  and `host-agent/windows-display-agent` Go tests.
- Runtime: live Windows 1C GUI proof is required for full acceptance when the
  authorized Windows host is reachable. No Vanessa MCP, EDT/meta snapshots,
  raw screenshots, raw runtime logs, credentials, or infobase contents are in
  scope for retained evidence.
