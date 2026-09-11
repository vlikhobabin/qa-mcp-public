# host-agent-launched TestClient does not persist on the .205 host

## Status
4.done

## Owner
Codex

## Order Index
126

## OpenSpec Stage
archived; review go; published. Runtime-acceptance follow-up under epic 111
(item 3 keystone: the remote-launch path must deliver a *usable* client, not
just issue the command).

## Change Set
- `host-agent-launched-testclient-persistence` →
  `openspec/changes/archive/2026-07-08-host-agent-launched-testclient-persistence/`

## Verify
- `$opsx-ff`: `openspec validate host-agent-launched-testclient-persistence --strict`
  passed on 2026-07-08T06:33:11Z-era planning run.
- `$opsx-ff`: `git diff --check -- openspec/changes/host-agent-launched-testclient-persistence openspec/board`
  passed.
- `$opsx-do`: focused Go launch/status tests passed after implementation.
- `$opsx-do`: full `go test ./...` under `host-agent/windows-display-agent`
  passed.
- `$opsx-do`: Windows cross-compile
  `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-persistence.test.exe .`
  passed.
- `$opsx-do`: focused pytest remote-launch/display-backend tests passed.
- `$opsx-do`: matrix preflight and archive checks passed with one explicit
  qa-mcp provider gap for the unavailable Windows .205 runtime proof.
- `$opsx-do`: `openspec validate --all` and `git diff --check` passed after
  spec sync and archive.
- `$opsx-review`: external verdict
  `.runtime/opsx/reviews/host-agent-launched-testclient-persistence.json`
  validated fresh with `result: go`, review cycle 1, 0 blocker/major findings
  and 1 minor runtime-gap finding.
- `$opsx-pub`: `git diff --check` passed.
- `$opsx-pub`: `openspec validate --all` passed with 13 items, 0 failed.
- `$opsx-pub`: `go -C host-agent/windows-display-agent test ./...` passed with
  `ok qa-mcp-host-agent 7.822s`.
- `$opsx-pub`: `GOOS=windows GOARCH=amd64 go -C host-agent/windows-display-agent test -c -o /tmp/qa-mcp-host-agent-persistence.test.exe .`
  passed.
- `$opsx-pub`: `uv run --with pytest --with pyyaml pytest` passed with
  781 tests.
- `$opsx-pub`: suite source-of-truth drift fallback check passed with
  0 findings.
- `$opsx-pub`: `uv run --with pytest --with pyyaml pytest -m smoke` passed with
  3 smoke tests.

## Archive
- `openspec/changes/archive/2026-07-08-host-agent-launched-testclient-persistence/`

## Result
Implemented the offline code and test changes for honest host-agent TestClient
readiness: bounded GUI child environment repair, launch readiness classification,
PID liveness status, Python remote-launch failure propagation, and container-side
TPort gating. The external review gate passed with one minor runtime-gap finding.
The real Windows .205 [redacted third-party configuration] persistence proof was not run in this session
and is recorded as a qa-mcp provider gap, not claimed as proven. Publish docs
updated the host-agent `/testclient/launch` README contract; the synced
OpenSpec specs remain the durable endpoint contract.

## Next
- run the retained Windows .205 host-agent launch smoke when the real host is
  available and replace the provider-gap artifact with a sanitized proof bundle

## Source
- 2026-07-08 .205 [redacted third-party configuration] runtime acceptance (see
  `docs/qa-mcp-connection-issues-2.md` → Resolution). Card D
  (`remote-testclient-launch-via-host-agent`) was proven to construct the correct
  `1cv8 … /NАдмин /TESTCLIENT -TPort … /DisableStartupDialogs` command, but the
  launched client does not survive.

## Problem
The Windows host-agent `/testclient/launch` (and the `launch_test_client` MCP
tool in remote-client mode) reports a `pid` and `listening:true`/`attached:true`,
but the spawned `1cv8` process **exits within ~4 s with no window**, and its TPort
never becomes LAN-reachable. A test agent then cannot drive the client.

Two defects:
1. **The client dies only when spawned by the running host-agent.** A client
   launched by *any other* parent persists on the same host and desktop:
   - `Start-Process`/`System.Diagnostics.Process` from an SSH session persists
     and binds TPort on `0.0.0.0`;
   - a **direct interactive scheduled task** (Task Scheduler → `1cv8`, session 1,
     `LogonType=Interactive`) persists with a visible `V8TopLevelFrameSDI`
     "Бухгалтерия предприятия, редакция 3.0" window and a `0.0.0.0` TPort.
   The host-agent process itself is on the interactive desktop (its
   `/window_list` sees the operator's Telegram/Chrome and the scheduled-task
   client). Ruled out by experiment: stdin/stdout redirection + immediate EOF
   (a `Process` replica persists), the `/P` empty-password argument (persists
   with and without it), and the creation flag (replacing
   `CREATE_NEW_PROCESS_GROUP` with `DETACHED_PROCESS` in the host-agent did **not**
   help). The remaining differentiator is the **host-agent process context
   inherited from Task Scheduler** (environment block / token) under which the
   exec'd GUI child cannot finish initializing and exits before creating its
   window.
2. **The launch result over-reports readiness.** `listening:true`/`attached:true`
   are returned even after the client has already exited, so the tool looks
   successful when it is not.

## Scope
1. Root-cause and fix the launch context so a host-agent-launched `/TESTCLIENT`
   persists and shows its `V8TopLevelFrame*` window. Investigate, in order:
   (a) pass an **explicit, correct user environment** to the child
   (`USERPROFILE`/`APPDATA`/`LOCALAPPDATA`/`TEMP`) instead of inheriting the
   Task Scheduler process env; (b) diff the host-agent process environment vs a
   normal interactive process; (c) if env is not sufficient, launch the client
   through a **fresh interactive context** (a transient scheduled task, or
   `CreateProcessAsUser` with the interactive session token) rather than a direct
   `exec` from the long-running Task Scheduler process.
2. Make the launch readiness honest: verify the process is **alive** AND the TPort
   is reachable before returning `listening`/`attached:true`; otherwise return a
   structured `testclient-exited-early` / not-listening result.

## Acceptance
- `/testclient/launch` on [redacted third-party configuration] produces a `1cv8` client that persists
  (> 60 s), reaches the application (`V8TopLevelFrameSDI` window present,
  login-dialog not stuck), and whose TPort is reachable for protocol reads.
- The launch result's `listening`/`attached` reflect real liveness — no
  false-positive after a fast exit.
- Regression: the existing all-in-one/Linux launch path is unchanged.

## Change 1: `host-agent-launched-testclient-persistence`

### Why
The remote-launch tool must deliver a usable, persistent client; today it issues
the right command but the client dies, blocking every remote read/scenario flow
on this host.

### Goal
Make host-agent-launched TestClients persist with their window and TPort, and
report honest launch readiness.

### Scope
- Windows host-agent launch path (`testclient_launch.go`, process spawn context).
- Launch readiness/liveness reporting.
- Go tests for the readiness classification; a documented manual runtime proof on
  a real host (persistence is a Windows session/context behavior not reproducible
  in the Linux offline suite → record as a runtime provider gap when unavailable).

### Acceptance
- As in the card Acceptance.

### Depends On
- none (follow-up to `remote-testclient-launch-via-host-agent`, archived).

### Related
- `docs/qa-mcp-connection-issues-2.md` (Resolution), epic 111.
- host-agent `testclient_launch.go`, `process_group_windows.go`.
- `openspec/changes/host-agent-launched-testclient-persistence/`

### Notes For `$openspec-ff-change`
- Capability to modify: `qa-mcp-windows-host-agent-security` (launch endpoint
  behavior + honest readiness).
- Treat the real-host persistence proof as runtime evidence; record a provider
  gap with owner `/opt/ai-dev-suite-for-1c/qa-mcp` when a Windows host is
  unavailable.

## Log
- 2026-07-08T06:33:11Z `$opsx-ff` completed proposal, design, delta specs and
  tasks for `host-agent-launched-testclient-persistence`; strict OpenSpec
  validation and scoped diff whitespace checks passed.
- 2026-07-08T06:33:11Z `$opsx-ff` accepted the card, kept the single
  card-owned change `host-agent-launched-testclient-persistence`, moved the card
  to `2.todo`, and started the delivery manifest. Runtime persistence proof on
  the real Windows .205 host is unavailable in this session and will be recorded
  as a qa-mcp provider gap rather than claimed as executed.
- 2026-07-08 `$opsx-do` implemented host-agent/Python readiness honesty and
  retained offline Go/pytest evidence plus
  `.artifacts/openspec/host-agent-launched-testclient-persistence/20260708T063311Z/windows-host-persistence-provider-gap.md`.
- 2026-07-08 `$opsx-do` synced main specs, archived the OpenSpec change as
  `openspec/changes/archive/2026-07-08-host-agent-launched-testclient-persistence/`,
  and stopped before review/publish per supervised-run instructions.
- 2026-07-08T07:09:07Z external `$opsx-review` verdict was already present and
  validated fresh with `result: go`, review cycle 1, 0 blocker/major findings
  and 1 minor runtime-gap finding for the still-unrun real Windows .205 proof.
- 2026-07-08T07:09:07Z `$opsx-pub` documentation pass updated
  `host-agent/README.md` for honest `/testclient/launch` readiness and
  preserved `.runtime/opsx/reviews/host-agent-launched-testclient-persistence.json`
  as ignored runtime state.
- 2026-07-08T07:13:36Z `$opsx-pub` final verification passed: diff whitespace,
  OpenSpec all, host-agent Go, Windows cross-compile, full pytest, suite
  source-of-truth drift fallback and smoke gates.
- 2026-07-08T07:15:15Z `$opsx-pub` created the scoped card-owned publish commit
  and synced the done card before push.
- 2026-07-08 filed from the .205 runtime acceptance; root-cause narrowed
  (ruled out stdio, `/P`, `CREATE_NEW_PROCESS_GROUP`/`DETACHED_PROCESS`) to the
  host-agent's inherited Task Scheduler process context; interactive/`Start-Process`
  launches persist. Workaround for other work: an interactive scheduled task.
