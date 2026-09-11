## Context

The real registered bound factory on 2405247 returns success/value={} for a
DisplayBackendError from list_windows. Ordinary RuntimeError already becomes
failure; successful empty/nonempty calls keep counts 0/1. This exact offline
baseline is retained under .runtime/qa-roadmap/oss-00/fix-06-planning/reproduction.json.
_get_window_list_impl intentionally exposes a legacy error dict. The default
handler registry currently feeds that dict to HandlerQAExecutor as ordinary data.

## Goals / Non-Goals

Preserve truthful operation verdicts for the complete window-list failure/success
partition, generic-data semantics, positive privacy reconstruction and direct
legacy compatibility. No new error taxonomy, protocol/frame claim, display
transport, live capture, permission/ownership state, artifact trust redesign or
active-window DTO change. FIX-07/FIX-08 retain their independent scope.

## Decisions

1. Add a narrow trusted window-list handler/adapter in mcp_server.py and register
   it for get_window_list in both existing default executor types. It may translate
   the documented legacy primitive error shape into OperationResult using existing
   failure vocabulary. Keep the direct legacy helper/call contract. Do not guess
   verdicts in HandlerQAExecutor from arbitrary error/ok/status dictionary keys.
   Ordinary exceptions must remain failures through the real operation path.
2. Exercise create_mcp_server, actual registered get_window_list and default local
   and Windows-host executors. Fake only external display calls/configuration
   boundaries; use real bound resolution/current target-session-attachment fixtures.
   Verify the expected executor type and backend call count/arguments so a remote
   unavailable guard or replacement executor cannot masquerade as the tested route.
3. Put C1-C3 acceptance nodes in tests/test_display_failure_verdicts.py, with every
   declared typed selector pointing there. C1 covers typed DisplayBackendError and
   ordinary RuntimeError through composed calls; check the injected exception type
   and intended code/detail so fixture-construction TypeError cannot pass silently.
   Include unbound composed operation failure; intentional direct-call legacy
   behavior is separately asserted under C3.
4. C2 proves successful empty and nonempty inventories with exact public counts
   and one actual backend invocation, and generic successful values containing
   ok=false/error/verdict-like keys staying SUCCESS and unchanged in a real
   HandlerQAExecutor dispatch. This generic check deliberately has no window-list
   producer identity. Preserve explicit typed OperationResult pass-through.
5. C3 serializes actual bound local/Windows-host results and checks fixed public
   error code/message, no backend prose, code/payload/cause/install-command secret
   fragments, captions or paths. Keep bound sanitized positive counts useful and
   direct legacy typed error dict plus successful inventory shape/count compatible.
   Positive-schema failure normalization may legitimately emit executor-failure;
   do not weaken the schema or introduce backend prose to retain a low-level code.
6. Retain a scoped ignored sensitivity control that restores the old window-list
   handler registry entry in a test-only patch and causes the real factory C1
   assertion to fail. Generic-data assertions reject global dictionary heuristics.
   Never mutate product files for sensitivity or touch live resources.

## Risks / Trade-offs

- Input safety/privacy: backend error strings can contain secrets. Bound outputs
  must retain existing fixed reconstruction, proven against hostile typed and
  ordinary errors (C1/C3).
- Compatibility: a global dict heuristic changes unrelated successful payloads.
  Translate only the trusted window-list producer and test arbitrary data plus
  direct legacy behavior (C2/C3).
- Mutation/external effects: none introduced; inventory is read-only with all
  external calls replaced. No screenshots, file deletion, processes or live I/O.
- Concurrency/restart: no state or context lifecycle changes; existing per-app
  settings and current-session admission remain intact, with both adapters tested.
- Publication: no release workflow or distribution change; ordinary delivery is
  runner-owned. Protocol frame ranges/replay sources are not applicable.

## Verification Matrix

| ID | Proof | External boundary |
| --- | --- | --- |
| C1 | Real registered factories reject typed/ordinary backend failures, never success={} | Synthetic backend, real default executor/admission |
| C2 | Empty/nonempty exact counts; generic dicts retain SUCCESS/data, typed result passes through | Real dispatch and temporary fixtures |
| C3 | Fixed bound errors and absent hostile fragments; deliberate direct legacy error/success shapes | Fake display, real serializer and direct wrapper |

Run verbose selected nodes with logs/JUnit; preserve source hashes and meaningful
before/action/after assertions. Run affected offline/integration separately after
final Result/Log. No full-suite coverage floor or native-runtime claims.

## Migration Plan

One native change and one implementation checkpoint. Product and test correction
needs no persistent migration; revert its scoped adapter if required. Finalizer
performs semantic sync, records its current native-sync mapping, updates Result/Log
and refreshes C1-C3 typed proof before successful handoff. Archive refresh uses the
same flow and same reviewer continuation. Command receipts alone are not condition
proof: retain actual terminal nodes and source-bound assertions. Evidence commands
serialize. Missing/stale proof is authorized remaining work, not a reason to stop.
Keep sync/archive/handoff/publication out of checkpoint prerequisite checkboxes.

## Open Questions

None requiring an operator decision. Choose the smallest trusted adapter that
preserves the complete declared partition and existing public error vocabulary.
