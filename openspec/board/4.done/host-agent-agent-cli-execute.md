# Host-agent agent_cli_execute endpoint (LLM CLI bridge for agentic-rag)

## Status
4.done

## Owner
Codex

## OpenSpec Stage
archived

## Source
- Suite finding **D** (Docker data-plane E2E, 2026-07-04): containerized
  `agentic-rag` `research.answer` fails closed because its LLM backend is a
  **local Codex/Claude CLI**, unreachable from a Linux container on a Windows
  host.
- Suite contract **already delivered** (root commit `be0d3d0`): the Windows
  host-bridge spec now defines the `agent_cli_execute` operation safety class —
  `openspec/specs/suite-windows-host-bridge/spec.md` (root repo). This card
  implements the host side of that contract.
- Root design card: `openspec/board/4.done/agentic-rag-llm-host-agent-bridge.md`.

## Summary
The qa-mcp Windows host agent (`host-agent/windows-display-agent/main.go`) is a
tokened Go HTTP daemon that already carries constant-time token auth
(`X-QA-MCP-Agent-Token`), origin allowlist, a failure rate-limiter and binary
SHA-pinning. Add a new operation class — `agent_cli_execute` — as a single
`POST /agent/complete` handler under the **existing** `withAuth` middleware, so
a container can have the operator's already-installed, already-authorized Codex
or Claude CLI run **on the host** and return the final model text.

This is the suite's chosen close-out for finding D (host-agent execution bridge,
per architecture doc Р4/Р8). The consumer side is a native `host_bridge`
transport in agentic-rag (its own card). The host agent owns all CLI-specific
knowledge; the container sends only semantics — **never** an arbitrary argv.

> Ownership note: this endpoint serves agentic-rag but lives in the qa-mcp
> host-agent daemon by suite decision (one bridge, one install, one token; Р6).
> A future neutral rename to a suite-level host-bridge is tracked separately
> with the namespace migration — out of scope here.

## Contract (what to implement — matches the delivered root spec)
Request `POST /agent/complete` (reuse `withAuth`: same token, origin allowlist,
rate-limit):
```json
{
  "agent": "codex",              // allowlisted {codex,claude}; NOT an argv
  "model": "gpt-5.5",            // optional -> CLI --model
  "reasoning_effort": "low",     // optional (codex: -c model_reasoning_effort)
  "prompt": "<stdin body built by agentic-rag>",
  "timeout_seconds": 300
}
```
Response: `{ "ok": true, "text": "...", "response_id": "codex-cli" }`.
Fail-closed `{ "ok": false, "error": <code>, "detail": ... }` for: unknown/
non-allowlisted agent, CLI missing from PATH / unauthorized, timeout, empty
output.

**Host-side command construction (mirror the agentic-rag transports):**
- `codex`: `codex exec --ephemeral --ignore-user-config --skip-git-repo-check -c
  approval_policy="never" --sandbox read-only --color never --output-last-message
  <hosttmp> [-c model_reasoning_effort="…"] [--model …] -`; stdin = `prompt`;
  read `<hosttmp>` for the final message.
- `claude`: `claude -p --output-format text --strict-mcp-config --tools ""
  --system-prompt <backend-persona> [--model …]`; stdin = `prompt`; read stdout;
  strip one wrapping Markdown code fence. (`<backend-persona>` neutralizes the
  Claude Code agent persona — host-side constant.)
- Spawn in a new process group; kill the group on timeout (mirror
  `agentic-rag/src/agentic_rag/llm/_subprocess.py`).
- **Windows exec nuance:** resolve `codex` via `exec.LookPath` (it is a
  `codex.cmd` shim on Windows); `claude` is `claude.exe`. Handle PATHEXT.

## Acceptance
- `POST /agent/complete` with a valid token + allowlisted `codex` or `claude` +
  `prompt` + bounded timeout returns the final model text; the prompt body and
  local CLI credentials are never logged.
- Non-allowlisted agent is rejected **before** spawning any process.
- CLI missing from PATH / unauthorized → fail-closed with a bounded failure
  class suitable for readiness diagnostics.
- Timeout terminates the process group and returns a fail-closed timeout
  response with bounded stderr.
- Missing/invalid token is rejected before prompt validation or process spawn.
- `/health` reports `codex`/`claude` availability on PATH; `AgentVersion` and
  the SHA-pin are bumped; the installer verifies the chosen CLI is present.
- Tests pass on Linux CI using a fake-CLI stub (the handler does not depend on
  the Win32 display driver).

## Scope
- Component-local (qa-mcp host-agent). New `/agent/complete` handler + host-side
  argv build + process-group/timeout + output read; `/health` extension;
  `AgentVersion`/sha bump; `install-windows-host-agent.ps1` CLI-present check;
  README delta; tests.
- Out of scope: agentic-rag transport (its own card); neutral host-bridge
  rename; any 1C-platform op.

## Safety
- Token-auth (reuse), agent allowlist, **no-secret logging** (never log the
  `prompt` body or CLI credentials), bounded stderr, timeout kill, fail-closed.
- The endpoint runs the operator's own authorized CLI under their session; it
  does not embed or ship credentials.

## Affected Repositories
- qa-mcp (host-agent). Consumes the root `suite-windows-host-bridge` contract.

## Change Set
1. `host-agent-agent-cli-execute` — `/agent/complete` handler implementing the
   `agent_cli_execute` contract (allowlist, host-side argv, process-group +
   timeout, output read, fail-closed), `/health` CLI-availability, version/sha
   bump, installer + README + tests (cap `qa-mcp-windows-host-agent-security`).

## Change 1: `host-agent-agent-cli-execute`

### Why
Containerized `agentic-rag` needs an LLM backend that runs on the Windows host
where the operator's authorized Codex/Claude CLI is installed, while preserving
the host-agent security boundary.

### Goal
Implement the host-agent side of `agent_cli_execute` as an authenticated
semantic bridge: the container sends agent intent and prompt text, and the host
agent constructs and supervises the allowlisted CLI command locally.

### Scope
- Add `POST /agent/complete` behind existing token/origin/rate-limit middleware.
- Add host-owned Codex and Claude command construction, bounded timeout, process
  group cleanup, output extraction, and fail-closed error mapping.
- Extend authenticated `/health` with CLI PATH availability.
- Update `AgentVersion`, installer guidance/checks, README, tests and the
  `qa-mcp-windows-host-agent-security` spec.
- Exclude agentic-rag consumer transport, neutral host-bridge rename and live
  1C runtime behavior.

### Acceptance
- Valid token + allowlisted `codex` or `claude` + prompt + bounded timeout
  returns final model text without logging prompt or credentials.
- Non-allowlisted agent is rejected before process spawn.
- Missing CLI, CLI failure, timeout and empty output return bounded fail-closed
  response classes.
- Missing/invalid token is rejected before prompt validation or process spawn.
- `/health` reports Codex/Claude PATH availability behind auth.
- Linux CI can verify behavior with fake CLI stubs.

### Depends On
- Root host-bridge contract commit `be0d3d0`.

### Related
- `openspec/changes/host-agent-agent-cli-execute/`

### Notes For `$openspec-ff-change`
- This is not a 1C runtime/card matrix change; protocol capture/replay evidence
  is N/A.
- Include Windows-native verification as installer/script review plus host-agent
  command-shape coverage in Go tests.

## Related
- `openspec/changes/archive/2026-07-04-host-agent-agent-cli-execute/`
- publish commit recorded in git history and OPSX final summary
- `.runtime/opsx/delivery-manifests/host-agent-agent-cli-execute.json` (ignored handoff state)

## Verify
- `go test -count=1 ./...` under `host-agent/windows-display-agent` — passed.
- `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent.test.exe .` under `host-agent/windows-display-agent` — passed.
- `openspec validate host-agent-agent-cli-execute --strict` — passed before archive.
- `openspec validate qa-mcp-windows-host-agent-security --strict` — passed.
- `openspec validate --all` — passed.
- `git diff --check` — passed.
- `pwsh` is not installed in this Linux workspace, so the PowerShell installer parse check was not executed here.

## Archive
- `openspec/changes/archive/2026-07-04-host-agent-agent-cli-execute/`

## Result
Published the qa-mcp Windows host-agent side of `agent_cli_execute`: authenticated `/agent/complete`, host-owned Codex/Claude command construction, timeout process-group cleanup, bounded fail-closed errors, prompt redaction from failure detail, authenticated CLI availability in `/health`, version bump, installer `-AgentCli` PATH check, README guidance and fake-CLI test coverage.

## Next
- none

## Log
- 2026-07-04: Accepted and decomposed into one card-owned OpenSpec change; artifacts prepared for implementation.
- 2026-07-04: Started implementation under `$opsx-do`.
- 2026-07-04: Implemented, verified, synced `qa-mcp-windows-host-agent-security`, and archived `host-agent-agent-cli-execute`.
- 2026-07-04: Published with scoped OPSX commit.
