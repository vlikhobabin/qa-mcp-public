# qa-mcp Hidden Worker Lifecycle Specification

## Purpose

Define the dormant, bounded Windows hidden-worker lifecycle that owns one
authenticated worker, child job and exact TPort listener without admitting a
public route, UI behavior or global input.
## Requirements
### Requirement: Hidden worker rendezvous is bounded and exact
The dormant lifecycle MUST accept only bounded S1 identity, exact absolute
worker/child paths, one valid requested TPort and bounded timeouts, and MUST
admit only one fresh response bound to the exact run, worker token, desktop and
port while retaining no raw token. The worker MUST publish only its worker-local
job handle and MUST NOT open or duplicate a handle into the controller. The
controller MUST authenticate response identity before duplicating from the
exact worker and MUST record a successful local duplicate as lifecycle-owned
before membership checks, cancellation or other admission work.

#### Scenario: Exact response is admitted
- **WHEN** the current-run worker returns matching opaque identity hashes,
  requested port and non-zero exact ownership identities before the deadline
- **THEN** the controller authenticates the response, duplicates the worker-local
  job handle into itself and retains only sanitized hashes, PIDs and exact-owned
  handles

#### Scenario: Response is stale, malformed or foreign
- **WHEN** the response is absent, duplicated, malformed, late, has a wrong
  schema, token, run, desktop or port, or names a foreign worker or child PID
- **THEN** admission fails closed and exact current-run cleanup runs without
  using the supplied handle as a controller-local handle

### Requirement: Child job and TPort ownership precede admission
The hidden worker MUST create one kill-on-close job, MUST create the exact child
suspended on the S1 desktop, MUST assign it before resume, and MUST accept the
requested TPort listener only when both child and listener are members of that
exact job. The worker MUST retain its local job handle until the authenticated
controller duplicate is acknowledged by removal of the current-run response.
Lifecycle-only listener admission MUST reject duplicate or truncated tables
without changing the published shared first-match listener parser.

#### Scenario: Exact child exposes the requested listener
- **WHEN** the assigned child is resumed and an exact job-member PID owns the
  requested TPort
- **THEN** the worker returns child/listener identities and its worker-local job
  handle for controller-initiated duplication and independent reconciliation

#### Scenario: Listener or child ownership is ambiguous
- **WHEN** the requested port is absent, its declared table is truncated, it is
  owned by a foreign PID, resolves to multiple candidates, or either child or
  listener is outside the exact job
- **THEN** the worker reports failure, never emits an admissible handoff and
  terminates only its current-run job

### Requirement: Lifecycle cleanup is complete and exact-owned
The lifecycle MUST make every success, child exit, timeout, controller
cancellation and partial-start failure converge on one idempotent cleanup that
attempts all current-run terminate, bounded wait, handle, desktop, final-response
and temporary-response actions and touches no foreign process, job or desktop.
Only `WAIT_OBJECT_0` is successful cleanup; syscall error, `WAIT_TIMEOUT` and
unexpected wait status MUST be retained as incomplete cleanup without skipping
later actions. Before a ready response exists, cleanup MUST use only
`SYNCHRONIZE` handles for direct descendants of the still-live exact worker and
MUST wait their kill-on-job-close convergence before returning.

#### Scenario: Controller cancels before or after duplication
- **WHEN** cancellation occurs after response publication but before controller
  duplication, or after the local duplicate is recorded but before admission
- **THEN** worker-local or controller-local ownership respectively converges on
  no exact worker, child, listener, job, desktop, response or `.tmp` path before
  the controller returns, while an unrelated process/handle remains usable

#### Scenario: Cleanup operation fails
- **WHEN** assignment, terminate, wait, close or path cleanup reports an error
  or a bounded wait returns timeout or an unexpected status
- **THEN** all remaining exact-owned cleanup actions are still attempted and
  the combined error identifies the original and incomplete cleanup actions

#### Scenario: Worker fails before lifecycle publication
- **WHEN** exact child job assignment fails, response publication fails or the
  worker stops after creating the current-run temporary response
- **THEN** the exact child is terminated and boundedly waited through worker/job
  ownership, both response paths are removed and no provisional controller
  handle exists

### Requirement: S2 remains dormant and input-free
S2 MUST add no existing non-test caller, public API, wire field, tool-profile
admission, window/UIA/prompt action or global-input behavior, and its added
production source MUST remain within `300` physical lines.

#### Scenario: S2 publish scope is inspected
- **WHEN** source callers, manifest paths and exact Windows evidence are audited
- **THEN** only the dormant lifecycle, focused tests and capability artifacts
  are added on top of S1 and no user-visible or public behavior changes
