# Host-agent /platform/execute: run 1C platform CLI (ibcmd/designer) on the host

## Status
4.done

## Owner
Codex

## OpenSpec Stage
archived

## Source
- Full-product E2E gap (2026-07-04): containerized `admin-mcp` (and `config-mcp`
  import execution routed through admin) must run 1C platform binaries
  (`ibcmd`/`designer`) that live on the Windows host, not in the Linux container.
  `admin-mcp`'s controlled runner fails closed when host-agent execution is
  required (`host_agent_execution_required` → "the local controlled runner will
  not start platform commands"), and the Go host-agent has **no** platform
  execution endpoint (only display + `/agent/complete`).
- Peer card: admin-mcp `host-agent-platform-execution-transport` (the client).
- Contract: root `suite-windows-host-bridge` spec already names the
  `platform_command_plan` / `platform_command_execute` safety classes.

## Summary
Add a `POST /platform/execute` handler to the qa-mcp Windows host-agent
(`host-agent/windows-display-agent/`) under the existing `withAuth` middleware,
so a container can run an **allowlisted** 1C platform binary on the Windows host
and get back the exit code, bounded stdout/stderr and evidence. The host-agent
is the **executor**; the owning provider (`admin-mcp`) owns the mutation policy
(plan-vs-execute, operator intent, mutation boundary) and only sends a validated
plan. The host-agent enforces defense-in-depth: a fixed executable allowlist and
required policy fields, fail-closed otherwise.

This is the platform-command half of the Windows host bridge (the LLM half
`/agent/complete` shipped in `83f1184`).

## Wire contract (agreed with the admin client card)
`POST /platform/execute` (reuse `withAuth`: token + origin allowlist + rate-limit):
```json
{
  "executable": "ibcmd",                 // allowlist {ibcmd, designer, 1cv8, 1cv8c}; NOT arbitrary
  "argv": ["infobase", "dump", "..."],   // already-built argv from admin's CommandPlan
  "cwd": "C:/1C_BASES/demo_1_0_41_3",     // optional working dir
  "timeout_seconds": 600,
  "operation": "platform_command_execute", // or platform_command_plan
  "mutation_class": "mutating|read_only",   // from admin mutation boundary
  "operator_intent": "<evidence token/text>" // required for _execute
}
```
Response:
```json
{ "ok": true, "exit_code": 0, "stdout": "...", "stderr": "...",
  "response_id": "platform-exec", "executable_resolved": "C:/Program Files/1cv8/8.3.27.2130/bin/ibcmd.exe" }
```
Fail-closed `{ "ok": false, "error": <code>, "detail": ... }` for: executable not
in allowlist, executable not found in the configured platform catalog,
`platform_command_execute` without `operator_intent`, timeout, oversize body.

## Fix / implementation
- New `platform_exec.go` handler `handlePlatformExecute` registered in `main.go`
  under `withAuth`.
- **Executable allowlist** = 1C platform binaries only (`ibcmd`, `designer`/1cv8
  designer mode, `1cv8`, `1cv8c`). Resolve via the configured platform catalog
  (`C:\Program Files\1cv8\<ver>\bin`) — reject anything off-allowlist or outside
  the catalog. Never accept an absolute arbitrary path from the caller.
- **Plan vs execute:** `platform_command_execute` requires `operator_intent`
  present (fail-closed if absent, mirroring the contract). `platform_command_plan`
  runs validation/dry semantics only.
- Run with a new process group + timeout kill (reuse the `agent_cli.go`
  `runCommandWithPromptOutput` process-group pattern; here stdin is empty).
- Capture exit code + bounded stdout/stderr; redact secret-bearing args
  (connection strings, `/P` passwords) from any echoed detail; no prompt/secret
  logging.
- Extend `/health` to report platform-catalog discovery (which 1C versions/bin
  are visible) alongside the existing `agent_cli` availability.

## Acceptance
- `POST /platform/execute` with a valid token + allowlisted `ibcmd` + argv runs
  the real binary on the host and returns exit code + bounded output.
- Off-allowlist executable (or an absolute path outside the catalog) → rejected
  **before** spawn; `platform_command_execute` without `operator_intent` →
  fail-closed; timeout → process-group kill + fail-closed.
- Secret-bearing args are redacted from returned detail; no secrets logged.
- First Windows-host smoke target: `ibcmd --version` or a read-only file-base
  operation resolves and returns output from the configured platform catalog.
  This Linux delivery records the smoke as a host-availability evidence
  boundary because no Windows host is attached here.
- Tests pass on Linux CI with a fake/stub executable (handler independent of the
  Win32 display driver); Windows cross-compile build stays green.

## Scope
- Component-local (qa-mcp host-agent): `platform_exec.go` handler + executable
  allowlist + catalog resolution + process-group/timeout + evidence/redaction +
  `/health` catalog + installer/README + tests.
- Out of scope: admin's mutation policy / plan-vs-execute decision (owned by
  admin, its own card); config import planning (config plans, admin executes).

## Safety
- Token-auth (reuse), **executable allowlist** (no arbitrary binaries/paths),
  operator-intent required for execute, redaction of secret args, bounded
  stderr, timeout kill, fail-closed. The host-agent executes only what an owning
  provider validated and sent.

## Affected Repositories
- qa-mcp (host-agent). Consumes root `suite-windows-host-bridge`
  (`platform_command_*`); paired with admin-mcp client card.

## Change Set
1. `host-agent-platform-execute` — `/platform/execute` handler (allowlist,
   catalog resolution, plan/execute, process-group+timeout, evidence/redaction),
   `/health` catalog, README, tests
   (cap `qa-mcp-windows-host-agent-security`).

## Change 1: `host-agent-platform-execute`

### Why
Containerized admin/config flows need host-side 1C platform binaries without
putting proprietary 1C binaries inside the Linux container. The qa-mcp
Windows host-agent is the existing authenticated host bridge, but it currently
has no platform-command execution endpoint.

### Goal
Add an authenticated, allowlisted `POST /platform/execute` executor to the
qa-mcp Windows host-agent, with catalog-only 1C executable resolution,
policy-field validation, process timeout cleanup, bounded/redacted output, and
health diagnostics.

### Scope
- `host-agent/windows-display-agent/` Go handler, execution helper, health
  diagnostics, and tests.
- `host-agent/README.md` contract and smoke guidance.
- `openspec/specs/qa-mcp-windows-host-agent-security/spec.md` requirement
  update through the OpenSpec delta.
- Out of scope: `admin-mcp` command planning/mutation policy and config import
  routing.

### Acceptance
- Authenticated allowlisted `ibcmd`/`1cv8`/`1cv8c`/`designer` request executes
  without a shell and returns exit code plus bounded/redacted output.
- Off-allowlist or path-like executable is rejected before spawn.
- `platform_command_execute` without `operator_intent` fails closed.
- Timeout kills the process group and returns a bounded timeout diagnostic.
- Authenticated `/health` reports platform catalog diagnostics.
- Go tests, Windows cross-compile, OpenSpec validation, and retained matrix
  evidence pass in this Linux delivery; real Windows `ibcmd` smoke is recorded
  as a host-availability evidence boundary when no Windows host is attached.

### Depends On
- Root `suite-windows-host-bridge` platform command safety-class contract.
- Peer admin-mcp `host-agent-platform-execution-transport` card for the client
  and mutation policy.

### Related
- `openspec/changes/archive/2026-07-04-host-agent-platform-execute/`

### Notes For `$openspec-ff-change`
- Use modified capability `qa-mcp-windows-host-agent-security`.
- Include the 1C verification matrix because this is a host execution surface
  for 1C platform commands.
- Keep live Windows platform execution as retained evidence if available; in
  the Linux-only pass, record it as N/A with residual risk rather than faking
  host evidence.

## Verify
- passed: `go test ./...` in `host-agent/windows-display-agent`
- passed: `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-platform-execute.test.exe .`
- passed: matrix checker preflight/archive
  (`.artifacts/openspec/host-agent-platform-execute/20260704T191759Z/`)
- passed: `openspec validate host-agent-platform-execute --strict`
- passed: `openspec validate qa-mcp-windows-host-agent-security --strict`
- passed: `openspec validate --all`
- passed: `git diff --check`

## Archive
- `openspec/changes/archive/2026-07-04-host-agent-platform-execute/`

## Related
- `openspec/changes/archive/2026-07-04-host-agent-platform-execute/`
- `.artifacts/openspec/host-agent-platform-execute/20260704T191759Z/platform-execute-verification.md`
- `.artifacts/openspec/host-agent-platform-execute/20260704T191759Z/windows-host-smoke.md`

## Result
delivered and archived; `/platform/execute` host-agent executor, catalog
health, README/installer wiring, tests, and synced security spec are complete;
published in the scoped host-agent delivery commit

## Next
- none

## Log
- 2026-07-04T00:00:00Z accepted into `2.todo` and decomposed into `host-agent-platform-execute`.
- 2026-07-04T19:18:00Z moved to `3.inprogress`; implementation and focused host-agent tests started.
- 2026-07-04T19:24:00Z verified, synced `qa-mcp-windows-host-agent-security`, archived, and moved to `4.done`.
- 2026-07-04T19:28:00Z published in the scoped host-agent delivery commit.
