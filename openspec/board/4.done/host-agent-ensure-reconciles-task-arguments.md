# host-agent: ensure reconciles scheduled-task arguments

## Status
4.done

## Owner
qa-mcp host-agent installer

## Order Index
129

## OpenSpec Stage
archived; reviewed GO; published locally with --no-push

## Source
- Root coordination card:
  `../openspec/board/1.backlog/s10-solo-profile-030-host-agent-ensure-reconciles-task-arguments.md`
- Finans solo onboarding repair run on 2026-07-27 and 2026-07-28.

## Problem
`install-windows-host-agent.ps1` can update the scheduled task action while a
previously running `qa-mcp-host-agent.exe` process continues to serve the old
project profile. A bridge can therefore stay healthy while pointing BSL
diagnostics at the wrong workspace.

## Acceptance
- Changing BSL project inputs from demo to Finans restarts the host-agent
  automatically.
- `qa-mcp-host-agent.exe` and supervised `bsl-agent.exe` use the desired BSL
  workspace/configuration/task arguments after the ensure run.
- A second identical ensure run is idempotent and does not stop/start the task
  when the installed artifacts and desired arguments already match.
- Restart/reinstall output records a concise secret-safe reason when the task is
  restarted.

## Scope
- `host-agent/install-windows-host-agent.ps1`
- focused installer contract tests
- host-agent documentation for the idempotent ensure/reconcile behavior

## Change Set
- `host-agent-ensure-reconciles-task-arguments` -
  `openspec/changes/archive/2026-07-28-host-agent-ensure-reconciles-task-arguments/`

## Change 1: `host-agent-ensure-reconciles-task-arguments`

### Why
An already running host-agent can retain stale BSL profile arguments after
onboarding updates the scheduled task.

### Goal
Make the installer act as an idempotent ensure script: compare desired task
arguments and staged artifacts with the effective scheduled task/running
process state, then restart only when they drift.

### Scope
- Secret-safe desired argument fingerprint and artifact hash checks.
- Scheduled-task action comparison.
- Running host-agent command-line comparison.
- Owned BSL child cleanup when a restart is required.
- Operator-visible restart reason.

### Acceptance
- Same as the card Acceptance section.

### Depends On
- none

### Related
- `openspec/changes/host-agent-ensure-reconciles-task-arguments/`

## Verify
- RED focused installer contract:
  `uv run pytest -q tests/test_host_agent_installer_contract.py` failed with
  3 expected missing-marker failures before implementation.
- GREEN focused installer contract:
  `uv run pytest -q tests/test_host_agent_installer_contract.py` passed,
  12 tests.
- Go host-agent package:
  `cd host-agent/windows-display-agent && go test ./...` passed,
  `ok qa-mcp-host-agent 14.485s`.
- OpenSpec:
  `openspec validate host-agent-ensure-reconciles-task-arguments --strict`
  passed.
- OpenSpec all:
  `openspec validate --all --strict` passed, 17 items.
- Whitespace:
  `git diff --check` passed.
- PowerShell runtime:
  `powershell -NoProfile -NonInteractive -ExecutionPolicy Bypass -File
  C:\Users\User\AppData\Local\qa-mcp-host-agent-proof-stage\windows-ensure-proof.ps1`
  passed on `HISTORICAL-LAB-HOST`; retained evidence:
  `.runtime/changerail/evidence/host-agent-ensure-reconciles-task-arguments/windows-ensure-proof-evidence.json`.
  The proof used isolated task `qa-mcp-host-agent-changerail-proof`, stage
  `C:\Users\User\AppData\Local\qa-mcp-host-agent-proof-stage`, install dir
  `C:\Users\User\AppData\Local\qa-mcp-host-agent-proof-install`, and recorded
  final cleanup with no task, host-agent process or BSL child remaining.
  Assertions passed for demo-to-Finans restart, desired host/BSL command-line
  arguments, host health, idempotent second run with unchanged host/BSL PIDs,
  and secret-safe output.
- RED evidence:
  retained summary at
  `.runtime/changerail/evidence/host-agent-ensure-reconciles-task-arguments/red-installer-contract-20260728.txt`.

## Archive
- `openspec/changes/archive/2026-07-28-host-agent-ensure-reconciles-task-arguments/`

## Related
- `host-agent/install-windows-host-agent.ps1`
- `host-agent/README.md`
- root coordination card:
  `../openspec/board/1.backlog/s10-solo-profile-030-host-agent-ensure-reconciles-task-arguments.md`

## Result
Implemented idempotent installer reconciliation: the installer now hashes
desired state, compares scheduled-task action, installed artifacts, token-file
content hash and running owned process command line, and restarts only when a
secret-safe drift reason is present. Matching reruns skip task stop/start.

## Next
- none; local publish completed with `--no-push`

## Log
- 2026-07-28T11:27:53Z `$changerail-deliver` on the root coordination card
  created this qa-mcp implementation card because the code owner is the
  component repository.
- 2026-07-28T11:36:33Z implemented the installer reconciliation contract,
  synced the host-agent security spec, and verified focused pytest, Go,
  strict OpenSpec and whitespace gates. Windows Task Scheduler proof is not
  available in this Linux context and is not claimed.
- 2026-07-28T11:36:33Z archived
  `host-agent-ensure-reconciles-task-arguments` to
  `openspec/changes/archive/2026-07-28-host-agent-ensure-reconciles-task-arguments/`;
  card remains in `3.inprogress` for independent review.
- 2026-07-28T11:42:34Z independent review cycle 1 returned `NO-GO`
  because Windows Task Scheduler/WMI proof and retained RED evidence were
  missing.
- 2026-07-28T11:54:48Z added retained Windows proof from `HISTORICAL-LAB-HOST`
  for demo-to-Finans drift, desired task/process arguments, idempotent same
  profile rerun and proof-only cleanup, plus a retained RED transcript summary.
- 2026-07-28T12:00:26Z independent review cycle 2 returned `GO`; validator
  accepted the fresh verdict at
  `.runtime/changerail/reviews/host-agent-ensure-reconciles-task-arguments.json`.
- 2026-07-28T12:02:55Z published the component card locally with `--no-push`.
