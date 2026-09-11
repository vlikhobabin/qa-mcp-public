## Context

The worker owns the only kill-on-close job handle while starting the suspended
child and exact TPort listener. The old worker-first `DuplicateHandle` created
a controller handle before authenticated handoff, so worker cancellation could
not revoke or identify every owner. Native proof must keep the controller alive
while cancellation occurs at both sides of the transfer boundary.

## Decisions

### Controller initiates the only cross-process duplication

The worker atomically publishes opaque identity, exact PIDs and its local job
handle value. It never opens the controller and never duplicates into it. The
controller authenticates response identity, duplicates from the exact worker
process into itself, immediately records that local handle, then performs
membership and worker-assignment checks. Removing the final response file is
the acknowledgement that lets the worker close its local handle.

### Cleanup waits for both worker and exact listener owner

Before termination the controller opens only a `SYNCHRONIZE` handle to the one
unambiguous PID on the requested current-run port. Cleanup terminates only its
exact job/worker, boundedly waits both owned processes, closes every handle and
removes final and `.tmp` response paths. `WAIT_OBJECT_0` alone is success;
timeout, unexpected status and syscall error are joined with the original
failure while later cleanup still runs.

Before a ready response exists, cleanup snapshots direct children of the still
live exact worker and opens only `SYNCHRONIZE` handles to those current-run
descendants. This lets timeout cleanup wait for kill-on-job-close convergence
without gaining authority to terminate a discovered PID. Listener uniqueness
uses a lifecycle-private complete-table parser; the published shared
first-match/truncated-table parser remains byte-identical to `HEAD`.

### Retain dormant scope and clean composition

The implementation has no production caller and adds no route, protocol,
window, prompt or input behavior. Verification reconstructs published `HEAD`
plus exactly the eight S2 source/test paths through the retained module-aware
`clean-composition.sh`, builds deterministic `-trimpath` Windows candidates and
runs the exact selector on the trusted historical-user interactive task contour.

## Risks / Trade-offs

- [Controller dies before duplication] -> worker retains the sole handle;
  worker death closes it and kills the child.
- [Controller cancels after duplication] -> lifecycle already owns the local
  handle and can terminate/wait exact resources.
- [Job close and child signaling are asynchronous] -> retain a synchronize-only
  handle for the exact requested-port owner and wait it before returning.
- [Publication stops at `.tmp`] -> controller cleanup removes both current-run
  paths and worker job closure kills the child.

## Migration Plan

No runtime migration is needed because the lifecycle remains dormant. Publish
the replacement only after clean-composition tests, exact-source Windows proof,
strict validation, scoped manifest and one fresh ordinary/high review.
