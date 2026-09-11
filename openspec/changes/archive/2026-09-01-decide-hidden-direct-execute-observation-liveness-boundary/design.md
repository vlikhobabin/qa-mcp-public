## Context

The exact same-candidate S4-R1 receipt retained a typed refusal at
`first_window_inventory/first_window_inventory_failed`. A bounded disposable
probe then reproduced `EnumDesktopWindows / ERROR_INVALID_DATA` and proved
that reusing the observer thread's current hidden-desktop handle is not a
sufficient correction. Neither artifact sampled exact child and listener
liveness at the failing call, so they do not establish an API-level cause.

Offline source inspection exposes two ambiguity sources:

- the prior investigation receipt set `ListenerReady` from
  `response.ListenerPID != 0`, which proves only that a PID was reported at
  transfer time, not that the exact listener is currently alive and still owns
  the exact TPort; and
- `hiddenWindowInventoryOnDesktop` returns either a slice or an error, but the
  S4 caller records every error as `window_inventory_failed` without a
  contemporaneous child/listener state. A successful zero-item callback is
  semantically different from `OpenDesktopW`/`EnumDesktopWindows` failure.

This decision uses only the tracked source and retained privacy-safe JSON named
by the card. It makes no protocol-capture claim: there are no TestClient frame
sources, frame ranges, dynamic protocol fields or replay strategy. Dynamic
evidence remains limited to canonical hashes, typed states, bounded counts and
booleans. No 1C, Windows task, real configuration, desktop or listener is
started or accessed by this change.

## Goals / Non-Goals

**Goals:**

- Define mutually exclusive child, listener, inventory and main-window states
  for one passive observation sample.
- Preserve the difference between successful empty inventory and inventory
  API error, and between a reported listener PID and current listener liveness.
- Authorize exactly one bounded correction for a later, separate S4-R1
  session, with one behavioral verification target.
- Keep every unresolved or changing liveness state fail-closed.

**Non-Goals:**

- Diagnose a sole Windows or 1C root cause from the retained failure.
- Modify the blocked S4-R1 implementation/tests, S7, OSS-07 or OSS-08.
- Retry enumeration, reuse a desktop handle as success, add a sentinel or job
  assignment, or weaken main/topology/marker admission.
- Grant a real-contour confirmation, public route, UI action or cleanup
  authority.

## Decisions

### 1. Model one observation as an exclusive ordered state

The later S4-R1 implementation SHALL classify one sample in this order. Once a
terminal classification is selected, no later predicate can relabel it as a
success.

| Boundary | State | Offline-observable predicate | Result |
| --- | --- | --- | --- |
| Child | `child_live` | Exact `ChildPID` synchronize handle is open, zero-time wait is `WAIT_TIMEOUT`, and PID remains in the duplicated exact job | Continue to listener check |
| Child | `child_exited` | Exact handle is signaled or the exact PID is absent | Typed terminal refusal; do not enumerate |
| Child | `child_unknown` | Handle/wait/job query cannot establish either live or exited | Typed terminal refusal; do not enumerate |
| Listener | `listener_live` | Exact `ListenerPID` synchronize handle is open and unsignaled, PID remains in the exact job, and the exact TPort still resolves to that PID | Continue to inventory |
| Listener | `listener_exited` | Exact handle is signaled, PID is absent, or exact TPort no longer resolves to that PID | Typed terminal refusal; do not enumerate |
| Listener | `listener_unknown` | Handle/wait/job/TPort query cannot establish the exact live or exited state | Typed terminal refusal; do not enumerate |
| Inventory | `inventory_error` | `OpenDesktopW` fails, callback overflows, or the single `EnumDesktopWindows` call returns failure | Typed terminal refusal; window state is `unknown`, never `absent` |
| Inventory | `inventory_empty` | The single enumeration call succeeds and completes with zero retained top-level rows | Typed fail-closed `main_absent`; never an API error or success |
| Inventory | `inventory_nonempty` | The single enumeration call succeeds with one or more bounded rows | Evaluate exact main identity |
| Window | `main_absent` | A successful non-empty inventory has no unique job-owned exact desktop/class/root-owner main | Typed refusal; later polling belongs to the existing bounded outer observation loop, not an inventory retry |
| Window | `main_present` | A successful non-empty inventory has exactly one admitted main and all existing job/desktop/class/owner predicates hold | Recheck child/listener liveness, then and only then continue to passive UIA |
| Fence | `lifecycle_changed` | Child or listener differs, exits, becomes unknown, leaves the job or loses exact TPort identity after enumeration | Typed terminal refusal even if a window row was observed |

`main_absent` is meaningful only after a successful inventory. An
`inventory_error` carries `window=unknown`; it cannot be rewritten as empty,
absent or admitted. A non-zero PID or historical listener-ready response alone
never satisfies `child_live` or `listener_live`.

### 2. Authorize exactly one later correction

The sole authorized correction is a **liveness-fenced observation sample** at
the existing first and second S4 inventory boundaries:

1. acquire/check exact child and listener synchronize state, job membership and
   listener-to-TPort identity;
2. perform exactly one existing desktop inventory call;
3. classify success-empty, success-nonempty or error without retry;
4. recheck the same child/listener predicates; and
5. admit a main only from a stable non-empty sample.

This is one correction because it replaces the existing untyped inventory
sample as a unit; it does not create a second observer, caller, public schema,
job assignment, desktop-handle fallback or retry path. Its one verification
target is: hostile offline tests prove every row in the table is exclusive and
that only `child_live + listener_live + inventory_nonempty + main_present +
unchanged post-fence` can reach passive UIA.

The later session may implement only this correction and its focused tests
inside the existing S4 observation/lifecycle seam. If the verification target
cannot be met or a subsequent authorized real-contour run still returns
`inventory_error`, that session stops; this decision does not authorize a
second correction.

### 3. Keep the retained failure classified as unresolved

The retained `first_window_inventory_failed` and disposable
`ERROR_INVALID_DATA` observations establish `inventory_error`. Because they do
not include the new contemporaneous child/listener predicates, their child and
listener states remain `unknown`. The seven-window listener-ready timeline is
a different retained sample; it cannot backfill liveness at the failing
inventory call. Likewise, its later `0xC0000005` child exit does not prove the
earlier inventory error was caused by that exit.

### 4. Preserve authority and payload boundaries

This decision is documentation/specification only. It grants no live
admission. Any later Windows confirmation requires a new explicit operator
resume, the exact source card endpoint and complete offline/session-0
preflight, restoration and cleanup gates. Raw UI, screenshots, paths,
credentials and dynamic error text remain forbidden; later evidence may retain
only allowlisted state names, normalized error class, hashes, counts and
booleans.

## Risks / Trade-offs

- [The fence observes a transition rather than making the APIs atomic] ->
  Classify any post-call liveness drift as `lifecycle_changed`; never accept the
  sampled window.
- [The exact listener can change PID or TPort ownership] -> Require the same
  response-bound PID, job and TPort before and after; a replacement listener is
  not equivalent.
- [Successful empty inventory is mistaken for transient readiness] -> Preserve
  it as `inventory_empty/main_absent`; the inventory call itself is never
  retried into success.
- [The correction improves diagnostics but does not yield a positive main] ->
  Stop after its one verification target or later typed failure; do not infer a
  second rescue authorization.
- [Dirty foreign payload enters publication] -> Use an explicit card-owned
  manifest and compare the exact protected paths with review cycle 1's
  immutable reviewed tree throughout the bounded rescue; stage no broad
  directory. This does not claim a missing delivery-start digest.

## Migration Plan

1. This card publishes only the decision document and capability spec.
2. A later separately resumed S4-R1 session may add the one fenced-sample
   correction and hostile offline tests without changing public callers.
3. That later session must pass its exact offline floor before requesting any
   new live confirmation authority.
4. Rollback of the later correction restores the current untyped sample; it
   does not authorize a retry or alternate correction.

This card invokes no runtime cleanup because it creates no runtime resources.
The later session remains bound to the source card's exact-owned cleanup and
configuration restoration requirements.

## Open Questions

- None. The retained evidence is deliberately insufficient for a sole root
  cause, and the continuation ceiling is exactly one fenced-sample correction.
