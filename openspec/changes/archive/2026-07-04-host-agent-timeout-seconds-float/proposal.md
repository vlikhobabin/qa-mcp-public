## Why

The real agentic-rag-to-host-agent wire path sends `timeout_seconds` as a JSON
number that may be encoded with a decimal point, such as `300.0`. The Go
receiver currently decodes that field into an `int`, so valid cross-process
requests fail with HTTP 400 before an allowlisted CLI can run.

## What Changes

- Accept integer and decimal JSON numbers for `/agent/complete`
  `timeout_seconds`.
- Preserve existing default, minimum and maximum timeout behavior after decode.
- Add a handler-level regression test that posts a JSON float and proves the
  authenticated request is dispatched.

## Capabilities

### New Capabilities

- None.

### Modified Capabilities

- `qa-mcp-windows-host-agent-security`: `/agent/complete` must tolerate JSON
  float timeout values while preserving timeout clamps and fail-closed request
  handling.

## Impact

Touches component-local Windows host-agent Go code and tests under
`host-agent/windows-display-agent/`, plus the host-agent security OpenSpec
contract. It does not require live 1C runtime, Vanessa MCP, EDT/meta snapshots
or protocol capture evidence; verification is offline Go unit tests and a
Linux-hosted Windows cross-compile.
