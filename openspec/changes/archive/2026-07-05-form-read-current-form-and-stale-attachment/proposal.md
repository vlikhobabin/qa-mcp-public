## Why

Tester feedback showed that `read_form_descriptor` and `read_table_cell` fail
with low-level ManagedForm GUID template errors when `open_link` is omitted, and
that stale `attached=true` state can survive after the TestClient endpoint is no
longer listening. Both failures make automation diagnose the wrong problem.

## What Changes

- Return a clear structured error when a form-read tool cannot infer the current
  ManagedForm GUID and needs `open_link`.
- Treat an attachment with `listening=false` as invalid for endpoint-touching
  tools instead of continuing toward a dead endpoint.
- Add action hints for restarting or re-attaching the TestClient, plus offline
  wrapper tests for these failure modes.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-tool-endpoint-contract`: endpoint-touching form-read tools must reject
  stale attachments and expose actionable `open_link` guidance instead of raw
  template errors.

## Impact

- Touches Python MCP wrapper behavior in `src/qa_mcp/mcp_server.py` and related
  protocol/tool tests.
- Requires offline pytest evidence in this Linux workspace.
- Windows/live form smoke remains useful but is not required for this Linux-only
  pass because the changed behavior is wrapper diagnostics and attachment
  gating, not a new protocol claim.
