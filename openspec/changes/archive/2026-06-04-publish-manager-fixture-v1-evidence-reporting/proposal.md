## Why

Manager V1 runs need compact reviewed evidence so researchers can see which
commands ran, which frame ranges are joinable and which gaps remain. Raw
captures alone are not reviewable and must stay outside committed docs.

## What Changes

- Publish a compact manager V1 evidence summary format for command catalog,
  runtime run id, output files, bootstrap phase and read-only case status.
- Add a frame-join report that links side-channel case events to proxy chunk
  counters or records explicit unresolved join gaps.
- Update the evidence index and protocol research docs with the reviewed
  manager V1 run summary.
- Keep acceptance boundaries explicit: no accepted protocol mapping is claimed
  without frame ranges, dynamic-field normalization and replay/direct
  Python-manager evidence.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require reviewed manager V1 evidence reports before
  command/event captures are used as protocol-corpus inputs.

## Impact

- Touches compact docs under `docs/protocol-research/` and related OpenSpec
  evidence artifacts.
- Consumes runtime outputs from ignored `runtime/` capture directories.
- Verification can use offline validation of generated summaries plus live
  run evidence when a fresh manager V1 capture is produced.
- Does not commit raw captures, platform logs or Vanessa EPF binaries.
