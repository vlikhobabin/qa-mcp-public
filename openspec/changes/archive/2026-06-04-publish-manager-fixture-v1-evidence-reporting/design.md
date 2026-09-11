## Context

Manager V1 will produce raw proxy traffic and side-channel event logs. Those
runtime outputs are necessary for research but too large and environment-bound
for reviewed documentation. The project needs compact summaries that preserve
the evidence chain without claiming more protocol knowledge than the run
proved.

## Goals / Non-Goals

**Goals:**

- Define a reviewed manager V1 evidence summary under
  `docs/protocol-research/evidence/`.
- Report command catalog coverage, run id, output files, bootstrap status and
  command result status.
- Report frame-join status for each command using proxy chunk counters or an
  explicit unresolved reason.
- Update the evidence index and related docs with compact links.

**Non-Goals:**

- No raw capture, platform log or full event-log publication.
- No accepted mapping promotion without normalized frame evidence and
  replay/direct Python-manager proof.
- No modification of historical corpus rows in place.

## Decisions

1. Publish compact Markdown plus optional machine-readable JSON summaries.
   Rationale: Markdown supports review, while JSON preserves deterministic
   checks for command counts and join status.

2. Keep frame joins statusful.
   Rationale: a command can be `joined`, `partial`, `unresolved`, `timeout` or
   `blocked`; unresolved joins are useful follow-up evidence and must not be
   hidden.

3. Treat manager V1 evidence as corpus input, not accepted protocol mapping.
   Rationale: accepted mappings still require normalized hashes, dynamic field
   evidence and replay/probe confirmation.

## Risks / Trade-offs

- Reviewed summaries may omit details needed for later low-level debugging.
  Mitigation: link to ignored runtime run id and list exact source files
  without copying payloads.
- Frame join status may be partial on the first runs. Mitigation: record
  unresolved reasons and owner route instead of blocking all documentation.
- Evidence index churn can grow quickly. Mitigation: add one compact entry per
  reviewed manager V1 run, not one entry per command.

## Migration Plan

1. Add the evidence summary and frame-join report structure.
2. Generate a summary from the first manager V1 capture run.
3. Validate JSON/Markdown structure and update the evidence index.
4. Defer accepted mapping publication to later normalizer/replay changes.

## Open Questions

- Whether the frame-join report should live beside manager V1 summaries or in
  the existing corpus-comparison evidence tree.
- Which unresolved join statuses should block `$opsx-pub` versus remain
  documented residual risk.
