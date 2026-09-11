## Why

The V2 safe-action scenario needs a machine-readable manifest contract before
tooling can capture or report action rows safely. The current safety docs
define the row semantics, but the tooling needs a concrete validation surface
that can fail closed.

## What Changes

- Define a machine-readable V2 safe-action tooling manifest shape.
- Require `target_marker`, `pre_state`, `post_state`,
  `recovery_expectation`, `mutates_business_data=false`,
  `allowed_action_family` and `expected_action_result_markers`.
- Reject unsupported or incomplete rows before capture, reporting or manager
  runner execution.
- Document how manifest rows map to corpus rows and fixture target maps.

## Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: V2 safe-action tooling gains a fail-closed manifest
  validation contract.

## Impact

- Protocol tooling under `tools/protocol-research/`.
- Protocol research docs under `docs/protocol-research/`.
- Does not require live 1C runtime by itself; live capture remains downstream.
