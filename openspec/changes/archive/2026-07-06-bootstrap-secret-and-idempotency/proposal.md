## Why

The Windows bootstrap writes a plaintext TestClient launch script containing
`/P<password>` into `%LOCALAPPDATA%\qa-mcp-setup` and leaves it behind after
success. Re-running bootstrap can also report success against a stale
TestClient listener from a previous infobase because the success probe only
checks that the TCP port accepts connections.

This change touches qa-mcp Windows bootstrap logic and tests. It affects
TestClient launch behavior but does not change BSL, metadata, protocol frame
semantics, live infobase data, or Linux capture/replay tools.

## What Changes

- Treat the TestClient launch helper as a temporary sensitive file: create it
  with user-only ACLs, run it through the scheduled task, then delete it after
  the launch attempt completes.
- Delete or replace the transient `qa-mcp-testclient` scheduled task after the
  launch path has started the client.
- Detect an existing listener on the requested `ClientPort` before launch and
  stop with an explicit stale-client message unless the implementation can
  prove it owns and replaces that process.
- Derive the window title from the launched process when possible instead of
  falling back to the first arbitrary `1cv8` process.
- Add offline tests for password-file cleanup/idempotency guards and record the
  Windows runtime smoke expected from an operator environment.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-self-hosted-release`: bootstrap does not leave plaintext TestClient
  launch credentials behind and cannot silently reuse a stale TestClient from a
  different infobase.

## Impact

- Bootstrap script: `delivery/bootstrap.ps1`.
- Tests: `tests/test_self_hosted_release_scripts.py` and any focused helper
  tests added for launch/idempotency behavior.
- Documentation: `delivery/README.md`, `delivery/windows-agent-runbook.md`, and
  release delivery docs if operator rerun behavior changes.
