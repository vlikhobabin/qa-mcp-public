## Context

Published predecessor decision
`4285a3d154c784f28625ade51b59297bf6ad2679` authorized one pre/post exact
child/listener fence around each existing S4 inventory sample. The sole later
confirmation retained only:

- stage `first_window_inventory`;
- failure `first_window_inventory_failed`;
- candidate and row/task/log hashes;
- exact endpoint/principal/session booleans;
- zero action, no raw UI, restoration and cleanup facts.

The retained pair is intentionally coarse. Offline source analysis shows two
successive information-loss boundaries:

1. `observeHiddenDirectInWorker` maps pre-fence child/listener refusal,
   `inventory_error`, and post-fence `lifecycle_changed` to the same
   `first_window_inventory_failed` value.
2. `inventoryHiddenWindowIsolation` maps hidden-desktop open/enumeration
   failure, operator-desktop open/enumeration failure, and isolation
   validation failure to one Go `error`; `hiddenWindowInventoryOnDesktop`
   likewise does not retain which of open, callback overflow, or enumeration
   failed.

The liveness fence therefore proves only that the candidate contains exact
response-bound child/listener/job/TPort predicates around the call. The
retained diagnostic does not prove that those predicates passed, that the
hidden-desktop enumeration call ran, or that `EnumDesktopWindows` was the
failing operation.

The controller owns the `CreateDesktopW` handle until lifecycle cleanup, while
the worker reopens a desktop by its environment-provided name for inventory.
The response contains a desktop-name hash, not a duplicated desktop handle or
an observation of the worker thread's desktop/window-station binding. The
process/port fence neither establishes nor invalidates that separate desktop
object/call usability boundary. Source analysis cannot choose one Windows
root cause from the coarse retained value.

There are no TestClient protocol capture sources, frame ranges, dynamic
protocol fields or replay strategy in this decision. Evidence inputs are the
three privacy-safe JSON files under the consumed `live-confirmation-20260901t1711z`
directory and tracked source. Dynamic values used here are limited to typed
states, hashes, bounded counts and booleans. No runtime resource is created,
so no runtime cleanup is required.

## Goals / Non-Goals

**Goals:**

- Explain why the published liveness fence and the repeated umbrella failure
  are not contradictory.
- Identify the exact information that is missing before another behavioral
  correction can be evidence-bounded.
- Authorize exactly one later behavior-neutral classification successor at
  the existing private S4 inventory/diagnostic seam.
- Define one hostile offline verification oracle and a fail-closed authority
  ceiling for that successor.

**Non-Goals:**

- Claim that child exit, listener exit, `OpenDesktopW`,
  `EnumDesktopWindows`, callback overflow, operator inventory or isolation
  validation caused the retained refusal.
- Implement the successor, alter the liveness fence, retry inventory, pass a
  desktop handle, change process/thread desktop binding, or redesign the
  lifecycle in this card.
- Run or connect to 1C, contact Windows, access real configuration, consume a
  new confirmation, substitute a target, or start S7.
- Add public API/wire authority or retain raw error text, desktop names,
  handles, PIDs, ports, UI values or screenshots.

## Decisions

### 1. Classify the retained refusal as `inventory_boundary_unresolved`

The durable finding is not `EnumDesktopWindows failed`. It is that the
allowlisted outer stage/failure pair identifies a refusal somewhere inside
the first fenced composite inventory boundary. Exact child/listener liveness,
hidden-desktop call execution, hidden versus operator inventory, and isolation
validation remain unknown for that row.

This classification explains the repeated value after the fence: the new
fence added predicates but the old diagnostic projection still collapses all
of their terminal results into the predecessor's single value.

### 2. Authorize one behavior-neutral cause-classification successor

One later, separate card may add a closed internal cause vocabulary at the
existing S4 fenced inventory/diagnostic seam. It may classify only:

- pre-fence child `exited` or `unknown`;
- pre-fence listener `exited` or `unknown`;
- hidden desktop `open`, `enumeration`, or `overflow` failure;
- operator desktop `open`, `enumeration`, or `overflow` failure;
- isolation validation failure;
- post-fence lifecycle change; and
- successful empty, non-empty/main-absent, or exact-main outcomes already
  represented by current state.

The successor may carry the one allowlisted cause code into the existing
private pre-receipt diagnostic. It MUST preserve current control flow and call
counts byte-for-behavior: no added Windows call, retry, fallback, sentinel,
desktop-handle transfer, job assignment, sleep, UIA admission, public caller
or live action. Generic/raw `error` values are never serialized.

This is the sole successor authorization. It is chosen over a lifecycle
redesign because a behavior-neutral classification seam is smaller, directly
testable with injected offline errors, and can determine whether redesign is
actually justified. It is chosen over another behavioral correction because
the retained evidence cannot identify a behavior to correct.

### 3. Bind the authorization to one hostile oracle

The successor's single verification target is an offline hostile matrix that
injects every allowlisted terminal source and proves all of the following:

1. exactly one cause code is retained for the matching first/second boundary;
2. unknown, unclassified, conflicting or malformed cause state refuses and
   never reaches passive UIA;
3. hidden and operator open/enumeration/overflow plus isolation-validation
   failures remain distinct;
4. no raw error text, endpoint, desktop name, handle, PID, port, UI value or
   other dynamic identifier is serialized;
5. hidden/operator inventory call counts, pre/post fence checks and UIA
   admission behavior are unchanged; and
6. no retry, fallback, process/job/desktop mutation or public route exists.

The oracle is test-firstable without 1C or Windows runtime by injecting the
existing function boundaries. A separately authorized implementation must
record a RED result showing the old umbrella projection cannot retain the
expected cause, then GREEN for the same hostile matrix.

### 4. Keep future runtime and redesign authority closed

This decision does not authorize the successor implementation, a new live
confirmation, or any real-target access. After this card is published, a
separate successor card may implement only the classification seam and its
offline tests. Any later live observation requires new explicit authority and
all source-card gates.

If the hostile oracle cannot preserve behavior/call counts, the successor
stops and architectural redesign is required. If a later separately
authorized observation still yields an unknown/unclassified result, or
identifies that desktop handle/thread/window-station ownership must change,
the next step is architectural redesign rather than another patch.

## Risks / Trade-offs

- [The diagnostic taxonomy is mistaken for a root-cause claim] -> State that
  codes identify exact source branches only; no Windows causal claim exists
  without later retained evidence.
- [Instrumentation changes timing or behavior] -> Require unchanged call
  counts/control flow and injected offline hostile tests; any deviation forces
  redesign.
- [Internal causes leak machine or UI data] -> Serialize only a closed enum
  and reject raw error strings and dynamic identifiers.
- [The successor becomes another rescue staircase] -> Authorize only this one
  classification seam; no behavioral fix or live retry follows implicitly.
- [Dirty blocked/foreign payload enters publication] -> Own only the new card,
  archived change, new synced capability and curated findings; reconcile the
  manifest and protected path hashes before review.

## Migration Plan

1. Publish this decision without changing runtime source or tests.
2. A separately accepted card may implement the exact classification seam and
   hostile RED/GREEN matrix.
3. That implementation is reviewed and published offline before any request
   for new live authority.
4. Failure to keep the successor behavior-neutral, or evidence that ownership
   rather than projection must change, routes to architectural redesign.

Rollback of this documentation removes no runtime state. A future successor
rolls back by removing only the cause projection and restoring the current
umbrella diagnostic; rollback never authorizes a retry.

## Open Questions

- None for this decision. The exact runtime branch is deliberately unresolved
  until the separately implemented classifier is both hostile-tested and, if
  later authorized, observed.
