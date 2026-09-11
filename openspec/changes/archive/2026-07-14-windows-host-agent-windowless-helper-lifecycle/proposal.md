## Why

The real T4 operators observed a persistent `bsl-agent.exe` console plus
short-lived console windows stealing focus every second on both Windows
workstations. Live diagnostics found two launch defects: Windows process-group
configuration replaced an already-applied `CREATE_NO_WINDOW` flag, and the BSL
supervisor relied on an inherited hidden console that Windows does not
guarantee for a console-subsystem child. On `.201`, an owned stale BSL listener
also caused the visible child to exit and restart on the one-second backoff.

This is not acceptable background behavior for an installed workstation agent.
The T4 rerun remains paused until the delivered binary proves windowless helper
operation on both owned stations.

## What Changes

- Preserve existing Windows process attributes when adding a process group so
  short-lived COM, CLI, platform and maintenance helpers retain
  `CREATE_NO_WINDOW`.
- Start the console-dependent BSL helper with a real but initially hidden
  console instead of `CREATE_NO_WINDOW` or an implicitly visible console.
- During reinstall, stop only a stale `bsl-agent.exe` whose executable path is
  the installer-owned staged path before replacing the binary and restarting
  the host-agent task.
- Retain Windows evidence showing both agents healthy without visible helper
  console windows or a restart loop.

## Capabilities

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: background helper processes do not
  expose consoles or take focus from the interactive operator.
- `qa-mcp-self-hosted-release`: reinstall reconciles only the staged owned BSL
  helper before replacement.

## Impact

- `host-agent/windows-display-agent/{process_group_windows.go,hide_window_windows.go,bsl_supervisor.go}`
- `host-agent/install-windows-host-agent.ps1`
- focused Windows attribute and installer contract tests
- T4 runtime evidence on `192.0.2.201` and `192.0.2.205`
