## Why

Manual Windows JSON-RPC diagnostics can corrupt Cyrillic navigation links when
PowerShell sends request bodies through its default string encoding. The
resulting `??????????.??????` link is forwarded toward 1C and looks like an
invalid navigation link instead of an encoding failure.

## What Changes

- Add a qa-mcp echo diagnostic for JSON-RPC tool arguments so callers can see
  the exact `open_link` and other Cyrillic values received by the MCP server.
- Add a clear request-body charset gate for qa-mcp's direct HTTP MCP transport:
  non-UTF-8 or non-UTF-8-declared JSON bodies are rejected before tool dispatch.
- Flag likely mojibake/replacement-character values at the tool boundary with
  structured diagnostics instead of letting them masquerade as bad 1C links.
- Update Windows/PowerShell JSON-RPC runbook examples to send UTF-8 bytes and
  declare `Content-Type: application/json; charset=utf-8`.

## Capabilities

### New Capabilities
- none

### Modified Capabilities
- `qa-mcp-tool-endpoint-contract`: MCP endpoint diagnostics must echo received
  Cyrillic arguments and fail closed on non-UTF-8 direct HTTP JSON bodies.
- `qa-mcp-self-hosted-release`: active Windows delivery/runbook JSON-RPC
  examples must use UTF-8 bytes and an explicit UTF-8 JSON content type.

## Impact

- Touches Python manager/MCP runtime code under `src/qa_mcp/`.
- Touches offline tests for MCP wrapper and direct HTTP transport behavior.
- Touches delivery/operator docs and runbooks.
- Does not change protocol frame synthesis, capture/replay assets, infobases,
  EDT/meta snapshots, or runtime lab configuration.
- Does not require live 1C runtime for the primary acceptance proof; a Windows
  `read_list_grid(open_link="e1cib/list/Справочник.Валюты")` smoke remains the
  preferred end-to-end confirmation when a Windows model-B host is available.
