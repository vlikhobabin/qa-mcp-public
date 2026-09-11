# Remote-client mode: host-agent-mediated TestClient launch + lifecycle (make launch_test_client work)

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived. **P1 capability + robustness**. Under epic 111.

## Source
- `docs/qa-mcp-connection-issues-2.md` finding **#3**.
- Session investigation 2026-07-07 (TestClient persistence): see
  [[qa-mcp-standalone-release-proven]].

## Problem
In model-B remote-client mode `launch_test_client` returns
`local-boot-disabled-remote-client` (`mcp_server.py:270`): the container cannot
boot the client because it runs on the Windows host. Today the ONLY thing that
launches a host TestClient is `bootstrap.ps1` (a one-shot `qa-mcp-testclient`
scheduled task); nothing owns its lifecycle:
- the container connects to the host client **transiently per tool call**
  (`session.py:314`, `with TestClientSession(...)`) and holds no keep-alive;
- the host-agent (`main.go`) does NOT monitor/relaunch the client;
- host-agent `/platform/execute` can run `1cv8` but is **run-and-wait**
  (`platform_exec.go` `cmd.Start`+`cmd.Wait`), so it can't hold a persistent GUI
  client.

Consequence: the tool named `launch_test_client` cannot launch; and if the host
client dies (crash, user closes the window), the agent has **no way** to
re-establish it — the tester must manually run `1cv8 … /TESTCLIENT -TPort <p>`.
(Note: a client stays up fine for a tester actively at their desktop — the
post-install deaths in headless SSH-driven runs were a session artifact, not a
product idle/disconnect timeout. So this is capability/robustness, not a P0.)

## Scope
1. **Host-agent detached-launch path** — a way to start a persistent
   `1cv8 ENTERPRISE /IBConnectionString File="…"; /N<user> [/P<pwd>] /TESTCLIENT
   -TPort <p>` on the host, detached (fire-and-forget), returning the spawned PID
   — either a new host-agent endpoint (`/testclient/launch`) or a detached mode
   on `/platform/execute`.
2. **Wire `launch_test_client` (remote-client) to route through it** so the agent
   can (re)establish a host client on demand instead of the current disabled
   stub. Keep the manual path documented as fallback.
3. **Optional lifecycle/watchdog** — host-agent monitors the TestClient TPort and
   can relaunch on request/exit; expose status (alive/PID/port/effective user).
4. **Interim UX** — until (1)/(2) land, return a stronger actionable hint from the
   disabled stub: the exact host command incl. the resolved `-TPort`, user and
   connection string (the report asked for this).

## Change Set

- `remote-client-host-agent-testclient-launch` -
  `openspec/changes/remote-client-host-agent-testclient-launch/`

## Change 1: `remote-client-host-agent-testclient-launch`

### Why

`launch_test_client` is the lifecycle entry point operators expect to use, but
remote-client mode still requires a manual Windows-host TestClient launch.

### Goal

Add host-agent-mediated TestClient launch/status support and wire
remote-client `launch_test_client` through it, while preserving the exact manual
host command as a fallback diagnostic.

### Scope

- Add a constrained host-agent TestClient launch/status endpoint.
- Wire Python remote-client lifecycle to launch, wait for TPort liveness and
  remember the attached endpoint.
- Add relaunch handling for stale/dead host TestClient endpoints.
- Add documentation and offline Python/Go coverage.
- Record Windows GUI smoke as retained evidence when available, otherwise as a
  runtime gap.

### Acceptance

- `launch_test_client` in remote-client mode can start a host TestClient through
  the host-agent and return PID/port metadata.
- Follow-up protocol tools attach to the launched TPort without explicit
  endpoint arguments.
- Calling `launch_test_client` after the host client dies re-establishes the
  endpoint.
- Missing host-agent support returns an exact redacted manual host command.

### Depends On

- none

### Related

- `openspec/changes/archive/2026-07-07-remote-client-host-agent-testclient-launch/`

## Verify

- `uv run --with pytest pytest tests/test_display_backend.py tests/test_mcp_server.py -q` - passed, retained at `.artifacts/openspec/remote-client-host-agent-testclient-launch/20260707T193354Z/python-launch-tests.md`.
- `go test ./...` under `host-agent/windows-display-agent` - passed, retained at `.artifacts/openspec/remote-client-host-agent-testclient-launch/20260707T193354Z/host-agent-launch-tests.md`.
- `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-testclient-launch.test.exe .` - passed, retained at `.artifacts/openspec/remote-client-host-agent-testclient-launch/20260707T193354Z/windows-compile-check.md`.
- 1C verification matrix preflight and archive checks - passed, retained at `.artifacts/openspec/remote-client-host-agent-testclient-launch/20260707T193354Z/`.
- Windows GUI smoke - recorded as runtime gap at `.artifacts/openspec/remote-client-host-agent-testclient-launch/20260707T193354Z/windows-host-launch-smoke.md`.
- `openspec validate remote-client-host-agent-testclient-launch --strict` - passed before archive.
- `openspec validate qa-mcp-tool-endpoint-contract --strict` and `openspec validate qa-mcp-windows-host-agent-security --strict` - passed after spec sync.
- `openspec validate --all` - passed after archive.
- `git diff --check` - passed.
- `uv run --with pytest --with pyyaml pytest` - passed, 763 tests.
- `uv run --with pytest --with pyyaml pytest -m smoke` - passed, 3 tests.
- `python3 /opt/ai-dev-suite-for-1c/agent-core/scripts/check_suite_source_of_truth_drift.py` - passed.

## Archive

- `openspec/changes/archive/2026-07-07-remote-client-host-agent-testclient-launch/`

### Notes For `$openspec-ff-change`

- Modify `qa-mcp-tool-endpoint-contract` and
  `qa-mcp-windows-host-agent-security`.
- Include 1C verification matrix rows for Python launch behavior, host-agent
  detached launch/status and Windows host smoke/runtime-gap evidence.

## Acceptance
- `launch_test_client` in remote-client mode starts a live host TestClient (TPort
  bound) via the host-agent and returns its PID/port; a follow-up protocol tool
  attaches and reads.
- Killing the host client and calling `launch_test_client` again re-establishes
  it with no manual host command.
- The disabled-stub interim hint contains the exact runnable host command.

## Related
- `docs/qa-mcp-connection-issues-2.md` (#3), epic 111.
- `mcp_server.py` (launch_test_client remote-client stub), host-agent
  `platform_exec.go` / `main.go`, `protocol/session.py`, `protocol/lifecycle.py`.
- Cross-ref [[qa-mcp-standalone-release-proven]] (persistence analysis).
- `openspec/changes/archive/2026-07-07-remote-client-host-agent-testclient-launch/`

## Result

Implemented and archived. Remote-client `launch_test_client` now routes
through host-agent TestClient launch when configured, remembers the launched
endpoint, and returns a redacted exact host command as fallback when host-agent
launch is unavailable. Host-agent exposes authenticated `/testclient/launch`
and `/testclient/status`.

## Next

- none

## Log
- 2026-07-07 filed from #3 + the persistence investigation; not a release blocker.
- 2026-07-07T19:30:07Z decomposed into
  `remote-client-host-agent-testclient-launch`; artifacts prepared and moved to
  `2.todo`.
- 2026-07-07T19:35:00Z delivery started; moved to `3.inprogress`.
- 2026-07-07T19:45:09Z implementation verified, specs synced, change archived,
  and card moved to `4.done`.
- 2026-07-07T20:00:00Z publish verification passed, scoped commit prepared.
