# Hidden-desktop inventory observation boundary decision

## Decision

The retained S4-R1 value
`first_window_inventory/first_window_inventory_failed` is an unresolved
composite-boundary refusal. It is not evidence that the exact liveness fence
passed, that hidden-desktop enumeration ran, or that `EnumDesktopWindows`
failed.

This is why the value can remain unchanged after the published fence: the
fence added exact child/listener/job/TPort predicates, but the existing outer
diagnostic still maps every pre-fence refusal, inventory error and post-fence
lifecycle change to the same predecessor stage/failure pair. A second source
projection then maps hidden inventory, operator inventory and isolation
validation errors to one generic error.

Exactly one later successor is authorized after this decision is published:
a behavior-neutral, closed-vocabulary cause classifier at the existing private
S4 fenced inventory/diagnostic seam, with the hostile offline oracle below.
It may expose which existing source branch refused; it may not change any
runtime behavior. This card does not implement that successor and grants no
live confirmation or behavioral-correction authority.

## Retained evidence

The only runtime input is the already-consumed privacy-safe directory:

`.runtime/changerail/evidence/oss-06-s4-r1-stabilize-hidden-direct-execute-observation-lifecycle/live-confirmation-20260901t1711z/`

Its three JSON records establish:

- exact retained endpoint `historical-user@192.0.2.201`, principal and session gates;
- the admitted candidate hash and one passed S3 row;
- one failed S4-derive row whose pre-receipt diagnostic is exactly stage
  `first_window_inventory`, status `failed`, failure code
  `first_window_inventory_failed`;
- zero action, no raw UI, no real-configuration access from session one;
- exact per-row/final configuration restoration and exact-owned task, stage,
  process and 1C cleanup.

They do not retain the fenced sample status, pre/post liveness snapshots,
hidden versus operator inventory phase, Windows API operation, normalized
error class, isolation-validation result, desktop handle, worker-thread
desktop or window-station identity. Hashes prove row/candidate identity and
integrity; they do not reconstruct omitted fields.

No prior row or timeline may backfill those omitted facts into this consumed
confirmation. No runtime probe was needed or performed for this decision.

## Exact source boundary

The bounded tracked call path is:

1. `observeHiddenDirectInWorker` emits the first-inventory checkpoint and
   calls `observeHiddenDirectWindowsFencedSample`.
2. `newHiddenDirectExactLivenessFence` opens response-bound child and listener
   process handles. Each snapshot checks synchronize state, membership in the
   duplicated exact job and exact listener ownership of the response TPort.
3. `observeHiddenDirectFencedSample` takes the pre-snapshot, invokes one
   `inventoryHiddenWindowIsolation` call, takes the post-snapshot and assigns
   a private fenced status.
4. `inventoryHiddenWindowIsolation` inventories the named hidden desktop,
   inventories the operator desktop, then validates isolation/job ownership.
5. `hiddenWindowInventoryOnDesktop` derives a desktop leaf, opens it with
   `OpenDesktopW`, enumerates it with `EnumDesktopWindows`, bounds callback
   rows and returns either rows or one generic error.

The outer worker retains the same `first_window_inventory_failed` for all of
these fenced statuses:

| Existing terminal source | Current private state | Retained outer pair |
| --- | --- | --- |
| child pre-fence exited/unknown | `child_exited` / `child_unknown` | first inventory failed |
| listener pre-fence exited/unknown | `listener_exited` / `listener_unknown` | first inventory failed |
| any composite inventory error | `inventory_error` | first inventory failed |
| any post-fence difference or refusal | `lifecycle_changed` | first inventory failed |

Within `inventory_error`, source collapses another set:

| Existing source branch | Fact lost before the outer diagnostic |
| --- | --- |
| hidden desktop name/open/enumeration/overflow | exact hidden failure phase |
| operator desktop open/enumeration/overflow | exact operator failure phase |
| isolation validation | whether both inventories succeeded first |

A successful empty inventory remains distinct in the private sample and is not
part of the immediate-error branch. Main absence after successful non-empty
inventory follows the outer bounded polling path. Neither state explains the
consumed failure without a retained private status.

## What the published fence proves

Published commit `4285a3d154c784f28625ade51b59297bf6ad2679` authorized the
exact predicates. The admitted candidate source includes those predicates and
hostile offline coverage. The retained confirmation therefore proves that the
fenced candidate was used, not that a particular predicate evaluated `live` in
the failing row.

The fence observes process synchronization, exact job membership and exact
TPort ownership. It does not observe desktop object identity/lifetime at the
call, the worker thread's current desktop/window station, or which branch of
the composite inventory returned an error. The controller holds the created
desktop handle through lifecycle cleanup, while the worker inventory reopens
the desktop by its environment-provided name. Those facts rule out neither a
desktop-call failure nor another composite branch; they only show why process
liveness cannot substitute for desktop-call usability.

Accordingly, the exact API-level cause remains unknown. Claiming a handle,
thread-binding, access-right or Windows API correction now would exceed the
evidence.

## Sole minimal successor authorization

A later separate card may introduce one private cause-classification unit
covering only existing terminal sources:

- pre-fence child exited/unknown;
- pre-fence listener exited/unknown;
- hidden desktop open/enumeration/overflow failure;
- operator desktop open/enumeration/overflow failure;
- isolation validation failure;
- post-fence lifecycle change; and
- existing successful-empty, successful-non-empty/main-absent and exact-main
  outcomes needed to prove exclusivity.

The unit may retain one allowlisted cause code in the existing private
pre-receipt diagnostic. It must not serialize raw errors, desktop names,
handles, PIDs, ports, endpoints, UI values or any other dynamic identity.

The authorization adds no Windows call, retry, fallback, sentinel, sleep,
desktop-handle transfer, thread/window-station change, job assignment, process
action, passive-UIA path, public caller or wire authority. Existing call counts
and fail-closed decisions must remain unchanged.

## Explicit hostile verification

The successor has one verification target: an injected offline RED/GREEN
matrix at the current function seams.

The RED result must show that the current umbrella projection cannot retain
the expected terminal cause. The same matrix must then pass GREEN and prove:

1. every allowlisted terminal source maps to exactly one expected cause at the
   correct first or second inventory boundary;
2. unknown, malformed, contradictory and unclassified inputs refuse before
   passive UIA;
3. hidden and operator open/enumeration/overflow plus isolation validation
   remain mutually distinct;
4. hostile raw error text and dynamic machine/UI identities never appear in
   the diagnostic;
5. exactly the current hidden/operator inventory calls and pre/post fence
   checks occur, with no retry or fallback; and
6. current admission results and zero-action behavior are unchanged.

The matrix is offline and injection-based. It does not authorize a 1C launch,
Windows session, real configuration access or live confirmation.

## Architectural-redesign stop

If the classifier cannot preserve current control flow/call counts, its
implementation stops and architectural redesign is required. The same stop
applies if later separately authorized evidence remains unclassified or shows
that desktop handle ownership, thread desktop/window-station binding or any
other runtime behavior must change. This decision authorizes no second
classifier, behavioral rescue or retry.

S7 remains blocked.
