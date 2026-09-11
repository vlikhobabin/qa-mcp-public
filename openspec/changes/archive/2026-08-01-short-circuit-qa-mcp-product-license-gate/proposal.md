## Why

qa-mcp is now a free product both standalone and inside `ai for 1c`, but its
startup path still contains an opt-in broker gate that can be activated by
legacy environment variables. A free distribution must not retain an
environment-triggered path that can call `ai1c-license` or deny startup.

## What Changes

- Remove the product-license gate from the MCP startup path and remove its
  broker implementation from the shipped Python package.
- Stop parsing `QA_MCP_LICENSE_GATE`, `QA_MCP_LICENSE_BROKER`, and
  `QA_MCP_LICENSE_TIMEOUT` as runtime settings; legacy values become inert.
- Replace fail-closed license-gate tests with regression coverage proving that
  startup proceeds and no broker process is launched even when all legacy
  license variables are set.
- Keep the separate 1C platform installation/license requirement unchanged.

## Capabilities

### New Capabilities

- `qa-mcp-free-startup`: qa-mcp startup is unconditional with respect to
  qa-mcp product licensing and cannot invoke a product-license broker.

### Modified Capabilities

- none

## Impact

- **Python manager code:** `src/qa_mcp/mcp_server.py`, `src/qa_mcp/config.py`,
  and removal of `src/qa_mcp/license_gate.py`.
- **Tests:** startup/config regression tests replace the retired broker
  decision matrix.
- **Runtime dependencies:** no live 1C runtime, Vanessa MCP, EDT/meta snapshot,
  license server, or broker is required; verification is offline.
- **Unchanged boundary:** legal use of the 1C platform still requires a valid
  platform installation/license under 1C rules.
