## Why

The V2 tooling pipeline can validate and report safe-action rows, but live
proof is still gated because the manager fixture cannot execute reviewed
non-mutating actions. The manager harness needs a runner that performs only
allowlisted actions against the client fixture.

## What Changes

- Implement manager-side commands for allowlisted V2 safe-action families.
- Execute each action only after catalog validation succeeds.
- Support focus/activate existing element, activate existing window/form,
  switch fixture page, select local table row and expand/collapse safe menu or
  group targets.
- Fail closed when a target is missing, disabled, mutating, unsafe or cannot
  be inspected after the action.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: Manager fixture V2 can execute reviewed
  non-mutating safe-action candidates against the client fixture.

## Impact

- Manager fixture BSL/harness commands in the `vanessa_manager` or manager
  fixture runtime.
- Windows-native live 1C runtime and Vanessa/TestClient evidence for
  verification.
- Does not accept protocol mappings without later candidate evidence review.
