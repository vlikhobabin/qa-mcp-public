## Why

Two pending rows have broad joined windows that are too wide for accepted
protocol mapping claims: `tm-v1-diag-window-get-form-path` spans frames
`26..106`, and `tm-v1-button-inert` spans frames `131..390`. These rows need
isolation before their semantic markers or endpoint contracts can be accepted.

## What Changes

- Add or use a focused capture/replay route that isolates broad pending rows.
- Preserve smaller frame windows or explicit evidence that isolation is still
  blocked.
- Keep broad rows non-accepted until the narrowed range can be matched by
  replay/direct-probe proof.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-protocol-lab`: broad manager fixture V1 pending windows require
  isolation before accepted promotion.

## Impact

- May touch manager fixture harness selection, capture runner timing/boundary
  handling, reporter range validation and tests.
- Requires live or replay evidence from the current cleanup route or a
  compatible focused rerun.
