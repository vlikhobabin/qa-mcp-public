# s35-qa-host-agent-claude-effort-parity

## Why

S35 Agentic RAG solo readiness uses `qa-mcp` Windows host-agent
`POST /agent/complete` as the host bridge for subscription-backed local model
calls. The endpoint already accepts semantic request fields including
`reasoning_effort`; Codex command rendering forwards that value, while Claude
command rendering currently does not. A solo install must not silently drop the
configured effort because root readiness needs to know the effective agent/model
profile being exercised.

## What Changes

- Forward `reasoning_effort` to Claude CLI with the supported `--effort` flag.
- Preserve existing Codex effort forwarding through `model_reasoning_effort`.
- Fail closed with a typed diagnostic when a selected agent cannot honor a
  requested effort, instead of returning successful text with a downgraded
  profile.
- Return or retain bounded non-secret profile metadata for `/agent/complete`
  readiness diagnostics.

## Capabilities

- `qa-mcp-windows-host-agent-security`

## Impact

- Delivery stays inside the `qa-mcp` host-agent implementation and tests.
- No Agentic RAG transport changes are included here.
- No root Docker/profile changes are included here.
