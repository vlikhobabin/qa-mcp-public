## Context

The Windows host-agent is a tokened HTTP daemon used when qa-mcp runs in a thin Linux container while the operator desktop and local tools live on the Windows host. It already centralizes host-side trust controls: constant-time token checks, origin allowlisting, failure rate limiting, binary SHA reporting behind auth, and installer-scoped network exposure.

The root suite contract has already defined `agent_cli_execute` as the host-bridge operation that lets a container ask the host to run an operator-authorized Codex or Claude CLI. This qa-mcp change implements only the host side of that contract. It does not add agentic-rag consumer transport and does not make containers send arbitrary command lines.

No 1C TestClient protocol capture, replay, frame ranges, dynamic fields, runtime lab cleanup, Vanessa MCP, live 1C runtime, or EDT/meta evidence is required. Verification is offline host-agent Go unit coverage plus OpenSpec validation.

## Goals / Non-Goals

**Goals:**
- Add `POST /agent/complete` behind the existing `withAuth` middleware.
- Accept semantic request fields and construct host-owned Codex or Claude argv internally.
- Bound process lifetime, stderr/detail size, request body size, and timeout values.
- Kill the spawned process group on timeout.
- Return only final model text and a stable response id when execution succeeds.
- Extend authenticated health diagnostics with Codex/Claude PATH availability.
- Keep prompt bodies and CLI credentials out of logs, errors, and tests.

**Non-Goals:**
- No agentic-rag client transport in this repository.
- No arbitrary argv, shell command execution, user-selected executable paths, or environment export.
- No bundling or storing Codex/Claude credentials.
- No live 1C runtime or UI automation execution.
- No neutral host-bridge rename.

## Decisions

### Semantic allowlist, not argv forwarding

The request carries `agent`, optional `model`, optional Codex `reasoning_effort`, `prompt`, and `timeout_seconds`. The handler maps `agent` through an internal allowlist:

- `codex`: `codex exec --ephemeral --ignore-user-config --skip-git-repo-check -c approval_policy="never" --sandbox read-only --color never --output-last-message <tmp> ... -`
- `claude`: `claude -p --output-format text --strict-mcp-config --tools "" --system-prompt <constant-persona> ...`

Unknown agents fail before process creation. This keeps the container contract semantic and prevents command injection through argv shape.

Alternative considered: accept a container-provided command line. Rejected because it would cross the host trust boundary and bypass the suite contract.

### Direct process execution with PATH lookup

The host-agent resolves the selected executable with `exec.LookPath` and runs it without a shell. On Windows this supports `codex.cmd` through PATHEXT and `claude.exe` normally. Missing binaries fail closed with a readiness-friendly error code.

Alternative considered: hard-code full executable paths. Rejected because Codex/Claude installation paths vary by operator and shell profile.

### Output handling differs by CLI

Codex writes the final message to a host temporary file via `--output-last-message`; the handler reads and removes the file after process completion. Claude returns text on stdout; the handler trims whitespace and strips one wrapping Markdown code fence when present.

Both paths reject empty final text. Stderr is included only as a bounded diagnostic detail on failures and never includes the prompt body.

### Timeout and process cleanup

The handler uses a context with a bounded timeout and starts each child in its own process group where the platform supports it. On timeout, it kills the process group and returns a fail-closed timeout response.

Alternative considered: rely on command context cancellation only. Rejected because child process trees can outlive their parent CLI wrapper.

### Auth before validation

`/agent/complete` is registered through `withAuth`, so missing/invalid tokens, hostile browser origins, and auth rate limiting run before JSON validation or any spawn decision. This preserves the existing sensitive-endpoint posture.

## Risks / Trade-offs

- CLI wrappers may emit authorization or setup prompts instead of final text -> return a bounded `cli-failed` or `empty-output` response and surface PATH availability through health.
- Windows process-group semantics differ from Linux test behavior -> isolate process-group setup behind small platform helpers and unit-test timeout cleanup with fake CLI stubs on Linux CI.
- The host-agent executes local model CLIs and can consume operator quota -> require explicit tokened access, semantic agent allowlist, and bounded timeout.
- Prompt bodies are sensitive -> never log request payloads, never echo prompt in errors, and keep tests focused on response classes.

## Migration Plan

1. Implement handler, command runner, platform process-group helpers, and tests.
2. Extend `/health` authenticated output with CLI availability.
3. Update installer guidance to verify at least one selected CLI is present.
4. Update host-agent docs with the new endpoint contract and security boundary.
5. Bump `AgentVersion`; the existing SHA-pin/reinstall flow then detects the new binary.

Rollback is reinstalling the previous host-agent binary and SHA pin. The endpoint is additive and does not change existing display primitives.

## Open Questions

- None for this host-side implementation. The agentic-rag consumer transport is tracked in its own repository/card.
