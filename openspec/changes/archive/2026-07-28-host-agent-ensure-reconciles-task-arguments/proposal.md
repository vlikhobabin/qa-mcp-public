# Host-agent ensure reconciles task arguments

## Why

Solo onboarding can render a new scheduled-task action for a project profile
while the old `qa-mcp-host-agent.exe` process continues serving the previous
BSL workspace. The installer is already the supported ensure surface, so it
needs to reconcile effective running state, not just rewrite task metadata.

## What Changes

- Make `install-windows-host-agent.ps1` compute a secret-safe desired profile
  fingerprint from the scheduled-task executable, arguments and staged
  artifact hashes.
- Compare the desired task action with the existing scheduled task and the
  running owned `qa-mcp-host-agent.exe` command line before deciding whether to
  restart.
- Restart the scheduled task, and clean up only the owned staged BSL child, when
  task action, running command line, host-agent artifact or BSL artifact drift is
  detected.
- Keep identical ensure runs idempotent: rewrite local files when needed, but do
  not stop/start the scheduled task when the running state already matches.
- Report concise restart reasons without token values or secret file contents.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: the supported Windows installer must
  reconcile effective host-agent process arguments with the desired scheduled
  task and restart only on secret-safe drift.

## Impact

- `host-agent/install-windows-host-agent.ps1`
- `tests/test_host_agent_installer_contract.py`
- `host-agent/README.md`
- Offline verification covers installer contract shape and Go host-agent
  regressions. Live Windows/Task Scheduler proof is not available in this Linux
  delivery context and is retained as a follow-up runtime contour when needed.
