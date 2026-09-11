## Why

OSS-04D and its linked replacement each exhausted two independent-review
rescues while repeating the same evidence-sanitization defects. A reviewed
boundary decision is required before more implementation because the failed
payload reached its 300-line ceiling without a closed ownership or admission
model.

## What Changes

- Record the exact failure lineage and classify the repeated defects by root
  cause rather than by individual leaked spelling or address.
- Define a typed public serialization boundary that separates core-trusted
  provenance from executor-controlled values, errors and artifacts.
- Define structured field and URL admission, bounded exception containment,
  evidence-policy behavior and an adversarial verification matrix.
- Produce an ordered successor implementation handoff and declare whether a
  separate published complexity authorization is required.
- Update the OSS-04 roadmap and downstream dependency without implementing or
  publishing either failed runtime payload.

## Capabilities

### New Capabilities

- `qa-mcp-operation-evidence-boundary-design`: reviewed investigation,
  architectural decisions, verification matrix and successor authorization
  contract for the public operation-evidence boundary.

### Modified Capabilities

- None. Runtime requirements remain unpublished until a successor implements
  and independently verifies the approved design.

## Impact

This change touches OpenSpec workflow, board metadata and durable design
documentation only. It does not change Python manager code, MCP provider setup,
protocol tools or runtime-lab configuration. It needs retained offline review
evidence but no live 1C runtime, Vanessa MCP, Windows execution, EDT/meta
snapshot or business-data mutation.
