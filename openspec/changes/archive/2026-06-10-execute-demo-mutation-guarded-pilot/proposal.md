## Why

After targets and manifest rows are reviewed, the pilot needs a single guarded
runtime path that can either execute a recoverable real-demo mutation or stop
before action with a precise blocker. This is the step that turns the contract
into retained live evidence without widening the blast radius.

## What Changes

- Pass the live runtime preflight (`scripts\preflight-live-runtime.ps1`,
  capture or attach mode per the selected runtime route) before any 1C process
  is started or attached; a failed preflight is a recorded `runtime_gap`
  blocker before execution, with `preflight_result.json` retained.
- Load only reviewed real-demo mutation manifest rows from
  `define-demo-mutation-manifest-contract`.
- Recheck active form, target marker and pre-state immediately before any
  mutation.
- Execute at most the selected first row set through the Windows-native
  reviewed runtime path when the row is complete and recoverable.
- Use unique `QA_MCP_*` markers or object names for created test data.
- Retain pre-state, action, post-state, recovery and owned-process cleanup
  evidence, or retain a blocked summary when execution is not allowed.
- Keep raw captures, full UI dumps, platform logs and generated replay payloads
  under ignored runtime or artifact paths.

## Capabilities

### New Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: Real demo mutation pilots gain a guarded execution
  step that runs only reviewed recoverable rows and records recovery evidence or
  no-execution blockers.

## Impact

- May use the local Windows 1C runtime, Vanessa/TestManager/TestClient lab and
  ignored runtime capture paths.
- Compact retained evidence belongs under
  `.artifacts/openspec/execute-demo-mutation-guarded-pilot/<run-id>/` or later
  reviewed docs evidence paths.
- Runtime scripts must clean only PIDs they created or explicitly own.
