## Why

The manager V2 runner must fail closed before it can execute any UI action.
It needs a reviewed allowlisted action catalog that consumes the client fixture
V2 target map and names target, pre-state, post-state and recovery
expectations for each safe action.

## What Changes

- Define a manager-side V2 safe-action catalog or manifest for allowed action
  rows.
- Require the V2 safety fields from `safe-ui-action-scope.md`, including
  `mutates_business_data=false`, `allowed_action_family`, target marker,
  pre-state, post-state, recovery expectation and expected result markers.
- Reject incomplete, unsupported or mutating rows before manager execution.
- Keep excluded families such as text input, value toggles, business command
  clicks, writes and external side effects outside V2.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: Manager fixture V2 gains a fail-closed safe-action
  catalog contract before runner execution.

## Impact

- Manager fixture harness/catalog artifacts and protocol research docs.
- Later live 1C runtime and Vanessa evidence will be required to verify
  execution, but this catalog change can be validated offline first.
- Does not change Python manager protocol acceptance or MCP provider setup by
  itself.
