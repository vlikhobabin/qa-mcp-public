## Why

The manager fixture V1 contract currently stops at source and dry-run
readiness. A live corpus run needs the manager harness itself to execute a
manifest command sequence and emit case boundaries before proxy traffic can be
joined to protocol frames.

## What Changes

- Finish the `ProtocolFixtureTestManager` manifest-driven run loop.
- Load and validate `manager_harness_manifest.json` from the runtime capture
  directory.
- Connect to the TestClient through the supplied proxy port and execute each
  read-only command in order.
- Emit before/after `case_events.jsonl` records and
  `manager_harness_result.json` with command counts, status and exception
  summaries.
- Keep the run read-only and fail closed for action or mutation command kinds.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require the manager fixture V1 harness to execute
  read-only manifest commands end to end, not only define the manifest
  contract.

## Impact

- Touches external 1C EDT source under the `vanessa_manager` project.
- Touches protocol-lab runtime evidence expectations.
- Requires BSL diagnostics and a later live 1C/TestManager smoke to verify
  runtime behavior.
- Does not add protocol normalization or accepted mappings by itself.
