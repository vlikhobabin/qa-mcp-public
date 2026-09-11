## Why

I13 reached its exact authorized contour but the first tracked S4 candidate
exited before an observation receipt, while the protected unrelated scheduled-
task-set fingerprint changed without being targeted. Those two stops need a
bounded investigation before another certification attempt or correction can
be authorized.

## What Changes

- Reconfirm the unchanged published-I11 five-blob lineage and the exact I13
  platform, target, fixture and argv identities.
- Isolate the S4 pre-receipt exit and classify its boundary using bounded typed
  evidence only.
- Determine whether the task-set fingerprint change is harness behavior,
  independent system drift or an ownership violation without altering foreign
  tasks, or retain `NOT-VERIFIABLE` without inferring a cause when the bounded
  evidence cannot distinguish them.
- Restore the configuration state and remove only I14-owned execution state;
  prove each evidenced cleanup rerun is a no-op and explicitly classify any
  unavailable continuity or zero-state evidence as `NOT-VERIFIABLE`.
- Publish an investigation decision and successor authority, if needed. No
  protocol tool, Python manager, MCP provider, runtime configuration,
  product/test source or test instrumentation changes are authorized.

## Capabilities

### New Capabilities

- `qa-mcp-i13-s4-early-exit-and-task-topology-investigation`: Defines the
  evidence-only decision gate for the I13 S4 early exit and protected task-
  topology drift.

### Modified Capabilities

- None.

## Impact

Delivery requires the exact operator-authorized Windows/1C contour and may
create only exact-owned temporary task, stage,
process/job/desktop and transport state. The reviewed payload is limited to
bounded privacy-safe evidence, OpenSpec artifacts, board/dependency updates and
the authorized predecessor I13 handoff. It adds no behavior, authority, public
surface, wire field or product/test byte.
