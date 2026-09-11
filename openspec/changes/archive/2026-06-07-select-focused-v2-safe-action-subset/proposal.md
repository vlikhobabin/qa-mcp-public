## Why

The first V2 safe-action proof needs a tiny reviewed input set before any live
action is attempted. Selecting the subset up front prevents the proof from
accidentally broadening into button-like behavior or mutation work.

## What Changes

- Select one or two manager fixture V2 safe-action rows for the first focused
  proof, preferably `switch_page` first and `focus_element` second.
- Require every selected row to have the full V2 safety contract: target marker,
  pre-state, post-state, recovery expectation, action result markers,
  allowlisted family and `mutates_business_data=false`.
- Record rejected, deferred or unsupported candidate rows with reason, owner
  and residual risk.
- Produce a reviewed focused-subset manifest or compact selection summary for
  the downstream live capture change.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: The first focused V2 proof starts from a reviewed
  safe-action subset before live execution.

## Impact

- Protocol research docs and compact evidence under
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/`.
- Uses archived client V2 target-map, manager V2 catalog and tooling manifest
  outputs.
- Requires offline review and manifest validation only; no live 1C runtime,
  Vanessa MCP or EDT/meta snapshot is required by this selection change.
