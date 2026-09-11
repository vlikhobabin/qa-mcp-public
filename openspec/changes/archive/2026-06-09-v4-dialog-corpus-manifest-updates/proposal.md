## Why

V4 scenario evidence needs a machine-readable manifest and publication
contract before captures can be reviewed consistently. Dialogs, expected
errors and waits add result types that V2/V3 manifest rows do not fully name.

## What Changes

- Define a fail-closed V4 corpus manifest shape for warning, question, modal,
  expected-error and bounded-wait rows.
- Require target marker, scenario family, expected text or diagnostic marker,
  bounded duration where applicable, pre-state, action, result and recovery
  expectations.
- Extend evidence publication expectations so expected errors are not mixed
  with infrastructure failures.
- Keep raw captures, platform logs and generated replay payloads under ignored
  runtime paths.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: V4 corpus rows gain explicit manifest and evidence
  publication requirements for dialog, wait, error and recovery scenarios.

## Impact

- Protocol research docs and corpus manifests.
- Protocol tooling or reporter changes may be needed during implementation.
- No 1C runtime execution is required for this planning change, but later
  publication needs compact reviewed evidence from Windows-native runs.
