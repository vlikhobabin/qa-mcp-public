## Why

The demo real-button pilot needs a single concrete target before any safety
classification or runtime action can be reviewed. Selecting the target as a
read-only planning step prevents the pilot from drifting into unknown business
button clicks.

## What Changes

- Select one visible button-like target from a demo configuration form for the
  pilot.
- Record the form path, element path, visible caption or marker, target owner,
  pre-state observations and reason the button is worth classifying.
- Record rejected or deferred demo buttons with reason, owner and residual risk.
- Produce a compact target-selection summary for the downstream safety
  classification change.
- Do not click the button or create protocol acceptance evidence in this
  change.

## Capabilities

### New Capabilities

### Modified Capabilities
- `qa-mcp-protocol-lab`: Demo real-button pilots start from an explicit,
  read-only target selection before safety classification or execution.

## Impact

- Protocol research docs and compact planning evidence under
  `.artifacts/openspec/select-demo-safe-button-target/<run-id>/`.
- May use live 1C read-only UI inspection, Vanessa form tree evidence or
  EDT/meta context for target discovery.
- Does not require a live click, protocol capture, Python manager replay or
  accepted mapping output.
