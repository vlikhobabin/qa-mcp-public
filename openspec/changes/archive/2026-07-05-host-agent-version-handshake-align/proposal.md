## Why

qa-mcp's remote display backend currently pins `HOST_AGENT_VERSION` to
`0.1.0-card124`, while the installed host-agent reports
`0.1.0-platform-execute`. That mismatch makes every remote keystroke fail at
handshake unless an operator supplies `QA_MCP_HOST_AGENT_EXPECTED_VERSION`.

## What Changes

- Align the default qa-mcp host-agent version expectation with the current
  supported host-agent build family.
- Keep `QA_MCP_HOST_AGENT_EXPECTED_VERSION` as an exact override for operators
  who intentionally pin a specific build.
- Preserve honest diagnostics for unsupported version mismatches.
- Add Python regression coverage for default-compatible versions, override
  behavior, and mismatch failure.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `qa-mcp-windows-host-agent-security`: clarifies the authenticated host-agent
  handshake compatibility boundary and mismatch diagnostics.

## Impact

- Touches Python display-backend handshake code and tests under
  `src/qa_mcp/protocol/` and `tests/`.
- May touch the Go `AgentVersion` string when the host-agent binary changes in
  this card, while preserving compatibility with `0.1.0-platform-execute`.
- Does not change host-agent auth, token storage, firewall scope, process
  execution policy, native protocol capture/replay, live 1C data, Vanessa MCP,
  EDT/meta snapshots, or runtime lab configuration.
