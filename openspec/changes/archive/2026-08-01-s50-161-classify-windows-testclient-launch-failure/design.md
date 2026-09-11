## Context

The Windows shell broker authenticates over an ephemeral loopback socket, calls
`Start-Process -PassThru`, and acknowledges a PID before the Go launcher opens
a process handle. The S50 evidence contains three materially different results:
Task Scheduler error `2147942405`, an acknowledged PID that was already invalid
when `OpenProcess` ran followed by no TPort owner, and one elevated run that did
produce a live listener owner. The current combined error hides those boundaries.
Focused task probes showed that Task Scheduler itself could run both limited and
highest actions, while the secret-bearing PowerShell action used by the old
broker failed before rendezvous. The delivered task therefore runs the same
source-built host-agent executable in a narrow internal broker mode; credentials
arrive only over the authenticated loopback channel and are decoded as explicit
base64 UTF-8 before its fixed PowerShell `Start-Process` child is invoked.

No protocol frame claim changes in this change. The capture source remains the
existing 8.3.27.2130 manager corpus; PID, TPort, session id and lifecycle id are
dynamic fields and raw command lines, tokens and infobase contents remain outside
tracked evidence.

## Goals / Non-Goals

**Goals:**

- Distinguish failure before broker acknowledgement, unusable PID ownership,
  and acknowledged 1C early exit before TPort readiness.
- Prefer the requested TPort's live owner over a transient acknowledged PID.
- Preserve exact lifecycle cleanup and bounded secret-safe diagnostics.
- Prove both the negative early-exit classification and a positive Windows
  launch on the authorized station.

**Non-Goals:**

- Change the TestManager protocol capture or handshake.
- Add arbitrary executable/argument launch, wildcard task cleanup, or broad 1C
  process termination.
- Treat a raw copied live 1CD directory as the final S50 acceptance path.

## Decisions

### Broker acknowledgement is start provenance, not lifecycle ownership

The launcher opens and session-checks one process handle as its first operation
after receiving the acknowledged PID, before it waits for task completion or
unregisters the exact task. It retains that immutable process-object identity
through those operations while it looks for the requested TPort owner. If the listener appears, its owning PID is
the only lifecycle PID recorded and later terminated; a differing listener
owner gets its own session-checked lifecycle handle.
This preserves the shell-broker ownership model while avoiding the failing
PowerShell scheduled-task action and allowing 1C/launcher indirection.

### Failure class is based on the last proven boundary

A task registration or authenticated rendezvous failure before a valid
`started <pid>` acknowledgement remains `testclient-launch-start-failed`. If a
valid acknowledgement was received, no listener owner appears within the
bounded launch wait, and the acknowledged PID is no longer alive, the response
is `testclient-exited-early` with the acknowledged PID, `alive:false`,
`listening:false`, and `readiness:"exited_early"`. If the PID is alive but
cannot be opened for ownership, the response uses a distinct bounded PID-handoff
failure instead of blaming the infobase.

If the retained acknowledged process remains alive but no requested-TPort owner appears,
the host-agent must not hand that PID to the generic readiness loop. The owner
wait uses the caller's normalized timeout; after it expires, the host-agent
terminates only through the already-retained process handle and never reopens
the numeric PID, then returns `testclient-not-listening` without a lifecycle
handle. This prevents PID recycling or a later unrelated listener from joining
the acknowledgement to a false lifecycle target.

The launcher does not infer the reason inside 1C; the negative Windows probe
provides the platform/file-infobase side of the distinction.

### Evidence is exact and ignored

Live proof uses only `User@192.0.2.200` after hostname verification. Evidence
records the exact task/stage names, acknowledged/listener PIDs, typed result and
proof ports. Tokens, screenshots and raw runtime logs stay in ignored runtime
state. Cleanup inventories exclude the inventory command itself and never use a
wildcard termination target.

## Risks / Trade-offs

- [A shell launcher exits before a later 1C child binds] → Continue the bounded
  TPort-owner wait; classify early exit only after the listener deadline.
- [PID reuse] → Retain the acknowledged Windows process handle across the owner
  wait and require the requested TPort owner plus active-session match before
  lifecycle ownership is accepted.
- [OpenProcess is denied for a live PID] → Report a PID-handoff failure and do
  not claim platform early exit or lifecycle ownership.
- [The target host becomes unavailable] → Retain a concrete network/device
  blocker and do not touch any alternate station.

## Migration Plan

Ship the source-compatible host-agent response refinement, rebuild the exact
Windows artifact, run focused tests/cross-build, then deploy only the temporary
run-owned artifact for the S50 proof. Rollback is the prior host-agent binary;
no persisted schema or customer data changes.

## Open Questions

The final reason for 1C early exit is resolved by the dependent disposable
restore/proof change, not inferred from the broker alone.
