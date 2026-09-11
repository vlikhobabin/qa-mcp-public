## Why

On published `289f432`, a real registered bound `click_command` reaches its native
handler with no session or attachment. The common operation entrypoint also
falls through to execution for names absent from the positive-result catalog.
FIX-01/FIX-02 are complete; enforce admission across the actual native surface.

## What Changes

- Separate route admission from positive output-schema membership.
- Explicitly classify every registered tool; unknown bound native routes fail closed.
- Reject invalid bound route state before hidden display callbacks, endpoint probes,
  native handlers or protocol sends, preserving application state.
- Preserve exact admitted routing, lifecycle-specific guards, pure/provider tools
  and explicit unbound compatibility with real-factory regression controls.

## Capabilities

### New Capabilities
None.

### Modified Capabilities
- `qa-mcp-target-bound-evidence-cleanup`: comprehensive native admission independent of result schemas.

## Impact

Python composition and operation policy in `mcp_server.py`, `core/operations.py`
and `core/application.py`; focused public-boundary tests and consumer docs.
No dependencies, protocol changes, native observation, BDD executor refactor,
ChangeRail development or live effects. Correcting previously permissive invalid
bound calls is intentional; public tool names and valid unbound usage remain.
