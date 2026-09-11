## Why

The workstation BSL helper inherited the scheduled-task service CWD and tried
to create `.bsl-agent` below `C:\Windows\System32`, then exited with access
denied before its own log opened. Checkpoint `4476585` fixed the launch CWD on
the live stand, but the fix needs offline regression coverage and the installer
still omits the flags, writable paths, timeout and task durability required by
the proven launch.

This change touches the Go host-agent supervisor, its Windows installer, tests,
host-agent docs and OpenSpec contracts. It requires offline process fixtures;
the retained Windows T4 evidence proves the real native contour. It does not
require a live 1C runtime for the delivery gate.

## What Changes

- Run the helper from the helper-binary directory regardless of parent CWD.
- Make child output capture an explicit configuration with closed file handles.
- Raise the cold-start default to 480 seconds.
- Extend the Windows installer with the complete BSL launch contract and a
  scheduled-task restart-on-failure policy.
- Add fake-helper regressions for CWD, readiness, early stderr and restarts.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-runtime-configuration`: workstation BSL supervision has a
  cold-warmup-safe, diagnosable launch contract.
- `qa-mcp-self-hosted-release`: the delivered Windows installer renders the
  required BSL arguments and durable task settings.

## Impact

- `host-agent/windows-display-agent/bsl_supervisor.go`
- `host-agent/windows-display-agent/main.go`
- `host-agent/windows-display-agent/bsl_supervisor_test.go`
- `host-agent/install-windows-host-agent.ps1`
- `host-agent/README.md`
- focused release/installer contract tests and specs
