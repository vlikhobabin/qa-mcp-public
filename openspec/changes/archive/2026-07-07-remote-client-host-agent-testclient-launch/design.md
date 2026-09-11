## Context

The qa-mcp remote-client contour runs the MCP server in Linux while the 1C GUI
client runs on the Windows host. The display host-agent already owns
authenticated desktop primitives and allowlisted host-side process execution,
but it does not own a persistent TestClient process. The bootstrap scripts can
start one manually as a scheduled task, yet `launch_test_client` itself still
returns `local-boot-disabled-remote-client`.

The desired lifecycle boundary is narrower than arbitrary platform execution:
qa-mcp should construct a reviewed TestClient command from semantic fields,
start it detached on the host, report the spawned PID and TPort, and let later
protocol tools attach over TCP. The launch may start a GUI process, but it does
not write 1C business data by itself.

## Goals / Non-Goals

**Goals:**

- Add an authenticated host-agent endpoint for detached TestClient launch and
  bounded status checks.
- Build the host command from semantic fields: platform executable/catalog,
  infobase connection string, user, optional password, TPort and extra safe
  startup flags.
- Return process metadata suitable for `launch_test_client` results:
  PID, port, listening/status information, effective executable/version and
  redacted command summary.
- Make Python remote-client `launch_test_client` call the host-agent path,
  wait for the TPort, remember the attached endpoint and support relaunch after
  the previous host client dies.
- Keep the manual command fallback exact and actionable when host-agent launch
  is unavailable.

**Non-Goals:**

- Do not add arbitrary host shell execution or arbitrary executable path
  support.
- Do not change native TestClient protocol frames or capture/replay data.
- Do not make the Linux container own or terminate unrelated host GUI
  processes.
- Do not run live Windows GUI launch from this Linux-only delivery unless an
  operator-owned Windows desktop is available and approved.
- Do not add business command clicks, object writes, posting, import/export or
  other 1C business-data mutation.

## Decisions

1. **Use semantic host-agent requests, not raw argv.**

   The Python side sends target fields and the host-agent renders the `1cv8`
   command locally. This keeps path resolution, password redaction and
   fail-closed validation on the host side, and avoids exposing a generic
   detached process launcher.

2. **Treat launch as detached and attach over TCP.**

   The host-agent returns after process start instead of waiting on the GUI
   process. Python waits for the configured TPort from the container and then
   records the same endpoint shape as `attach_test_client`, so existing
   endpoint-touching tools reuse it.

3. **Separate ownership from stop semantics.**

   A remote host process is not a Linux child process. `stop_test_client` must
   not attempt local process-group cleanup for it unless a later host-agent stop
   contract is explicitly added. The launch result should be honest about host
   ownership and tell callers whether qa-mcp can only re-launch/attach.

4. **Use exact fallback command as a first-class diagnostic.**

   If the host-agent is missing, unreachable or too old, `launch_test_client`
   should still return a structured result containing the exact host command
   the operator can run. The password value must be redacted in diagnostics
   while `password_set` remains visible.

5. **Runtime proof is planned but host-dependent.**

   Linux offline tests can prove request construction, error handling and
   endpoint remembrance. Real GUI launch proof requires an attached Windows
   desktop with 1C installed; when unavailable in this workspace, record a
   runtime gap and require a retained Windows smoke transcript before claiming
   field proof.

## Risks / Trade-offs

- A detached GUI process may outlive the host-agent request. Mitigation: return
  PID and status metadata and keep stop semantics explicit.
- Host-agent launch can duplicate an already-running TestClient on the same
  TPort. Mitigation: status-check/listening preflight and relaunch behavior
  should prefer an existing listening TPort or fail with a bounded diagnostic
  before spawning a duplicate.
- Passwords can leak through command summaries. Mitigation: never echo the raw
  password; redact `/P` values and connection-string password fragments in all
  returned diagnostics.
- Linux CI cannot prove Windows GUI startup. Mitigation: Go unit tests,
  Windows cross-compile, Python offline tests and retained runtime-gap evidence
  are required; Windows smoke remains a delivery evidence row when available.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | Python `launch_test_client` remote-client route and attached endpoint state | Focused offline tests for host-agent launch success, relaunch after stale endpoint, host-agent failure fallback and exact redacted manual command | Pytest output and retained verification summary | `.artifacts/openspec/remote-client-host-agent-testclient-launch/20260707T193354Z/python-launch-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | Windows host-agent detached TestClient launch/status endpoint | Go unit tests with fake platform executable/driver and Windows cross-compile check | Go test output, Windows compile result and retained verification summary | `.artifacts/openspec/remote-client-host-agent-testclient-launch/20260707T193354Z/host-agent-launch-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | Real Windows host TestClient launch, TPort liveness and follow-up protocol attach | Operator-owned Windows smoke: launch through host-agent, verify TPort from container, run a read-only protocol tool, kill client and relaunch | Sanitized MCP transcript or runtime-gap report | `.artifacts/openspec/remote-client-host-agent-testclient-launch/20260707T193354Z/windows-host-launch-smoke.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Business data mutation | Object writes, posting, delete/fill/import/export | No business mutation is part of this lifecycle change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change only launches or attaches to TestClient and runs read-only liveness/protocol probes. | Residual risk is limited to process/runtime availability. |
| Native protocol claim | TestClient frame format, dynamic fields or replay templates | No frame or protocol semantic change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | This change uses existing attach/read behavior after launch and makes no new protocol claim. | None for protocol corpus coverage. |
