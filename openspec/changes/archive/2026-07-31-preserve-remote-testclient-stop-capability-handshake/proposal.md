## Why

The lifecycle-stop safety check already accepts either the current
`0.1.10-testclient-lifecycle-handle` host-agent or a future protocol-compatible
host-agent that explicitly advertises lifecycle-handle stop support. The
Python `/version` handshake currently drops advertised capabilities, so that
future-compatible path cannot work.

## What Changes

- Preserve a bounded, validated `capabilities` field from
  `RemoteAgentBackend.handshake()` when `/version` returns either a list of
  capability names or a mapping whose values are explicit booleans.
- Keep the current lifecycle-stop host-agent version supported.
- Keep legacy/protocol-compatible PID-only stop routes refused before posting
  `/testclient/stop`.
- Add offline regression tests for both the direct support helper and the real
  `_json()` -> `handshake()` -> `stop_test_client()` path.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-tool-endpoint-contract`: remote-client stop compatibility now requires
  `/version` capability passthrough so explicit future lifecycle-stop support
  can authorize `/testclient/stop`.

## Impact

- Python manager code: `src/qa_mcp/protocol/display_backend.py`.
- Tests: focused offline coverage in `tests/test_display_backend.py`.
- Runtime: no live 1C runtime, Vanessa MCP, EDT/meta snapshots, Windows
  host-agent rebuild, or raw capture evidence required; this is a pure Python
  handshake and routing compatibility fix.
