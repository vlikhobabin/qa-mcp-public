## 1. Host-Agent TestClient Launch Boundary

- [x] 1.1 Add a constrained authenticated endpoint for detached TestClient
  launch and a bounded status path.
- [x] 1.2 Build launch argv from semantic fields and configured platform
  catalog resolution; reject arbitrary executable paths, shell fragments,
  invalid ports, NUL bytes and empty targets before spawn.
- [x] 1.3 Start the TestClient detached without waiting for GUI exit and return
  PID, TPort, platform metadata and redacted command summary.
- [x] 1.4 Redact password and password-bearing connection-string values from
  every response/log diagnostic.
- [x] 1.5 Bump host-agent version and Python compatibility set for the
  TestClient launch contract.

## 2. Python Remote-Client Lifecycle

- [x] 2.1 Add a host-agent client method for TestClient launch/status with
  structured errors and install/upgrade guidance.
- [x] 2.2 Wire `launch_test_client` in remote-client mode to call the
  host-agent launch path, wait for TPort liveness and remember the attached
  endpoint for later protocol tools.
- [x] 2.3 Support relaunch after a stale remembered endpoint or dead host
  TestClient.
- [x] 2.4 Preserve local Linux/Xvfb launch behavior when remote-client mode is
  disabled.
- [x] 2.5 Return an exact runnable host command as the remote-client fallback
  diagnostic when host-agent launch is unavailable.

## 3. Documentation

- [x] 3.1 Update host-agent documentation with the launch/status contract,
  security boundary, command rendering, redaction behavior and smoke command.
- [x] 3.2 Update remote-client/TestClient lifecycle docs or runbooks so the
  manual scheduled-task path is documented as fallback rather than the primary
  lifecycle path.

## 4. Verification

- [x] 4.1 Run the 1C verification matrix checker in preflight mode and retain
  output under `.artifacts/openspec/remote-client-host-agent-testclient-launch/20260707T193354Z/`.
- [x] 4.2 Add and run focused Python tests for remote launch success, stale
  relaunch, host-agent failure fallback/manual command redaction and unchanged
  local launch.
- [x] 4.3 Add and run Go tests for host-agent TestClient launch validation,
  auth-before-body-parse, detached process start, status, redaction and version
  reporting.
- [x] 4.4 Run `go test ./...` under `host-agent/windows-display-agent`.
- [x] 4.5 Run a Windows host-agent compile check:
  `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-testclient-launch.test.exe .`.
- [x] 4.6 Run a Windows host smoke when an operator-owned Windows desktop is
  available: host-agent launch, TPort liveness from container, read-only
  protocol attach, kill/relaunch. If unavailable, record a retained runtime
  gap at the matrix artifact path.
- [x] 4.7 Run the 1C verification matrix checker in archive-gate mode.
- [x] 4.8 Run `openspec validate remote-client-host-agent-testclient-launch --strict`.
- [x] 4.9 Run `git diff --check`.

## 5. OpenSpec Handoff

- [x] 5.1 Sync `qa-mcp-tool-endpoint-contract` and
  `qa-mcp-windows-host-agent-security` requirement deltas into main specs.
- [x] 5.2 Archive the change after tasks, verification and spec sync are
  complete.
- [x] 5.3 Record protocol corpus/evidence-index updates as N/A because the
  change makes no new native TestClient protocol frame claim.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | Python `launch_test_client` remote-client route and attached endpoint state | Focused offline tests for host-agent launch success, relaunch after stale endpoint, host-agent failure fallback and exact redacted manual command | Pytest output and retained verification summary | `.artifacts/openspec/remote-client-host-agent-testclient-launch/20260707T193354Z/python-launch-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | Windows host-agent detached TestClient launch/status endpoint | Go unit tests with fake platform executable/driver and Windows cross-compile check | Go test output, Windows compile result and retained verification summary | `.artifacts/openspec/remote-client-host-agent-testclient-launch/20260707T193354Z/host-agent-launch-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | Real Windows host TestClient launch, TPort liveness and follow-up protocol attach | Operator-owned Windows smoke: launch through host-agent, verify TPort from container, run a read-only protocol tool, kill client and relaunch | Sanitized MCP transcript or runtime-gap report | `.artifacts/openspec/remote-client-host-agent-testclient-launch/20260707T193354Z/windows-host-launch-smoke.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Business data mutation | Object writes, posting, delete/fill/import/export | No business mutation is part of this lifecycle change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | The change only launches or attaches to TestClient and runs read-only liveness/protocol probes. | Residual risk is limited to process/runtime availability. |
| Native protocol claim | TestClient frame format, dynamic fields or replay templates | No frame or protocol semantic change | none | N/A | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | This change uses existing attach/read behavior after launch and makes no new protocol claim. | None for protocol corpus coverage. |
