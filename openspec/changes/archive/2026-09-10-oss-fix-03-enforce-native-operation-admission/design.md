## Context

Retained baseline `.runtime/qa-roadmap/oss-00/fix-03-planning/reproduction.json`
shows real FastMCP `click_command` invoking the fake native boundary with session
and attachment absent. Socket creation was forbidden during the invocation;
capture resolution/template and native implementation were substituted. This is
defect evidence, not acceptance. Source inspection shows `execute_operation`
returns straight to executor for schema-missing names. `_admit_bound_route`
already provides most route checks, but catalog membership controls its use.

## Goals / Non-Goals

One invariant: every bound native side effect requires a current admitted route.
Cover both composed tool calls and shared operation entrypoints, including names
outside result schemas. Preserve public tools and valid legacy usage.
No BDD step dispatch redesign (FIX-09A/B/C), wire changes, new observer, mutation
permissions, live operation, broad refactor, or ChangeRail development. Existing
capture/frame/hash/replay contracts are unchanged; new protocol evidence is N/A.

## Decisions

1. Use a shared pure admission policy, separate from result normalization. Reuse
   validated runtime resolution and exact identity checks; do not duplicate a
   per-tool guard. Validate current session sequence against binding generation,
   attachment target/session/generation and exact route arguments. Malformed or
   missing bound state must not downgrade to an unbound execution path.
2. Explicitly inventory native-session, lifecycle, provider-data and pure/readiness
   tools. Classify semantics, not name prefixes or schema membership. Include
   decorated and direct functions and both public profiles. Unknown bound routes
   and unclassified extension calls cannot inherit native permission. Preserve
   documented extension usage for explicit unbound applications. Any explicit
   classification seam must be narrow and validated; do not trust arbitrary
   caller result schemas as authority.
3. Apply admission before context-bound hidden argument evaluation, display
   callbacks, endpoint readiness and native side effects. Keep argument/schema
   hiding intact and route positive calls using admitted attachment identity.
   Lifecycle wrappers retain dedicated launch/status/attach/cleanup policies;
   pure/provider calls do not require a native session solely to inspect data.
4. Keep output normalization for declared schemas intact. A schema-missing known
   native operation may use its existing output contract only after admission;
   unknown bound operations are blocked even if a caller supplies a plausible
   name/kind. Legacy unbound behavior remains explicit.
5. Tests run real factories/registered wrappers and shared entrypoints. Replace
   only external boundaries (sockets, processes, native replay, display backend),
   retaining real policy and state. Assert before/action/after state, zero
   external calls on every negative route and exact endpoint/identity/count on
   positive controls. Include missing/stale/foreign generation and session,
   mismatched arguments, corrupted boundary, different application identity,
   no-schema click_command, and unavailable display callbacks. Classification
   coverage alone is not side-effect proof. Add a sensitivity control showing
   that bypassing the gate makes desired-behavior assertions fail.

## Risks / Trade-offs

- Input safety: caller arguments, stale identities and missing schemas could
  bypass policy. C1/C2 reject before callbacks, with fixed secret-safe outcomes.
- Mutation/external effects: native commands can act before endpoint validation.
  C1 forbids native/probe/display calls and asserts unchanged state; C3 proves
  useful exact admitted execution with fake external boundaries.
- Concurrency: context mixing could authorize another application's route.
  C1/C3 test separate applications and nested/concurrent registered calls while
  preserving current activation semantics; no new scheduler or global owner.
- Restart: no persistence or process lifecycle redesign. Existing lifecycle
  restart/cleanup guards remain and receive compatibility controls (C3).
- Publication: no release workflow change. Installed runner owns independent
  review, archive, final checks and publication after task groups are complete.

## Verification Matrix

| Surface | Required evidence | Boundary / limitation |
| --- | --- | --- |
| Registered negative native calls, C1 | Source-bound JUnit; state snapshots; zero native/probe/display counts | Real factories/policy, fake external effects |
| Full tool inventory and shared entrypoint, C2 | Exact profile/classification sets, unknown-route controls, schema-missing tests | No trusted-observer or protocol claim |
| Admitted read/write/display and independent/legacy controls, C3 | Exact route/identity/count, lifecycle and context isolation assertions | No live 1C or Windows execution |
| Affected subprocess consumers | Separately selected integration JUnit | Actual stdio only where selected |
| BSL, metadata, forms, roles, posting, reports, migration | N/A: no infobase/source objects changed | Native qualification remains FIX-11/FIX-12 |

Retain actual node IDs, timestamps, source hashes and risk observations under
`.runtime/qa-verification/oss-fix-03/`, with current runner-owned typed receipts.
Focused checks follow `--qa-plan` selection and separate offline/integration;
no full suite is implied. Plan each condition at implementation stage so checkpoint
proof is possible without depending on later aggregate finalization.

## Migration Plan

Prepare one stock change, accept, publish planning checkpoint, then clean-start
native runner. Implementation checkpoints prepare evidence; the separate outer
finalization handles semantic sync, handoff, archive and publication. Rollback is
a scoped code revert with the same focused controls; no live resource migration.

## Open Questions

None requiring operator input. Resolve implementation details within this policy
and retain any concrete new finding before expanding scope. The two independent
reviews apply to this new card; prior FIX-02 accounting remains separate history.
