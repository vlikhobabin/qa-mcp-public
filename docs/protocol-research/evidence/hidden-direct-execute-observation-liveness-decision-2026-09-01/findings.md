# Hidden direct-execute observation liveness decision

## Decision

The retained S4-R1 refusal is an `inventory_error` with child and listener
liveness unknown at the failing call. It is not evidence of an empty desktop,
an absent main, a marker-derivation failure or one API-level root cause.

Exactly one later S4-R1 correction is authorized: replace each current untyped
inventory sample with one liveness-fenced sample that checks the exact child
and listener before and after one enumeration call, preserves success-empty
and error as distinct fail-closed outcomes, and admits a main only from a
stable successful non-empty inventory. No retry, current-desktop-handle
fallback, sentinel, extra job assignment or second correction is authorized.

This card implements none of that correction and grants no live authority.

## Retained evidence limits

1. The exact same-candidate confirmation retained
   `first_window_inventory/first_window_inventory_failed`, no positive receipt,
   no marker hash, zero action and no raw UI. The row ended before main
   admission or marker derivation, so generic row/task/log hashes cannot move
   the failure downstream.
2. The subsequent bounded disposable probe reproduced
   `EnumDesktopWindows / ERROR_INVALID_DATA` after reading the current hidden
   desktop identity. It falsifies current-desktop-handle reuse as a sufficient
   fix, but it does not establish why enumeration failed.
3. The earlier seven-window timeline and its later `0xC0000005` child exit are
   a different sample. They show that listener-ready/windowed and child-exit
   outcomes both occurred, but cannot backfill exact child or listener
   liveness at the retained first-inventory failure.
4. All cited runtime evidence is privacy-safe and retained under the blocked
   source card. This decision created no new runtime evidence and did not run
   or connect to 1C.

Primary retained inputs:

- `.runtime/changerail/evidence/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle/live-confirmation-20260901t1825z/admission-bundle.json`
- `.runtime/changerail/evidence/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle/live-confirmation-20260901t1825z/blocker.json`
- `.runtime/changerail/evidence/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle/retry-blocker-20260901t155633z.json`
- `.runtime/changerail/evidence/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle/live-timeline-20260901t1520z/admission-bundle.json`

## Offline source findings

- `collectHiddenDirectInvestigation` historically assigned listener readiness
  from `response.ListenerPID != 0`. That is response identity, not a current
  synchronize-handle, job-membership or exact-TPort liveness observation.
- `hiddenWindowInventoryOnDesktop` can return a successful empty slice only
  when `EnumDesktopWindows` itself succeeds. `OpenDesktopW` failure, callback
  overflow and a zero enumeration return are errors; the zero return is
  normalized to `ERROR_INVALID_DATA` when Windows supplies no error code.
- `observeHiddenDirectInWorker` returns immediately when either inventory
  call errors, before main admission. It therefore preserves fail-closed
  behavior but does not retain contemporaneous child/listener state around the
  call.
- Controller transfer authenticates response identity and exact job membership
  before the worker observer runs. That ordering is necessary but not proof
  that the exact child and listener remain live during a later inventory.

These findings support a bounded classification correction, not a claim that
process exit caused the enumeration error.

## Exclusive liveness model

| Layer | State | Meaning and transition |
| --- | --- | --- |
| Child | `live` | Exact synchronize handle is unsignaled and PID remains in the duplicated job; continue |
| Child | `exited` / `unknown` | Signaled/absent or not safely classifiable; refuse before inventory |
| Listener | `live` | Exact synchronize handle is unsignaled, PID is in the exact job and exact TPort still maps to it; continue |
| Listener | `exited` / `unknown` | Signaled/absent/TPort mismatch or not safely classifiable; refuse before inventory |
| Inventory | `error` | Open/enumeration/overflow error; window presence is unknown and cannot be inferred |
| Inventory | `empty` | Enumeration succeeded with zero retained rows; main is absent and the sample refuses |
| Inventory | `nonempty` | Enumeration succeeded with bounded rows; evaluate the existing exact main predicates |
| Window | `absent` | Successful inventory has no unique exact job-owned desktop/class/root-owner main; refuse |
| Window | `present` | Exactly one main matches; recheck child/listener before passive UIA |
| Fence | `changed` | Any post-enumeration child/listener drift, exit, unknown, job loss or TPort mismatch invalidates the whole sample |

An inventory error is never an empty inventory. An empty or non-empty
inventory is never proof of stable liveness without the post-fence. A PID
reported at controller transfer is never current liveness by itself.

## Sole bounded correction

The later correction replaces the existing first and second S4 inventory
sample as one unit:

1. prove exact child and listener liveness;
2. enumerate exactly once;
3. classify error, empty or non-empty without retry;
4. prove the same liveness again; and
5. allow passive UIA only for stable live/live/non-empty/exact-main state.

Its single verification target is a hostile offline state matrix proving that
all other combinations refuse before passive UIA. The change stays inside the
existing S4 observation/lifecycle seam and focused tests. It adds no public
caller or wire field.

If that target fails, or a later separately authorized exact-contour run still
returns `inventory_error`, delivery stops with the typed state. This decision
does not authorize another implementation rescue.

## Safety and resume condition

This investigation was documentation/OpenSpec-only. No 1C process, real
configuration, Windows task, stage, desktop, listener, SSH session or new live
admission was used. Blocked S4-R1 and foreign S7, OSS-07 and OSS-08 paths are
outside its publish manifest.

A later S4-R1 session requires a new explicit operator resume before any real
contour use and remains bound to the exact endpoint, complete offline floor,
session-0 ownership, restoration and exact-owned cleanup gates recorded by the
source card. S7 remains blocked.
