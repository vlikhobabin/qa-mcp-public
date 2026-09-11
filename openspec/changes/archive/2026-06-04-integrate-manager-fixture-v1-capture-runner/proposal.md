## Why

The controlled manager harness must run inside the same capture lifecycle as
the TCP proxy and TestClient so command boundaries can be joined to protocol
frames. A standalone manager processor is not enough without runner
integration and shared capture ids.

## What Changes

- Extend the Windows-native protocol capture runner to support a manager V1
  fixture scenario.
- Start or attach the client TestClient through the proxy port and pass that
  proxy endpoint into the manager harness.
- Route manager harness output into the selected capture/runtime directory
  using the same `run_id` as proxy traffic.
- Preserve bootstrap/open-form traffic as a separately labeled phase before
  read-only corpus cases.
- Keep raw TCP data, 1C logs and generated run output under ignored
  `runtime/` paths, with cleanup limited to PIDs created by the runner.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require the capture runner to orchestrate the manager
  V1 harness, proxy traffic and runtime output under one capture id.

## Impact

- Touches `tools/protocol-research/` runner scripts and related tests/docs.
- Uses live 1C TestClient/TestManager runtime for end-to-end verification.
- Must preserve Windows-native execution and owned-PID cleanup rules.
- Does not promote any protocol mapping without later frame/rule evidence.
