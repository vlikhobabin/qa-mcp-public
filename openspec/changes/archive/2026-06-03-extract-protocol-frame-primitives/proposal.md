## Why

The reusable frame and template logic needed by the future Python manager
package is still embedded in an exploratory script. Extracting the low-level
primitives first reduces risk before moving live session behavior.

## What Changes

- Move or recreate capture bootstrap loading, frame constants, dynamic field
  replacement and template rendering under `src/qa_mcp/protocol/`.
- Keep exploratory scripts working by importing package primitives or using
  temporary compatibility shims.
- Add fixture-backed offline tests for captured bootstrap loading and template
  rendering behavior.
- Preserve raw capture path policy: package tests use committed compact
  evidence or small curated fixtures, not full runtime captures.
- This change touches Python manager code and tests. It does not require live
  1C runtime, Vanessa MCP or EDT/meta snapshots.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: Add requirements for package-owned frame/template
  primitives and offline dynamic-field verification.

## Impact

- `src/qa_mcp/protocol/`
- `tools/protocol-research/python_manager_client.py`
- tests under `tests/`
- optional documentation under `docs/protocol-research/`
