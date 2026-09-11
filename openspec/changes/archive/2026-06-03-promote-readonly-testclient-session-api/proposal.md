## Why

After frame primitives have package ownership, the direct TCP session and
read-only query API can move from exploratory tooling into `qa_mcp.protocol`.
This gives future MCP/runtime work a reusable entrypoint for talking to a
running 1C TestClient without starting a 1C TestManager.

## What Changes

- Promote `TestClientSession` and read-only query result models into
  `src/qa_mcp/protocol/`.
- Expose package APIs for initial UI context, active window/form context, form
  summary and form-element details while preserving evidence status.
- Keep accepted mappings limited to active-window and active-form operations
  from current compact evidence.
- Add offline socket/renderer tests and an optional retained live read-only
  smoke plan for a running `/TESTCLIENT`.
- This change touches Python manager code and tests. Live 1C runtime is useful
  for final smoke evidence but the package must still verify offline first.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: Add requirements for a reusable read-only
  `TestClientSession` package API and evidence-status preserving query
  results.

## Impact

- `src/qa_mcp/protocol/`
- `tools/protocol-research/python_manager_client.py`
- `tools/protocol-research/python_manager_probe.py`
- tests under `tests/`
- optional compact live smoke evidence under `docs/protocol-research/evidence/`
