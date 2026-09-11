## Why

The consumed S4-R1 confirmation retained only the umbrella diagnostic
`first_window_inventory/first_window_inventory_failed` after the published
liveness-fenced observation change. That pair does not reveal whether the
pre-fence refused, the inventory operation failed, the post-fence changed, or
the hidden/default isolation composite refused, so another behavioral
correction is not evidence-bounded.

## What Changes

- Publish a privacy-safe source/evidence analysis of the exact first-inventory
  observation boundary and the information lost by its current diagnostic
  projection.
- Decide one minimal successor authorization: a later separate change may add
  behavior-neutral, allowlisted cause classification at the existing private
  S4 inventory seam plus hostile offline tests.
- Keep that authorization below all runtime behavior, live confirmation,
  retry, target, S7 and real-configuration authority boundaries.
- Touch only OpenSpec workflow artifacts and protocol-research documentation;
  do not change protocol tools, Python manager/MCP code, Go production/tests,
  provider setup or runtime lab configuration.

## Capabilities

### New Capabilities
- `qa-mcp-hidden-desktop-inventory-observation-decision`: Defines the evidence
  limit, exact cause-classification successor seam, hostile oracle and
  fail-closed authority ceiling for the retained first-inventory refusal.

### Modified Capabilities
- None.

## Impact

This decision uses only retained privacy-safe confirmation JSON and offline
tracked Go-source analysis. It requires no live 1C runtime, Vanessa MCP,
EDT/meta snapshot, SSH session, Windows task, disposable probe, real
configuration access or cleanup operation. The blocked S4-R1 payload and all
foreign S7, fixture, OSS-07 and OSS-08 paths remain outside the change.
