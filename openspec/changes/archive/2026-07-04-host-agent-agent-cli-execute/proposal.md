## Why

Containerized agentic-rag cannot reach an operator-authorized local Codex or Claude CLI when the LLM backend lives on the Windows host. The qa-mcp Windows host-agent is already the tokened, SHA-pinned host bridge, so it should expose the delivered `agent_cli_execute` operation without letting containers send arbitrary argv.

## What Changes

- Add an authenticated `POST /agent/complete` operation to the Windows host-agent.
- Build host-side Codex and Claude commands from semantic request fields only: `agent`, optional `model`, optional Codex `reasoning_effort`, `prompt`, and bounded `timeout_seconds`.
- Reject unknown agents, missing CLI binaries, timeouts, empty output, bad methods, invalid JSON, and unauthorized requests with bounded fail-closed error classes.
- Extend authenticated `/health` with Codex and Claude CLI availability diagnostics.
- Update the host-agent installer/readme and tests for the new bridge.

## Capabilities

### New Capabilities
- None.

### Modified Capabilities
- `qa-mcp-windows-host-agent-security`: adds the authenticated, allowlisted host CLI execution boundary and its fail-closed behavior.

## Impact

- Touches host-agent Go code and tests under `host-agent/windows-display-agent/`.
- Touches the Windows host-agent installer and README.
- Touches OpenSpec artifacts and the existing `qa-mcp-windows-host-agent-security` capability.
- Does not touch protocol capture/replay, Python manager code, MCP provider setup, OpenSpec workflow internals, runtime lab config, live 1C runtime, Vanessa MCP, or EDT/meta snapshots. Verification is offline Go unit coverage plus OpenSpec validation.
