## Why

The delivered Windows host-agent called `WTSQueryUserToken`, which requires a
privilege absent from its normal Limited/Interactive scheduled-task principal.
The T4 station probes also disproved two fallback assumptions: SYSTEM
`CreateProcessAsUserW` exited before TPort, and a child launched by a transient
InteractiveToken task was terminated with the scheduler job when that task was
released. The long-running installed host-agent itself already has the required
Limited, InteractiveToken, active-console context.

## What Changes

- Replace the Windows-only TestClient process launcher with a transient
  InteractiveToken task shell broker after verifying the host-agent session is
  the active console session. The fixed hidden broker receives the exact
  executable/argument line only through an authenticated ephemeral loopback
  exchange and asks the interactive Windows shell to start 1cv8 through
  `Shell.Application.ShellExecute`.
- Fail closed unless the host-agent process session matches the active console
  session; keep the explicit `winsta0\default` desktop and Limited principal.
- Keep passwords out of helper argv, task metadata, disk artifacts and
  diagnostics by putting only a random nonce/loopback port in the transient
  task action, removing the task before response, and retaining bounded
  redaction.
- Discover the actual 1cv8 PID as the requested TPort listener owner, then
  obtain and monitor its process handle.
- Pin the semantic launch request to the exact QA platform version instead of
  selecting a newer installed build with incompatible protocol captures.
- Preserve existing readiness dwell/fail-loud behavior and the non-Windows
  direct-exec implementation.

## Capabilities

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: define the privilege-free interactive
  launch and secret-safe transient artifact boundary.
- `qa-mcp-tool-endpoint-contract`: expose bounded launch mechanism/cleanup
  metadata while retaining readiness semantics.

## Impact

- `host-agent/windows-display-agent/testclient_process_windows.go`
- Windows launch helper/resolver/unit tests and host-agent documentation
- runtime T4 proof on the owned `.201` station
