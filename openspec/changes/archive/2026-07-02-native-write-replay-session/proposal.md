## Why

`protocol/native_write.py` carries many near-identical replay loops, which makes
transport fixes and verdict handling easy to apply inconsistently. CR-03 and
CR-04 already established fail-closed write verdicts and one frame-aware receive
point, so the replay orchestration can now be centralized without changing tool
behavior.

## What Changes

- Introduce one native write replay engine (`ReplaySession`) plus a small
  operation spec (`ReplayOp`) for setup replay, frame retargeting and verdict
  evaluation.
- Convert native write/list/dialog/window operations to use the shared replay
  engine instead of per-operation socket/setup/observe loops.
- Reuse `protocol.transport.read_protocol_available`; do not add a new idle-gap
  receive loop.
- Preserve CR-03/CR-04 behavior for `WriteRetargetError`,
  `_retarget_failed_result`, `_write_value_matches_readback`,
  `ProtocolSendTimeout`, `send_timeout`, and frame-tail receive semantics.
- Keep this as Python manager/protocol code only. It does not change MCP
  provider setup, OpenSpec workflow, runtime lab configuration or 1C metadata.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: native write replay operations share one replay
  session engine while preserving observable protocol results.

## Impact

- Affected code: `src/qa_mcp/protocol/native_write.py` and helper modules under
  `src/qa_mcp/protocol/`.
- Affected tests: offline protocol/native write tests plus full `uv run pytest
  -q`.
- Live 1C runtime is not required for the refactor gate. If a client is
  available, unchanged live-regression output may be retained as additional
  evidence.
