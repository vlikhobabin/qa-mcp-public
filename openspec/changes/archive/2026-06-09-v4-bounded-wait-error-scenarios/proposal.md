## Why

After the V4 dialog state model exists, the fixture needs deterministic
handlers for warnings, questions, expected errors and bounded waits. These
scenarios give protocol research controlled complex UI behavior without
introducing business workflow automation.

## What Changes

- Add fixture-local warning and question scenarios with stable text markers.
- Add fixture-owned modal open/close scenarios with stable lifecycle markers.
- Add controlled expected-error scenarios that return diagnostic markers.
- Add bounded wait/progress scenarios with observable state and a fixed maximum
  duration.
- Keep all scenarios local to the fixture and resettable to the V1 baseline.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: V4 fixture behavior gains deterministic dialog,
  expected-error and bounded-wait scenario requirements.

## Impact

- Client fixture BSL, managed form commands and fixture-owned modal form
  surface in the `vanessa_client` infobase.
- Later manager-runner and capture evidence that consumes V4 scenario markers.
- Requires live 1C runtime, Vanessa UI evidence and BSL/EDT checks during
  implementation; this planning pass does not execute those scenarios.
