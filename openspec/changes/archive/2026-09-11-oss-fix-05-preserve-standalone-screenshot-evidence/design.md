## Context

On published `2a4c159`, real unbound factory capture_screenshot calls with both
default and explicit output return paths that were deleted. The synthetic
baseline is retained in `.runtime/qa-roadmap/oss-00/fix-05-planning/reproduction.json`.
_capture_screenshot_handler applies ledger.policy == sanitized without checking
whether that policy belongs to an admitted runtime_target. CLI uses this factory.
FIX-04C already isolates filesystem roots; no root repair belongs here.

## Goals / Non-Goals

Preserve useful standalone screenshot outputs while retaining admitted bound
privacy, retention and truthful failure. One small complete policy partition.
No new display transport, screenshot format, target observation, retention TTL,
generic artifact-production trust model or error taxonomy. FIX-06 owns broader
display verdict translation and FIX-08 generic artifact provenance. No live
screenshot, real 1C/Windows effects, credentials or ChangeRail development.

## Decisions

1. Scope the existing raw-image deletion to the actual project-bound policy
   context. Do not change the global ledger default or treat unbound behavior as
   permission for bound full_local retention. Keep one producer/handler.
2. Test the real registered capture_screenshot through create_mcp_server and
   the default executor. Fake only the screenshot backend/filesystem failure
   boundary; do not bypass _capture_screenshot_handler or replace the executor
   in positive controls. Direct legacy calls are a separate compatibility row.
3. Put complete acceptance controls in tests/test_screenshot_retention.py so
   every typed condition can select its actual relevant nodes from one declared
   selector. Reuse existing admitted target/session fixture patterns when useful.
   C2 must have a valid current attachment/session/generation and real admitted
   sanitized/full_local profile, not an unbound context named bound.
4. C1 covers default, explicit relative and absolute paths; assert exact bytes,
   truthful path/size and useful direct compatibility. C2 records actual backend
   destinations, final file inventory, exact digest and absence of raw path/UI
   secrets in bound public DTO. Distinguish image removal after successful
   sanitized capture from retained image plus failure when unlink is rejected.
5. For C3, create unrelated sentinel files and snapshot their bytes before EACH
   capture/cleanup failure; compare immediately after. Exercise controlled
   backend exception, missing evidence and failed required unlink. A failure
   outcome is not evidence that privacy cleanup succeeded. Do not implement the
   separate generic artifact trust redesign to satisfy unrelated hostile-producer
   cases outside this card's capture/cleanup failure scope.
6. Retain a meaningful sensitivity control without product edits: reintroducing
   unbound deletion in a test-only wrapper must fail the standalone retained-file
   assertions; bypassing sanitized cleanup must fail the bound privacy control.
   Scope every fixture/control to its own tmp_path. Preserve actual expected
   failure logs and source identities separately from passing proof.

## Risks / Trade-offs

- Input safety/privacy: changing the ledger default could expose bound images.
  Preserve admitted policy and verify both real bound modes independently (C2).
- File mutation/external effects: deletion or cleanup failure can lie about
  output or affect unrelated files. Use exact per-operation sentinel inventories,
  safe temp files and injected unlink failure; no live backend invocation (C3).
- Standalone compatibility: a sanitized ledger alone is not project admission.
  Real unbound factory and explicit direct controls prove the partition (C1).
- No new shared state, restart, protocol, business-data or publication behavior.
  Existing context isolation and final native qualification remain separate.

## Verification Matrix

| Condition | Observable proof | Real / fake boundaries |
| --- | --- | --- |
| C1 | Default/relative/absolute return path exists with exact captured bytes; direct compatibility; deletion regression fails | Real factory/default executor/handler and file reads; synthetic backend |
| C2 | Admitted sanitized deletion versus approved full_local retention; exact destination/digest; safe DTO | Real target/session/policy/serializer; synthetic screenshot files |
| C3 | Capture/missing-evidence/cleanup failures, no successful artifact, per-failure unchanged sentinels | Real operation result/cleanup; injected backend/unlink failure |
| Affected consumers | Changed offline and integration selected and reported separately | No full suite or native runtime proof |

Record source hashes, verbose passing node IDs/JUnit, before/action/after facts
and negative-control logs under ignored current-run evidence. All C1-C3 are
implementation-stage proof. Run broad affected lanes after final implementation
Result/Log edits so their first retained receipt is useful; during debugging use
exact nodes. No full project coverage floor belongs to this card.

## Migration Plan

One native change/checkpoint. After implementation and its current proof, the
separate finalizer performs semantic sync, refreshes current typed C1-C3 proof
AFTER sync/Result/Log changes, then successfully handoffs. Archive similarly
refreshes proof for the changed fingerprint. Missing/stale proof is authorized
work to finish, not a reason to exit with a report. Use verbose pytest and each
condition's declared selector; choose relevant nodes, not arbitrary passing tests.
Recovery records its own no-op native-sync mapping if canonical is already merged.
Do not add these later aggregate stages as implementation prerequisite checkboxes.
Revert the scoped policy correction if needed; no persisted data migration.

## Open Questions

No operator decision remains. Implement the smallest correction satisfying the
complete policy partition; preserve later FIX-06/FIX-08 scopes and all history.
