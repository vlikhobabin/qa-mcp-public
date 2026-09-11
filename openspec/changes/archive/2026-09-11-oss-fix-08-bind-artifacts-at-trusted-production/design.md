## Context

Published `15ab9a7` still promotes raw executor paths with scope.record after
execution. The actual registered bound capture accepts an existing in-root file
with all-zero SHA metadata. Source hashes match the retained synthetic reproduction.
The default screenshot handler also reads/deletes a provider-returned path without
proving that it is the destination allocated for this invocation.

## Goals / Non-Goals

Bind current evidence to trusted production, verify path/content, preserve exact
failure ordering, useful unbound capture and isolated cleanup. No live runtime,
protocol frames/replay claim, storage migration, signing service, configurable
producer/schema registry, hostile arbitrary Python sandbox or ChangeRail change.
Capture sources are temporary synthetic backend bytes; native frame ranges,
dynamic wire fields and replay are inapplicable.

## Decisions

1. Keep receipt authority application-owned. A private request-local scope carrier
   can expose the current operation scope to the source-owned screenshot handler.
   The handler registers validated production; execute_operation consumes those
   current records and MUST NOT mint authority by iterating raw result paths.
   Post-hoc containment is insufficient because it proves location, not production.
2. Allocate a fresh current destination within the admitted root before invoking
   the backend. Validate its returned path against that destination before reading,
   registering or deleting. Reject symlinks, borrowed old paths and wrong output;
   preserve unrelated provider-returned files. Validate exact metadata types before
   any callback/coercion. Do not expand public schemas or caller-controlled authority.
3. Bind the current record to actual canonical path and content hash; full_local
   verifies current bytes/path identity at normalization. Sanitized registers owned
   production before deletion and verifies retained production metadata, exposing
   no raw path/image. Cleanup failures stay non-success; only owned files are removed.
   Hash validation is a statement at completion, not perpetual filesystem immutability.
4. Explicit EvidenceScope.record is a trusted low-level API. Preserve its deliberate
   use for core fixtures and document strengthened actual-file-hash semantics. Raw
   ArtifactReference data alone cannot invoke that authority. Preserve exact stale,
   foreign, lookalike, class, bounds and artifact-before-receipt validation controls.
5. Use tests/test_trusted_artifact_production.py for every C1-C3 acceptance family.
   Positive tests MUST use actual default local and Windows-host application factories
   and registered capture handlers; substitute only external display/native boundaries.
   A custom executor is allowed for hostile result injection, never as default-producer
   proof. No module-wide schema/projection bypasses or weakened exact assertions.
6. C3 barriers overlap scopes in one ledger, with identical bytes/artifact IDs and
   different paths; then overlap distinct applications with both opposite policies.
   Pause sibling after production/registration, snapshot foreign bytes and records,
   finish the current scope and immediately compare while sibling remains paused.
   Release it only after proving current cleanup touched no foreign state. Exercise
   success/failure and same-callback carrier restoration so async task isolation cannot
   hide a missing reset. Assert exact destinations, results and backend call counts.
7. Deliberately unbound direct/standalone capture retains readable paths and legacy
   behavior from FIX-05. Bound guards, public serialization, fixed failure taxonomy,
   sizes and provenance remain intact. Public MCP and shared scenario entrypoints
   exercise raw-claim refusals; no real sockets, display or file outside tmp roots.

## Risks / Trade-offs

- Untrusted paths/hashes → validate producer destination, exact classes, current
  records and actual file hash; malformed artifact shape still precedes receipt errors.
- Concurrent authority/cleanup leak → request-local carrier, per-token records,
  barriers and immediate foreign inventory comparisons, success/failure reset controls.
- File mutation → check current bytes and symlink/path identity before full_local
  success; retained sanitized registration is only valid for its current operation.
- Cleanup external effects → delete only own synthetic/raw production; never borrowed
  backend paths. Retain sentinel files and exact per-invocation negative controls.
- Restart → no persisted ledger or new resumable state, stale records remain unusable.
- Publication → ordinary runner publication only; no release workflow change.

## Migration Plan

One native checkpoint, focused and affected offline/integration checks, independent
review, semantic spec sync and stock archive. No data migration or new dependencies.
A scoped product revert restores the prior code if necessary, retaining run evidence.
After final Result/Log and sync, collect current command receipts AND registered
C1-C3 typed proof using meaningful setup/action/assertion source spans and observed
verbose terminal nodes; file headers are not proof. Complete handoff without
stopping at partial evidence. Postarchive refresh continues the same reviewer thread.
Sync, handoff, archive, publication are outer stages, not prior task checkboxes.

## Open Questions

None blocking. Choose small source-owned internals within these contracts and
preserve all actual review attempts; at most two ordinary independent sessions.
