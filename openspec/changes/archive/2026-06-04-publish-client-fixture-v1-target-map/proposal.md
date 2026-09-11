## Why

The V1 fixture surface is only useful for protocol research when every `PF_*`
element can be targeted and reviewed consistently. A compact target map and
read-only corpus readiness evidence connect the EDT fixture source to future
frame ranges, normalized hashes and replay/probe results.

## What Changes

- Publish a reviewed V1 target path map for the fixture processor.
- Link each `PF_*` marker to element family, expected state, expected response
  markers and intended read-only case ids.
- Update the corpus planning artifacts or manifest inputs so the V1 fixture can
  drive later capture runs.
- Record read-only form analysis evidence and explicit gaps for missing or
  provider-dependent elements.
- Keep raw captures and runtime logs out of git; accepted protocol mappings
  remain deferred until capture/replay evidence exists.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require controlled fixture target maps and compact
  marker coverage evidence before V1 fixture rows are used for corpus capture.

## Impact

- Touches protocol research docs and compact evidence under
  `docs/protocol-research/`.
- May update fixture/corpus manifest inputs for read-only cases.
- Does not change 1C runtime behavior beyond using the V1 fixture form as a
  source of read-only target metadata.
- Does not promote any row to `accepted` without the existing corpus evidence
  contract: frame range, normalized hash, dynamic fields and replay/probe
  status.
