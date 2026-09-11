## Why

`mcp_server.py` mixes MCP tool registration/result shaping with raw protocol
socket work, frame rebinding and introspection sweeps. Extracting that wire code
under `protocol/` makes the MCP layer smaller while preserving the agent-facing
tool contracts hardened by CR-05.

## What Changes

- Move foregrounding, descriptor/value/table/window reads and splice helpers out
  of `mcp_server.py` into protocol-owned modules such as
  `protocol/introspection.py` and `protocol/foreground.py`.
- Leave tool wrappers responsible for argument plumbing, endpoint decoration,
  docstrings and result shaping.
- Preserve `_values_equivalent`, activation retry behavior,
  `_should_retry_label_locate`, and all existing structured result shapes.
- Verify that `mcp_server.py` no longer opens raw sockets or imports
  `GuidRebinder` directly.
- Keep this as Python manager/MCP tool implementation code only. It does not
  change OpenSpec workflow, runtime lab configuration or 1C metadata.

## Capabilities

### New Capabilities

- none

### Modified Capabilities

- `qa-mcp-protocol-lab`: protocol wire/introspection behavior is provided by
  protocol modules instead of the MCP server module.
- `qa-mcp-tool-endpoint-contract`: endpoint-aware tool wrappers preserve
  structured errors and attached endpoint behavior after protocol extraction.

## Impact

- Affected code: `src/qa_mcp/mcp_server.py` and new/existing modules under
  `src/qa_mcp/protocol/`.
- Affected tests: offline MCP registry/endpoint tests, protocol tests and full
  `uv run pytest -q`.
- Live 1C runtime is optional additional evidence only; the required gate is
  offline behavior preservation.
