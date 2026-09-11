## Why

Live manager fixture traffic is not useful until side-channel command events
can be joined to proxy chunks and normalized into corpus rows. Current
reporting can count dry-run gaps, but it does not derive reviewed frame ranges
or hashes for manager fixture V1 cases.

## What Changes

- Extend corpus runner/analyzer/reporting to consume manager fixture V1
  `case_events.jsonl` and `traffic.jsonl`.
- Join command event boundaries to manager/client chunk or frame ranges.
- Generate compact corpus rows with request/response sizes, dynamic fields,
  normalized hashes, operation token candidates, response markers and
  replay/probe status.
- Keep unresolved joins visible with precise reasons instead of accepting
  incomplete rows.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: require manager fixture V1 event/traffic joins and
  normalized reviewed rows before using live manager harness runs as corpus
  evidence.

## Impact

- Touches Python protocol research tooling under `tools/protocol-research/`.
- Consumes runtime capture output but keeps raw traffic ignored.
- Requires live capture output for full verification; offline fixture samples
  can verify parsers.
- Does not change 1C BSL source.
