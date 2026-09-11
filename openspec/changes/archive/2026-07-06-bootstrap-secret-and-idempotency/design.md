## Context

`bootstrap.ps1` builds a TestClient launch command that can include
`/P<password>`, writes it to
`%LOCALAPPDATA%\qa-mcp-setup\launch-testclient.ps1`, registers a one-shot
interactive scheduled task that points at that script, and leaves the script on
disk. The same script uses a port-open probe as the success criterion, so a
stale TestClient from a previous bootstrap can satisfy the check even when the
new infobase failed to launch.

This is a TestClient launch-safety change. It does not change protocol frames,
BSL, metadata, or Linux capture/replay. Because the behavior is Windows
specific, Linux delivery should include offline script/tests and record a
Windows runtime smoke requirement when an operator environment is available.

## Goals / Non-Goals

**Goals:**

- Avoid leaving plaintext infobase passwords in
  `%LOCALAPPDATA%\qa-mcp-setup\launch-testclient.ps1`.
- Restrict any temporary launch helper to the current user while it exists.
- Prevent stale TestClient listeners from producing false bootstrap success.
- Remove or replace stale `qa-mcp-testclient` scheduled task state before each
  launch attempt.
- Prefer the process started by this bootstrap run when deriving the window
  title.

**Non-Goals:**

- Store or manage long-lived 1C credentials.
- Change the host-agent HTTP API.
- Change container runtime wiring beyond using the correct TestClient host/port.
- Terminate unrelated 1C sessions without a clear ownership signal.

## Decisions

**D1 - Keep the scheduled task path, but make the launch helper temporary.**
The interactive scheduled task is still needed for the Windows desktop session.
Create the launch helper with user-only ACLs, run the task, then remove the
helper in cleanup after success or failure. The scheduled task should also be
deleted or overwritten so it cannot re-run a stale helper later.

Alternative considered: put the full launch command directly into the scheduled
task action. That can move the password into scheduled-task metadata, which is
not an improvement.

**D2 - Fail loudly on ambiguous pre-existing listeners.**
Before launching TestClient, probe `ClientPort`. If it already accepts
connections and bootstrap cannot prove ownership of that listener, stop with a
diagnostic that names the port and the expected operator action. This satisfies
idempotency by preventing false success against a stale infobase.

**D3 - Record the launched process when possible.**
Use `Start-Process -PassThru` inside the temporary launch helper and write the
process id to a non-secret pid file. Window-title derivation can then filter
host-agent `window_list` results by that pid instead of choosing the first
`1cv8` process. If no pid/window match is available, bootstrap should warn or
fail according to existing `WindowTitle` fallback policy.

**D4 - Separate Linux offline evidence from Windows runtime evidence.**
Add Linux tests for script structure, cleanup branches and stale-listener
guards. A Windows operator smoke remains the runtime evidence path for proving
actual scheduled-task and TestClient behavior.

## Risks / Trade-offs

- Deleting the helper too early could race the scheduled task -> cleanup should
  happen only after the launch command has started and the port probe has
  completed or failed.
- Failing on existing listeners can interrupt same-port reruns -> the failure is
  intentional unless the implementation can identify and replace an owned
  previous TestClient.
- Windows runtime proof may not be available in this Linux workspace -> record
  the gap explicitly rather than claiming live TestClient evidence.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `delivery/bootstrap.ps1` scheduled task and TestClient launch path | offline script tests plus Windows bootstrap smoke plan for password cleanup and stale-listener rerun | focused pytest/script assertions; Windows scenario log when available; cleanup evidence showing no plaintext launch helper remains | `.artifacts/openspec/bootstrap-secret-and-idempotency/<run-id>/` | required | qa-mcp | N/A for BSL/metadata/form/role/posting/report/live-read surfaces | Linux-only delivery cannot prove Windows scheduled-task behavior without an operator smoke |
