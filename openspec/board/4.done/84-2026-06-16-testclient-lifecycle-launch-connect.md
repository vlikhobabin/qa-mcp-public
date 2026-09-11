# 84. TestClient lifecycle — launch / connect / manage clients

## Status
4.done

## Order Index
84

## Owner
unassigned

## OpenSpec Stage
story

## Source
- 2026-06-16: roadmap card 82, stage 2. Today qa-mcp only CONNECTS to a `/TESTCLIENT` that is already
  listening on a host/port; it cannot launch or manage a client. vanessa-mcp's `connect_test_client` launches
  the client from a profile and manages it.

## Summary
Give qa-mcp the client lifecycle vanessa-mcp has: launch a TestClient against a target infobase, connect,
report status/PID, and tear down — so an agent can stand up the test client itself.

## Acceptance
- An MCP tool (e.g. `ensure_test_client` / `connect_test_client`) launches `1cv8 ... /TESTCLIENT -TPort N`
  against a target (file/server infobase, user, kind thin/thick) under a headless display, waits for the
  port, and returns a connected session handle (redacted connection summary, PID).
- Supports the existing lab pattern (Xvfb on Linux) and the apache/OData version-contention handling
  (stop apache for `vanessa_client`) as a documented precondition or automated step.
- A profile/target descriptor (like `.ai1c/vanessa-qa-mcp.env`) parameterizes it; secrets stay local.
- Clean teardown (kill client, restore apache). Reuse the proven `run_*_test.sh` boot logic.

## Change Plan
1. ✅ Lifecycle module — `src/qa_mcp/protocol/lifecycle.py`: `TestClientTarget` (file/server infobase, user,
   thick/thin → 1cv8/1cv8c, port, headless Xvfb wrap, apache management, stale-lock clear), `load_env_file`
   (UTF-8/Cyrillic, quote-stripping), `launch_test_client` (own session/process-group, waits for TPort, child
   OUTLIVES the call), `TestClientProcess` (status/connect/stop + context manager), `stop_test_client`/
   `stop_by_pid` (SIGTERM→SIGKILL the group, reap zombies, restore apache). DONE.
2. ✅ MCP surface — `launch_test_client` / `test_client_status` / `stop_test_client` (server now registers 9
   tools); password is never echoed back (redacted connection summary). DONE.
3. ✅ Tests — `tests/test_lifecycle.py` (11 offline: env parse, from_env override, argv build, conn-string,
   redacted summary hides password, port-listening, group-kill, wait-timeout). Full suite 184 passed. DONE.

## Progress (2026-06-16)
- **DONE.** Live test via `tools/protocol-research/run_lifecycle_test.sh` drives the lifecycle through the MCP
  tools across THREE SEPARATE python processes — A: `launch_test_client(manage_apache=True)` → pid alive +
  listening, apache stopped; B: (new process) `test_client_status` alive+listening **and** a native
  `run_step('read_active_window')` → status=passed with a real active-window context (the launched client
  outlives the launcher and is usable by the rest of the surface); C: `stop_test_client` → stopped=true,
  apache_restored=true, AFTER alive=false/listening=false. Env `TEST_CLIENT_KIND=thin` correctly selected
  1cv8c and a live read succeeded. Lab left clean (no stray clients, OData 200).
- Acceptance met: launch under headless Xvfb + wait-for-port + connected handle (PID + redacted summary);
  apache/OData contention handled (manage_apache); `.ai1c/*.env` profile parameterizes it (secrets local);
  clean teardown (kill group + restore apache); reuses the proven boot logic.

## Change Set
- `src/qa_mcp/protocol/lifecycle.py` (NEW), `src/qa_mcp/protocol/__init__.py` (exports),
  `src/qa_mcp/mcp_server.py` (+3 tools), `tests/test_lifecycle.py` (NEW, 11),
  `tools/protocol-research/run_lifecycle_test.sh` (NEW).

## Related
- card 81 (genuine manager on Linux — has the boot recipe), memories linux-native-testclient-xvfb /
  vanessa-mcp-linux-genuine-manager, `tools/protocol-research/run_fullreplay_test.sh` (boot pattern),
  `src/qa_mcp/protocol/session.py` (TestClientSession).

## Log
- 2026-06-16T00:00:00Z card created.
- 2026-06-16: implemented + live-verified → moved to 4.done. lifecycle.py (launch/connect/status/stop) +
  3 MCP tools (server now 9 tools) + 11 offline tests (full suite 184 passed). Live 3-process MCP test
  (run_lifecycle_test.sh): launch→status+read→stop all green, apache restored, lab clean.
