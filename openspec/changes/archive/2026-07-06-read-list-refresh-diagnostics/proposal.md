## Why

`read_list_grid`, `read_list_column`, and related list reads collapse host-agent
refresh failures into generic "no display backend" notes. After the historical-user
foreground-lock finding, the tool result must name the actual blocker, such as
`foreground-denied`, so operators can distinguish an unreachable agent from a
busy-desktop foreground policy problem.

## What Changes

- Preserve structured host-agent display-backend errors from `_force_list_refresh`
  and `_cold_state_sweep` instead of replacing them with generic reachability
  text.
- Include actionable refresh diagnostics in zero-row list results so
  `foreground-denied`, version mismatch, unreachable agent, and unsupported
  key failures remain visible at the MCP boundary.
- Add Python tests for list-refresh diagnostic propagation without requiring a
  live 1C runtime or Windows host.
- Record retained Windows E2E evidence requirements for a non-foreground
  `read_list_grid` returning populated rows once the host-agent contract is
  installed.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `qa-mcp-tool-endpoint-contract`: extends list-reading diagnostics so display
  refresh failures retain their structured host-agent cause and no longer imply
  the display backend is unreachable when the actual failure is foreground
  denial or another host-agent primitive result.

## Impact

- Touches Python manager/MCP code in `src/qa_mcp/mcp_server.py` and display
  backend error handling in `src/qa_mcp/protocol/display_backend.py`.
- Adds or adjusts focused Python tests under `tests/`.
- Does not change protocol read/replay semantics, the descriptor-table
  resolution fix, host-agent authentication/firewall behavior, model-A X11
  behavior, COM bridge behavior, Vanessa MCP, EDT/meta snapshots, or runtime lab
  configuration.
- Verification is mostly offline Python coverage plus retained Windows E2E
  transcript when an operator-owned Windows desktop is available.
