## Context

The source-bound remote launch contract is version-coupled, but validation treats an empty version as the legacy auto-select request. The transient task is primarily removed by PowerShell `finally`; `exec.CommandContext` can terminate that process on cancellation before the cleanup executes.

## Goals / Non-Goals

**Goals:**

- Reject omitted and malformed platform versions before resolution.
- Ensure the exact random transient task name is removed by Go on success, error and request cancellation.
- Keep cleanup bounded, idempotent, secret-safe and independent of the canceled request context.

**Non-Goals:**

- Change the shell-broker launch mechanism, relay protocol or TPort ownership model.
- Run a live TestClient or mutate an infobase during offline delivery.

## Decisions

- Treat the trimmed empty string as `invalid-platform-version`; no remote launch request may use legacy newest-build selection.
- Keep PowerShell `finally` as the fast cleanup and add an exact-name Go cleanup command using a fresh bounded background context.
- Run the Go cleanup after the registration process completes and before interpreting registration/broker errors. A cleanup failure is a launch failure, while an idempotent deferred fallback covers unexpected early returns.
- Use no wildcard or name-wide termination. The cleanup command receives only the generated task name via JSON stdin and emits no launch credentials.
- Verification uses native Go tests, a Windows test cross-build and static exact-name cleanup assertions. No protocol capture/frame evidence changes.

## Risks / Trade-offs

- [Task Scheduler is temporarily unavailable] → Fail the launch with a bounded cleanup diagnostic instead of claiming a residue-free response.
- [Both PowerShell and Go remove the task] → The Go command treats absence as success.
- [Cancellation delays return during cleanup] → The independent cleanup budget is finite and intentionally outlives the caller context.
