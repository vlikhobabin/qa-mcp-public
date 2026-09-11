## Context

The existing Windows host-agent exposes desktop primitives and the
`/agent/complete` CLI bridge behind `withAuth`, which provides token checks,
origin allowlisting, and failed-auth rate limiting before request bodies are
parsed. Platform command execution has a different safety boundary: the
owning provider (`admin-mcp`) owns command planning, mutation classification,
operator intent, and plan-vs-execute policy, while the host-agent is the
host-side executor that can see installed 1C binaries.

The root `suite-windows-host-bridge` contract already defines
`platform_command_plan` and `platform_command_execute` as bridge safety
classes. This change implements the qa-mcp host-agent side without moving
admin policy into qa-mcp.

## Goals / Non-Goals

**Goals:**
- Add an authenticated `POST /platform/execute` endpoint.
- Allow only fixed 1C platform executable names: `ibcmd`, `designer`, `1cv8`,
  and `1cv8c`.
- Resolve executables from configured platform catalog roots such as
  `C:\Program Files\1cv8\<version>\bin`, and reject absolute arbitrary paths.
- Fail closed when operation, mutation class, timeout, executable, or operator
  intent requirements are not met.
- Return bounded stdout/stderr, exit code, response id, and resolved executable
  metadata.
- Redact password-like arguments from diagnostics.
- Reuse the existing process-group timeout behavior and authenticated
  health-reporting pattern.

**Non-Goals:**
- Do not implement `admin-mcp` command planning, mutation policy, operator
  approval, or config import routing.
- Do not add arbitrary shell execution or arbitrary argv/executable path
  support.
- Do not add new native TestClient protocol claims or raw protocol captures.
- Do not require a live Windows host in the Linux CI pass; record the residual
  Windows-host smoke risk separately.

## Decisions

1. **Host-agent enforces an executor allowlist, admin owns policy.** The
   request must carry `operation`, `mutation_class`, and for
   `platform_command_execute` a non-empty `operator_intent`. The host-agent
   does not decide whether an admin operation should be allowed beyond these
   defense-in-depth fields.

2. **Catalog-only executable resolution.** Request `executable` is treated as a
   semantic name. The handler maps `designer` to `1cv8` with `DESIGNER` prepended
   to the command argv, and maps the other allowlisted names to executable
   basenames. It searches configured platform catalog roots and PATH only for
   test/dev fallback. Absolute request paths, `..`, path separators, and
   off-allowlist names fail before spawn.

3. **Bounded process execution mirrors `/agent/complete`.** The handler uses a
   request-scoped timeout, starts a new process group where supported, kills the
   group on timeout, and returns bounded stdout/stderr. Stdin is empty.

4. **Redaction is argument-aware.** Returned diagnostics and stderr/stdout
   details redact secret-bearing arguments such as `/P`, `--password`,
   `pwd=...`, `password=...`, and connection strings containing passwords.

5. **Health reports discovery only after auth.** Authenticated `/health`
   reports bounded platform catalog availability by executable/version. Public
   unauthenticated clients still receive no detailed status because `/health`
   remains behind `withAuth`.

## Risks / Trade-offs

- **Windows catalog variance** -> Support explicit catalog roots through an
  environment variable and keep PATH fallback only for tests/dev diagnostics.
- **Caller sends a semantically dangerous but allowlisted command** -> The
  host-agent still requires policy fields, but final mutation authorization
  remains with `admin-mcp`.
- **Secret leakage through command output** -> Bound output and redact known
  request-argument secret shapes before response construction.
- **No attached Windows host during this Linux delivery** -> Retain Go unit,
  cross-compile, and OpenSpec evidence here; record the Windows `ibcmd`
  smoke as a follow-up evidence boundary with residual risk.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `host-agent/windows-display-agent` `/platform/execute` host executor | Authenticated endpoint, allowlisted executable resolution, policy-field validation, timeout kill, bounded/redacted output | Go unit tests, Windows cross-compile, retained verification summary | `.artifacts/openspec/host-agent-platform-execute/20260704T191759Z/platform-execute-verification.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | Real Windows host `ibcmd` smoke | Read-only `ibcmd`/platform version or file-base read-only command against an operator-owned Windows host | Retained Windows smoke transcript when host is available | `.artifacts/openspec/host-agent-platform-execute/20260704T191759Z/windows-host-smoke.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows host, PowerShell runtime, or licensed host 1C platform is available inside this Linux workspace. | The first Windows package run must execute this smoke before relying on real host execution. |
| Source/import workflow | `admin-mcp` platform command planning and mutation policy | Admin provider sends already validated command plans and operator-intent evidence | Admin component tests and policy evidence under its peer card | N/A | N/A | `/opt/ai-dev-suite-for-1c/admin-mcp` | The admin client and mutation policy are explicitly out of scope for this qa-mcp executor card. | End-to-end admin execution remains incomplete until the peer admin-mcp transport card lands. |
