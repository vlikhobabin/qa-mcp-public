## Why

Several pending rows appear to use too-strict or wrong expected markers, while
two replayed rows show current-run marker mismatches. The project needs an
evidence-gated marker contract decision before changing the manifest or
promoting rows.

## What Changes

- Reconcile candidate expected-marker corrections for rows identified in the
  pending classification.
- Decide whether endpoint semantics are title/form identity, target identity,
  row identity, group identity or still wrong endpoint.
- Apply manifest/catalog corrections only when current-run proof validates the
  corrected semantics.
- Keep mismatched rows pending with retained evidence when proof is not enough.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-protocol-lab`: marker contract corrections for manager fixture V1
  pending rows are evidence-gated.

## Impact

- May touch manager fixture command catalog JSON, capture manifest generation,
  reporter validation and docs.
- May require BSL source review if the manager harness command catalog is
  updated in 1C source.
- Does not accept a row from manifest changes alone.
