## Why

After pending rows are probed, isolated and reconciled, the project needs one
reviewed cleanup state that states accepted/pending counts and whether manager
fixture V1 read-only coverage unblocks V2 safe-action acceptance.

## What Changes

- Regenerate the manager fixture V1 cleanup live-join report with all retained
  accepted and non-accepted summaries.
- Publish final accepted/pending counts and V2 readiness.
- Update protocol research docs and evidence index.
- Keep raw captures and generated replay output under ignored runtime paths.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-protocol-lab`: pending-row promotion work is published as a reviewed
  V1 read-only readiness state.

## Impact

- May touch reviewed evidence, protocol research docs, evidence index and
  OpenSpec specs.
- Does not implement new probes by itself; it consumes retained summaries from
  prior changes.
