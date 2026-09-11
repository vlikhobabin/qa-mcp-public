## Why

The native write engine currently retargets edit-field leaves with an ASCII-only helper and swallows every
`ValueError`. On Cyrillic field names that can leave the write SET frame addressed at the captured template field,
silently writing the wrong field instead of failing closed.

## What Changes

- Retarget form and table write frames through an element-leaf helper that supports both latin1 and UTF-16LE paths.
- Distinguish expected frames that legitimately lack the base leaf from frames that should have been retargeted.
- Return a structured retarget failure before sending a frame when an expected write/read frame cannot be retargeted.
- Add offline frame tests for Cyrillic UTF-16 field leaves and missing-leaf failures.
- Retain live-regression evidence for a Cyrillic-named field write as part of the card-level write run.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: native write retargeting must address the requested field leaf across ASCII and UTF-16 paths
  and must fail closed on unexpected retarget misses.

## Impact

- Touches protocol write code in `src/qa_mcp/protocol/native_write.py`.
- Adds focused offline tests in `tests/test_native_write.py`.
- Requires live 1C TestClient runtime for final card acceptance via `python -m qa_mcp.regression --include-write`.
- Does not change MCP provider setup, runtime lab configuration, or raw capture storage policy.
