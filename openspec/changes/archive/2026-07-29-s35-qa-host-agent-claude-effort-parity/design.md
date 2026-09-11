# Design: Host-Agent Claude Effort Parity

## Context

`host-agent/windows-display-agent/agent_cli.go` already models
`reasoning_effort` as a semantic request field. The Codex path renders it as
`model_reasoning_effort`, and the Claude path currently renders model and other
safe fixed flags but omits effort. Local `claude --help` on 2026-07-29 exposes
`--effort <level>`, so the supported Claude path can be explicit.

## Goals

- Preserve the caller-selected `reasoning_effort` for both Codex and Claude
  agent selections.
- Keep agent selection explicit: `agent: "claude"` must not fall back to Codex
  just because Codex is available, and vice versa.
- Keep prompt text, credentials and token values out of logs and responses.
- Provide enough bounded profile metadata for S35 root and Agentic RAG readiness
  summaries to identify the effective host-agent CLI profile.

## Non-Goals

- Do not implement Agentic RAG LLM tiering here.
- Do not add arbitrary argv support to `/agent/complete`.
- Keep Linux unit tests independently runnable. Retain source-bound
  Windows-native verification for the host-bridge change; retain additional
  Windows artifact provenance and read-only artifact smoke when the product
  host-agent executable itself is rebuilt.

## Decisions

- `reasoning_effort` remains a semantic field, not caller-supplied argv.
- Claude effort maps to `claude --effort <level>` when non-empty.
- Unsupported effort values or unsupported CLI behavior must be typed
  fail-closed; returning success after dropping effort is not allowed.
- Readiness metadata should expose only bounded fields such as agent, model,
  effort, timeout and response id. It must not expose prompt text, CLI
  credentials, token values or raw stderr beyond existing bounded diagnostics.

## Verification

- Go unit tests for Claude command rendering with effort.
- Go unit tests for Codex effort parity remaining unchanged.
- Go unit tests that explicit agent selection does not fallback to another CLI.
- Source-bound Windows-native tests for command rendering, typed effort
  rejection, bounded profile metadata, and selected-agent failure dispatch.
- If delivery rebuilds the Windows host-agent executable, additionally retain
  product artifact provenance and Windows read-only artifact smoke evidence per
  `qa-mcp/AGENTS.md`.
