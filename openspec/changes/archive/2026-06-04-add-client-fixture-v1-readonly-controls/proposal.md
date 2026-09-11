## Why

Once the fixture processor shell exists, V1 needs a broad static control
surface so protocol research can cover common form element families without
returning to EDT for each new read-only case. The current dashboard-based
fixture leaves `Button`, `Table`, `CommandBar`, `Page`, `Label` and `CheckBox`
as gaps.

## What Changes

- Populate the V1 fixture form with stable read-only/control-family elements
  and unique `PF_*` markers.
- Add deterministic fixture values for string, number, date, checkbox,
  choice/radio, table, button, command bar, label, group and pages controls.
- Include enabled, disabled, read-only and visible-state variants where safe.
- Keep every element local to the fixture form and independent from business
  data.
- Preserve action and mutation semantics as out of scope: controls may exist
  and expose properties, but clicks/input/page switching are not accepted
  protocol mappings in this change.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require the V1 fixture form to expose a broad,
  stable read-only control surface with unique markers for corpus targeting.

## Impact

- Touches managed form layout, form attributes and possibly form initialization
  BSL in the `client` EDT target.
- Requires EDT validation and read-only runtime UI evidence that the expected
  `PF_*` families are visible or inspectable.
- Does not update Python protocol templates, accepted mappings or manager
  harness behavior by itself.
- Raw UI evidence and runtime logs remain outside git; compact reviewed
  summaries can be stored under `docs/protocol-research/evidence/`.
