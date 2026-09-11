## Why

V2 safe actions are acceptable only when the client fixture returns to a known
baseline after each action. The manager runner needs recovery verification
that labels cleanup traffic separately from the candidate action range.

## What Changes

- Define and verify recovery/reset behavior after each manager V2 safe action.
- Record recovery result markers, recovery frame ranges and residual-risk
  reasons.
- Fail closed when recovery is unavailable or cannot be proved.
- Keep the same action rerunnable after recovery.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: Manager fixture V2 safe-action runs gain explicit
  recovery verification and rerun expectations.

## Impact

- Manager harness recovery sequence and reviewed V2 evidence.
- Windows-native live runtime evidence and compact recovery proof.
- Does not introduce V3 mutation or business rollback semantics.
