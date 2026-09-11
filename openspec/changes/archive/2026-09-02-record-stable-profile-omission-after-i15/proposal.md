## Why

Published I15 exhausted its one authorized canary without a typed Session-1
receipt or candidate invocation, so the roadmap's card-405 release gate now
needs an explicit stable-profile omission decision before OSS-07 can begin.
The current roadmap and handoff cards also contain stale post-I15 paths, counts
and an incorrect claim that OSS-07 is already planned.

## What Changes

- Record the published-I15 outcome and omit `open_external_processor` from the
  declared stable release support profile and public support matrix until a
  separately reviewed future qualification publishes. The unchanged
  code-level `standalone` catalog remains explicitly pre-stable inventory, not
  a stable-support claim.
- Preserve the dormant implementation, tests, tracked EPFs, runtime authority
  and published foundations unchanged; preserve I13 active, unarchived and
  uncertified, with S4-R1 and S7 incomplete.
- Reconcile the OSS-06 parent, S4-R1 parent, I13, S7, roadmap, published I15
  card and OSS-07 handoff with actual `origin/main` board state, including the
  I15 `4.done` path and nine-entry evidence count.
- Record OSS-07 as the next separate backlog card after this decision
  publishes and bind the operator-approved `Apache-2.0` choice without
  creating OSS-07 OpenSpec artifacts or implementation.
- Touch only evidence/docs/spec/board/OpenSpec workflow surfaces. No live 1C,
  Vanessa MCP, EDT/meta snapshot, protocol tool, Python manager, MCP provider,
  runtime lab, product/test, fixture, tracked EPF or license-path change is
  required or authorized.

## Capabilities

### New Capabilities

- `qa-mcp-stable-profile-omission-after-i15`: Defines the evidence-bound
  card-405 omission decision, preserved incomplete lineage and OSS-07 handoff.

### Modified Capabilities

- None.

## Impact

The reviewed payload is limited to one bounded decision evidence pair, the new
decision spec, the archived change artifacts and exact affected board/public
support documentation. It removes no source or public API and grants no retry,
qualification, live-contour, candidate-action or OSS-07 implementation
authority.
