# host-agent-launched TestClient still dies — bounded env insufficient, needs a fresh interactive session context (F2)

## Status
4.done

## Owner
Codex

## Order Index
128

## OpenSpec Stage
archived; awaiting external review. Direct follow-up to `host-agent-launched-testclient-persistence`
(archived): its delivered fix (bounded child environment) was **proven
insufficient** on the real host. This card is the deeper fix the predecessor
flagged as option (c).

## Source
- 2026-07-08 real .205 / [redacted third-party configuration] E2E. Rebuilt + deployed host-agent
  `0.1.1-testclient-readiness` (sha `c95490eb…`) to .205 (Session 1, started by
  the `qa-mcp-host-agent` scheduled task, backup `qa-mcp-host-agent.exe.0.1.0.bak`
  kept). Drove HEAD `launch_test_client` (after F1 fix) against it.

## Problem
`/testclient/launch` on the real host returns `ok:true, readiness:"ready",
listening:true, pid:N` with the **bounded launch environment applied**
(`launch_context.env_keys` = USERPROFILE/APPDATA/LOCALAPPDATA/TEMP/TMP/HOMEPATH/
PATH/SYSTEMROOT) and the correct command
(`1cv8c … /NАдмин /TESTCLIENT -TPort 15381 …`). But an immediate probe (repeated,
2/2) shows **`NO 1cv8 process alive` and TPort 15381 not listening within
seconds** — the spawned client still dies ~4 s after launch, exactly the
predecessor card's symptom.

So the bounded-environment fix (predecessor Scope option (a)) does **not** solve
persistence. The host-agent runs in Session 1 but is started by Task Scheduler;
the surviving differentiator is the **process token / session context** the child
inherits, not just the environment block. A client launched by an interactive
context (Start-Process / a fresh interactive scheduled task) persists on the same
host; a host-agent-`exec`-spawned one does not.

## Scope
Implement the predecessor's option (c): launch the TestClient child through a
**fresh interactive session context** rather than a direct `exec` from the
long-running Task-Scheduler host-agent process. Investigate, in order:
1. `CreateProcessAsUser` / `CreateProcessAsUserW` with the interactive session
   token (WTSGetActiveConsoleSessionId → WTSQueryUserToken / DuplicateTokenEx),
   spawning into Session 1 with a fresh primary token.
2. Or a transient interactive scheduled task (register → run → the client
   persists → optionally clean the task) as the launch mechanism.
3. Compare the host-agent process token vs. a normal interactive process to
   confirm the exact differentiator.

## Acceptance
- `/testclient/launch` on [redacted third-party configuration] produces a `1cv8` client that **persists
  > 60 s** (process alive, `V8TopLevelFrameSDI` window present, TPort reachable
  from the container) — verified by an immediate probe AND a probe ≥ 60 s later.
- Regression: the existing all-in-one/Linux launch path is unchanged.
- Runtime proof on the real host (record a provider gap only if the host becomes
  unavailable — it was available for this card's discovery).

## Change Set
- `host-agent-testclient-persistence-fresh-session-context` -
  `openspec/changes/archive/2026-07-08-host-agent-testclient-persistence-fresh-session-context/`

## Verify
- `$opsx-ff`: `openspec validate host-agent-testclient-persistence-fresh-session-context --strict`
  passed.
- `$opsx-ff`: `git diff --check -- openspec/changes/host-agent-testclient-persistence-fresh-session-context openspec/board`
  passed.
- `$opsx-do`: focused Go launch-context tests passed.
- `$opsx-do`: `go test ./...` under `host-agent/windows-display-agent` passed.
- `$opsx-do`: `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-fresh-session.test.exe .`
  passed.
- `$opsx-do`: focused Python host-agent version compatibility tests passed.
- `$opsx-do`: `uv run --with pytest --with pyyaml pytest` passed with
  790 tests.
- `$opsx-do`: suite source-of-truth drift gate passed through the agent-core
  fallback script.
- `$opsx-do`: `uv run --with pytest --with pyyaml pytest -m smoke` passed with
  3 selected tests.
- `$opsx-do`: matrix preflight and archive gates passed with one explicit
  qa-mcp provider gap for unavailable Windows .205 persistence proof.
- `$opsx-do`: `openspec validate qa-mcp-windows-host-agent-security --strict`,
  `openspec validate --all` and `git diff --check` passed after spec sync and
  archive.
- Runtime proof on the real Windows .205 host was not run and is not claimed as
  passed.

## Archive
- `openspec/changes/archive/2026-07-08-host-agent-testclient-persistence-fresh-session-context/`

## Related
- `openspec/changes/archive/2026-07-08-host-agent-testclient-persistence-fresh-session-context/`
- `openspec/changes/archive/2026-07-08-host-agent-launched-testclient-persistence/`
- `.artifacts/openspec/host-agent-testclient-persistence-fresh-session-context/20260708T121735Z/windows-host-persistence-provider-gap.md`

## Result
Implemented the host-agent launch-context change: common launch/readiness logic
now uses a platform launcher seam, non-Windows keeps the existing direct exec
path, and Windows builds use `CreateProcessAsUserW` with the active interactive
session token and `winsta0\\default`. Bounded launch-context metadata reports
method, session id and environment keys without exposing token handles or raw
environment values.

Runtime persistence proof remains unrun and unproven because the real Windows
.205 host is unavailable in this environment. The gap is recorded as a qa-mcp
provider gap owned by `/opt/ai-dev-suite-for-1c/qa-mcp`.

## Next
- 2026-07-08 the real Windows .205 persistence proof was RUN (supervised live
  session) and **disproves this card's approach**: with `SeTcbPrivilege` and the
  launch-time panic fixed, `CreateProcessAsUserW` spawns a client in Session 1
  but it still `exited_early`. The persistence goal is carried forward on
  `host-agent-testclient-persistence-interactive-launch-mechanism` (backlog),
  which pursues a persisting interactive-scheduled-task launch (proven > 60 s on
  the same host). The delivered `CreateProcessAsUserW` code stays as-is; this
  card remains done for the code it shipped, not for the persistence acceptance.

## Change 1: `host-agent-testclient-persistence-fresh-session-context`

### Why
The delivered bounded-env fix does not make the host-agent-launched client
persist; the real fix is to spawn the child in a fresh interactive session
context with its own primary token.

### Goal
Make host-agent-launched TestClients persist > 60 s with their window and TPort
by launching them through a fresh interactive session context.

### Acceptance
- As in the card Acceptance.

### Depends On
- none (supersedes the persistence goal of `host-agent-launched-testclient-persistence`).

### Related
- `host-agent-launched-testclient-persistence` (archived; bounded-env fix),
  `host-agent-testclient-launch-persistence-dwell` (F3), epic 111.
- host-agent `testclient_launch.go`, `process_group_windows.go`.

### Notes For `$openspec-ff-change`
- Capability to modify: `qa-mcp-windows-host-agent-security`.
- Windows-session/token behavior is not reproducible in the Linux offline suite:
  keep Go unit tests for the token/session plumbing where feasible and treat the
  persistence proof as runtime evidence on the real host.

## Log
- 2026-07-08 filed from the .205 E2E; bounded-env fix (predecessor) proven
  insufficient — host-agent-launched client dies ~4 s (2/2 probes) despite
  `readiness:ready`. Root cause narrowed to the inherited Task-Scheduler process
  token/session, not the environment block. Needs option (c) fresh interactive
  session context.
- 2026-07-08T12:17:35Z `$opsx-ff` created apply-ready artifacts for
  `host-agent-testclient-persistence-fresh-session-context`, recorded Windows
  .205 persistence proof as a planned qa-mcp provider gap for this Linux
  session, and moved the card to `2.todo`.
- 2026-07-08T12:17:35Z `$opsx-do` started, matrix preflight passed with one
  explicit qa-mcp provider gap for unavailable Windows .205 persistence proof,
  and the card moved to `3.inprogress`.
- 2026-07-08T12:17:35Z Implemented Windows fresh interactive-session
  `CreateProcessAsUserW` launch path, preserved non-Windows direct exec path,
  synced `qa-mcp-windows-host-agent-security`, retained provider-gap evidence
  instead of Windows runtime proof, archived
  `host-agent-testclient-persistence-fresh-session-context`, and stopped at
  `awaiting external review` per supervised-run instruction.
- 2026-07-08T12:44:33Z `$opsx-deliver` resumed after external review,
  validated `.runtime/opsx/reviews/host-agent-testclient-persistence-fresh-session-context.json`
  with `--check-fresh`, recorded `result: go`, review cycle 1, findings
  blocker/major/minor = 0/0/0, updated `host-agent/README.md` for the
  interactive-session launch contract, and proceeded to scoped publish.
- 2026-07-08 (later, supervised live .205) persistence proof RUN and NEGATIVE.
  Test 1 (deployed User/Limited host-agent): `WTSQueryUserToken failed: a
  required privilege is not held` → fail-closed. Test 2 (host-agent as SYSTEM,
  and after fixing the `windowsEnvironmentBlock` NUL panic delivered as
  `host-agent-testclient-launch-envblock-nul-panic`): `CreateProcessAsUserW`
  spawned a Session-1 client (PID 8728) that still `exited_early`. The
  fresh-session-token hypothesis is disproven; an interactive scheduled-task
  launch of the same command persisted > 60 s (325 s observed). Follow-up:
  `host-agent-testclient-persistence-interactive-launch-mechanism` (backlog).
