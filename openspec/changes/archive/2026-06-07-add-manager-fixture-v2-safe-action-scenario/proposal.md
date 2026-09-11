## Why

V2 safe-action evidence needs a dedicated capture scenario that separates
pre-read, action, post-read and recovery traffic. The existing manager fixture
V1 read-only route can join read-only case events, but it does not yet provide
an action-oriented scenario boundary for non-mutating UI actions.

## What Changes

- Add a `manager-fixture-v2-safe-action` capture scenario to the protocol
  tooling.
- Require the scenario to consume reviewed safe-action manifest rows before it
  starts capture or manager-runner execution.
- Record action phase events separately from bootstrap, background refresh and
  recovery events.
- Keep raw captures and generated runtime output under ignored
  `runtime/protocol-research/` paths.

## Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: The protocol corpus tooling gains a V2 safe-action
  capture scenario for manager fixture runs.

## Impact

- Protocol tooling under `tools/protocol-research/`.
- Protocol research docs under `docs/protocol-research/`.
- Requires Windows-native capture verification when implemented.
- Does not modify the client fixture surface or manager-side action execution.
