## Why

After `attach_test_client` records an active TestClient endpoint, many endpoint-touching MCP tools still default to `127.0.0.1:15381`. That creates split-brain sessions where reads can target the attached client while actions and replay helpers target another or dead client.

## What Changes

- Add one shared MCP tool wrapper/decorator for endpoint-touching TestClient tools.
- Make wrapped tools resolve the active attached endpoint when `host` and `port` are omitted.
- Resolve capture directories and return structured tool errors from one envelope.
- Preserve existing structured write/replay errors such as retarget and send-timeout results instead of flattening them.
- Add the local-boot guard to `measure_scenario` so remote-client mode returns the same structured "not served here" result as other local boot tools.

## Capabilities

### New Capabilities
- `qa-mcp-tool-endpoint-contract`: MCP TestClient tools consistently honor attached endpoints and local-only boot boundaries.

### Modified Capabilities
- none

## Impact

Touches Python manager/MCP provider code in `src/qa_mcp/mcp_server.py` and focused offline tests. This does not require live 1C runtime, Vanessa MCP, EDT/meta snapshots, or new protocol capture evidence; the behavior is verified with monkeypatched connectors and tool-registry tests.
