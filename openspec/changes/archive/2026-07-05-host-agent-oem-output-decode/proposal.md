## Why

`/platform/execute` returns platform command stdout/stderr through JSON, but
Windows 1C command-line tools can emit Russian text in the OEM console code
page. Treating those bytes as UTF-8 makes diagnostics unreadable and replaces
Cyrillic output with `U+FFFD` noise.

## What Changes

- Decode platform command stdout/stderr from bytes before JSON serialization.
- Preserve valid UTF-8 and ASCII output unchanged.
- Fall back to the Russian OEM code page (`CP866`) for invalid UTF-8 command
  output, while keeping existing bounding and secret redaction.
- Add Go unit tests for CP866 Cyrillic output, ASCII/UTF-8 preservation, and
  redaction after decode.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `qa-mcp-windows-host-agent-security`: extends `/platform/execute` result
  handling so bounded stdout/stderr remain readable for host-side 1C platform
  diagnostics.

## Impact

- Touches host-agent Go platform execution code, tests, and Go module
  dependencies if a structured code-page decoder is needed.
- Does not change executable allowlists, mutation policy fields, operator
  intent, timeout behavior, authentication, native TestClient protocol claims,
  live 1C data, Vanessa MCP, EDT/meta snapshots, or runtime lab configuration.
