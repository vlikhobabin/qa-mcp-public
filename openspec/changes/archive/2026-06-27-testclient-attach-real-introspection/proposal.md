## Why

The prior attach card proved launch diagnostics and an external endpoint handle, but attach still behaves like a
status shim for the tools that matter. A TestClient launched out-of-band can be probed as listening, yet
`read_form_descriptor` may still return an empty descriptor for an existing form because the replay-backed tools
create fresh sessions without any reusable attached-client context or attach-specific diagnostics.

## What Changes

- Add a real attached-client session route for replay-backed MCP tools so `attach_test_client` can establish a
  reusable endpoint context instead of only returning status.
- Route descriptor, value-read, write and scenario session factories through the shared attached-session resolver
  while preserving the explicit `host`/`port` override path.
- Replace silent empty descriptor results from an attached endpoint with either non-empty live form evidence or a
  bounded attach/bootstrap diagnostic that names the failed phase.
- Add offline tests that prove descriptor/write tools use the attached endpoint route and retain non-owned cleanup
  semantics.
- Retain read-only live evidence against an out-of-band TestClient when Linux runtime preflight succeeds; keep
  mutation evidence behind the existing write-safety and recovery policy.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: Attached TestClient endpoints must be usable by real replay-backed introspection and
  write/session tools, not only lifecycle status probes.

## Impact

- Affected code: `src/qa_mcp/protocol/lifecycle.py`, `src/qa_mcp/mcp_server.py`, protocol session factories and
  focused lifecycle/MCP tests.
- Affected MCP surface: `attach_test_client`, `read_form_descriptor`, `read_form_value`, write helpers and scenario
  runners that currently instantiate `TestClientSession(host, port)` directly.
- Runtime: offline tests are required first. Live proof requires the qa-mcp Linux runtime preflight and a free
  `vanessa_client` TestClient port; the live gate should run read-only descriptor evidence before any write proof.
- Not in scope: new protocol frame families, raw capture publication, replacing existing replay templates, killing
  externally owned 1C sessions, or broad host-agent/display work.
