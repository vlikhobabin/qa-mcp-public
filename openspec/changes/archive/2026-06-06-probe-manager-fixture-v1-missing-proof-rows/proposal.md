## Why

Five manager fixture V1 pending rows were not attempted in the previous review
because no fresh endpoint was available. They need focused current-run replay
or direct-probe evidence before they can be promoted, corrected, or retained
with a stronger blocker.

## What Changes

- Probe `tm-v1-diag-command-interface-dump`,
  `tm-v1-diag-window-children`,
  `tm-v1-diag-window-find-form-marker`,
  `tm-v1-diag-window-get-form-path` and `tm-v1-form-summary`.
- Retain positive and negative probe summaries with current cleanup identity.
- Keep rows pending when proof is absent, mismatched, ambiguous or from the
  wrong endpoint.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-protocol-lab`: pending rows with missing proof are attempted through
  focused current-run replay or direct probes before promotion.

## Impact

- May touch replay/direct-probe tooling and tests under
  `tools/protocol-research/` and `tests/`.
- Requires runtime readiness from
  `prepare-manager-fixture-v1-pending-probe-runtime`.
- Does not weaken accepted mapping gates.
