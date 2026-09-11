## Why

The V2 safe-action surface cannot be verified until the client fixture exposes
stable local state markers. The current V1 read-only fixture proves the shell,
but it does not yet define a resettable state model for focus, page, row and
last-action tracking.

## What Changes

- Add a fixture-local state model for `PF_LAST_ACTION`, `PF_ACTION_COUNTER`,
  `PF_SELECTED_PAGE`, `PF_SELECTED_ROW`, `PF_FOCUSED_ELEMENT` and
  `PF_RESET_STATE`.
- Make the state model resettable back to the V1 baseline after each safe
  action.
- Keep the state model transient and fixture-local so no business objects,
  registers or external services are mutated.
- Provide observable marker transitions that downstream safe-action evidence
  can correlate with frame ranges and recovery checks.

## Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: V2 fixture behavior gains a resettable local state
  model for safe actions.

## Impact

- Client fixture BSL and managed form code in the `vanessa_client` infobase.
- Protocol research docs and later compact evidence bundles.
- Requires live 1C runtime evidence for verification.
