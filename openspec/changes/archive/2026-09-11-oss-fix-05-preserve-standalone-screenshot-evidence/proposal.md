## Why

On published `2a4c159`, both default and explicit screenshot calls through the
real standalone factory return a path whose file has already been deleted.
The unbound application's default sanitized ledger is being mistaken for an
admitted project-bound screenshot retention policy.

## What Changes

- Preserve readable screenshot bytes returned by unbound standalone factories.
- Apply existing sanitized/full_local screenshot policy only in its actual
  admitted bound context, preserving bound privacy and evidence authority.
- Prove default/explicit output, both bound policy modes and truthful capture/
  cleanup failures through registered tools with a synthetic backend.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `qa-mcp-shared-core-extension`: standalone screenshot retention, bound policy partition and failure truthfulness through the shared factory.

## Impact

`src/qa_mcp/mcp_server.py`, a focused factory screenshot test module and direct
consumer documentation. No wire, display routing, generic artifact receipt,
new retention policy, dependency, live runtime or ChangeRail changes. Existing
bound contracts and later FIX-06/FIX-08 scopes remain separate.
