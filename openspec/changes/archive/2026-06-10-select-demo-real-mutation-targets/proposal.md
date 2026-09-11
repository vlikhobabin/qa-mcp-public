## Why

The real-demo mutation pilot needs a small reviewed target set before any
business-data mutation can be attempted. Selecting targets as a read-only
planning step prevents the pilot from drifting into unbounded clicks across the
demo10413 configuration.

## What Changes

- Select one primary document-form mutation candidate from the prior demo-button
  work and one or two low-blast-radius catalog or processing candidates when
  they can be reviewed safely.
- Record form/object path, element path, visible caption or marker, operation
  family, expected mutation, recovery feasibility, owner and residual risk for
  each selected, rejected or deferred candidate.
- Require target-selection evidence to identify whether the target was observed
  through live 1C runtime, Vanessa UI tree, metadata/EDT context or prior
  compact evidence.
- Produce a target-selection summary for the downstream manifest-contract
  change.
- Do not click, write, save, post, delete, capture action traffic or accept any
  protocol mapping in this change.

## Capabilities

### New Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: Real demo mutation pilots start from explicit
  read-only target selection before manifest validation or guarded execution.

## Impact

- Protocol research planning evidence and compact selection bundles under
  `.artifacts/openspec/select-demo-real-mutation-targets/<run-id>/`.
- May use live 1C read-only UI inspection, Vanessa form tree evidence,
  metadata/EDT context or card-60 evidence.
- No live mutation, runtime capture, Python-manager replay or docs publication
  is required by this selection-only change.
