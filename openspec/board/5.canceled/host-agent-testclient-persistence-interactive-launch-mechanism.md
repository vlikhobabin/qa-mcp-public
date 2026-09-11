# Host-agent TestClient persistence: CreateProcessAsUser disproven on live host — adopt a persisting interactive launch mechanism

## Status
5.canceled

## Owner
unassigned

## Order Index
132

## OpenSpec Stage
backlog. Carries forward the still-unmet persistence acceptance of
`host-agent-testclient-persistence-fresh-session-context` (F2, archived/done):
F2 shipped the `CreateProcessAsUserW` launch code, but its runtime acceptance
(a launched client that persists > 60 s) was recorded as a provider gap and is
now **disproven** on the live host.

## Source
- 2026-07-08 supervised live .205 / [redacted third-party configuration] session (Proof-B run). Deployed
  the F2 build to .205 and drove `/testclient/launch` three ways.

## Problem
F2's hypothesis was: launching the TestClient from a **fresh interactive session
primary token** (`WTSGetActiveConsoleSessionId` → `WTSQueryUserToken` →
`DuplicateTokenEx` → `CreateProcessAsUserW`, `winsta0\default`) would make the
client persist. Live results disprove it on two axes:

1. **Privilege.** `WTSQueryUserToken` requires `SeTcbPrivilege`. The deployed
   host-agent runs as `User` / Interactive / Limited and does not hold it, so
   F2 fails closed with `testclient-interactive-session-unavailable`.
2. **The mechanism itself is insufficient even with privilege.** Running the
   host-agent as `NT AUTHORITY\SYSTEM` (which holds `SeTcbPrivilege`) and after
   fixing an unrelated launch-time panic
   (`host-agent-testclient-launch-envblock-nul-panic`, delivered), the
   `CreateProcessAsUserW` path **does** spawn a client (PID in Session 1 on
   `winsta0\default`) — but it still returns `testclient-exited-early`; the
   client dies before its TPort binds, exactly the original symptom.

**Contrast (the proven path):** the same
`1cv8 ENTERPRISE ... /TESTCLIENT -TPort 15381` command launched via an
**interactive scheduled task** (User / Interactive) persisted — TPort listening
continuously past 60 s (325 s observed), bound on `0.0.0.0`, window in Session 1.
So the persisting differentiator is NOT the session token F2 duplicates; a
Task-Scheduler interactive logon produces a client that lives, a
service-`CreateProcessAsUser` one does not.

## Scope
1. Replace the host-agent launch mechanism with one that actually persists.
   Prefer F2 scope **option 2**: a transient interactive scheduled task
   (register → run → the client persists → the task can be cleaned) as the
   launch mechanism, OR another logon path that reproduces the interactive
   Task-Scheduler token/session the surviving client has.
2. Diagnose the exact differentiator between an interactive-scheduled-task
   client (persists) and a `CreateProcessAsUserW`-from-service client (exits
   early) — token linkage / logon session / window station association — so the
   new mechanism is chosen on evidence, not trial and error.
3. Keep the F2 launch fail-closed and honest-readiness contracts
   (`testclient-exited-early` / persistence dwell) intact.

## Acceptance
- `/testclient/launch` on [redacted third-party configuration] produces a `1cv8` client that persists
  > 60 s (process alive, TPort reachable from the container, window present),
  verified by an immediate probe AND a probe ≥ 60 s later — the acceptance F2
  never met.
- Works with the host-agent under its normal deployed principal (does not
  require running the whole host-agent as SYSTEM, or explicitly scopes and
  justifies any principal change).
- Regression: the non-Windows / all-in-one launch path is unchanged.
- Runtime proof on the real host (record a provider gap only if the host is
  unavailable).

## Change 1: `host-agent-testclient-persistence-interactive-launch-mechanism`

### Why
The `CreateProcessAsUserW` approach is disproven live; the persistence goal that
motivated F2 is still unmet, and an interactive-scheduled-task launch is proven
to persist on the same host and base.

### Goal
A host-agent TestClient launch mechanism that yields a client persisting > 60 s
under the normal deployed host-agent principal.

### Acceptance
- As in the card Acceptance.

### Depends On
- `host-agent-testclient-launch-envblock-nul-panic` (delivered — removes the
  launch-time panic that otherwise masks any launch outcome).

### Related
- `host-agent-testclient-persistence-fresh-session-context` (F2; disproven),
  `host-agent-launched-testclient-persistence` (bounded-env; insufficient),
  `host-agent-testclient-launch-persistence-dwell` (F3; readiness dwell),
  `read-list-grid-third-party-config-positive-read-runtime-closure` (Proof B — its
  interactive-client fallback is the proven persisting path this card
  generalizes). Capability `qa-mcp-windows-host-agent-security`.

### Notes For `$openspec-ff-change`
- Capability to modify: `qa-mcp-windows-host-agent-security`.
- Windows session/token behavior is not reproducible in the Linux offline suite;
  keep Go unit tests for the launch-mechanism plumbing where feasible and treat
  the persistence proof as runtime evidence on the real host.

## Log
- 2026-07-08 filed from the supervised live .205 Proof-B session. F2's
  `CreateProcessAsUserW` persistence hypothesis disproven live (privilege gap +
  client still exits early with SYSTEM + panic fixed); the interactive
  scheduled-task launch persisted > 60 s (325 s observed) on the same host/base.
- 2026-07-13 canceled as an exact duplicate. Its runtime evidence and
  acceptance are preserved in
  `../2.todo/fix-windows-testclient-launch-and-solo-read-regression.md`, change
  `windows-testclient-interactive-task-launch`.
