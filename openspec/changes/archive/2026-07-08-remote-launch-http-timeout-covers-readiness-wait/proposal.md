## Why

The previous remote-client launch work made the Windows host-agent
`/testclient/launch` endpoint wait synchronously until it classifies TestClient
readiness. The Python `RemoteAgentBackend` still used the short default
`host_agent_timeout` for every HTTP call, so a real launch could time out on the
client before the host-agent returned its readiness verdict.

## What Changes

- Extend only the remote `/testclient/launch` HTTP request timeout so it covers
  the host-agent `timeout_seconds` readiness wait plus a small client-side
  margin.
- Keep ordinary host-agent primitive calls on the configured short default
  timeout.
- Add offline pytest regression coverage that observes the launch request
  timeout passed through `RemoteAgentBackend`.
- Record the real .205 before/after runtime evidence as the regression proof
  for this already-implemented fix.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `qa-mcp-tool-endpoint-contract`: remote `launch_test_client` must use an HTTP
  request timeout that covers the synchronous host-agent readiness wait and must
  retain the shorter default timeout for unrelated host-agent calls.

## Impact

- Touches Python manager code in
  `src/qa_mcp/protocol/display_backend.py`.
- Touches offline pytest coverage in `tests/test_display_backend.py`.
- Touches the OpenSpec endpoint contract for remote `launch_test_client`.
- Requires no new protocol frame claim, capture, replay template, BSL change,
  business-data mutation, runtime apply, Vanessa MCP, EDT/meta snapshot, or raw
  capture artifact.
