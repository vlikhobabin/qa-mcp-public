## Why

The V2 state model alone does not exercise the safe-action surface. The
fixture also needs explicit handlers for focus, activation, page switching,
popup/menu expansion and local row selection so those actions can be observed
without touching business data.

## What Changes

- Add allowlisted handlers for existing window/form activation, control focus,
  page switching, popup/menu expansion and local table-row selection.
- Update the local state markers and action counter when one of those handlers
  completes successfully.
- Reject text input, checkbox/value toggles, business command clicks and other
  mutating requests before they can change fixture state.
- Keep safe-action results local to the client fixture so downstream evidence
  can correlate the action request with the marker transitions.

## Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: V2 fixture behavior gains allowlisted safe-action
  handlers with fail-closed exclusions.

## Impact

- Client fixture BSL and managed form event handlers in `vanessa_client`.
- Evidence bundles that correlate action requests with marker transitions.
- Requires live 1C runtime and fixture evidence for verification.
