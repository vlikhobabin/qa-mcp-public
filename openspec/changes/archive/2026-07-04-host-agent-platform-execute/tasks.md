## 1. Host-Agent Endpoint

- [x] 1.1 Register `POST /platform/execute` behind the existing `withAuth` middleware.
- [x] 1.2 Add request/response types and validation for allowlisted `executable`, argv, optional `cwd`, bounded `timeout_seconds`, `operation`, `mutation_class`, and `operator_intent`.
- [x] 1.3 Implement catalog-only executable resolution for `ibcmd`, `designer`, `1cv8`, and `1cv8c`, rejecting path-like or off-allowlist executable values before spawn.
- [x] 1.4 Implement `platform_command_execute` operator-intent enforcement while allowing `platform_command_plan` through the same allowlist/catalog boundary.
- [x] 1.5 Run commands without a shell, with empty stdin, process-group timeout kill, exit-code reporting, and bounded stdout/stderr.
- [x] 1.6 Redact secret-bearing request arguments and echoed diagnostics before returning stdout, stderr, or error detail.
- [x] 1.7 Extend authenticated `/health` with bounded 1C platform catalog diagnostics.

## 2. Documentation

- [x] 2.1 Bump `AgentVersion` so SHA-pin consumers detect the new host-agent binary.
- [x] 2.2 Update `host-agent/README.md` with the `/platform/execute` request/response contract, security boundary, catalog configuration, and Windows smoke command.

## 3. Tests And Verification

- [x] 3.1 Add fake-platform executable unit tests for valid allowlisted execution, off-allowlist rejection before spawn, path-like executable rejection, missing operator intent, auth-before-body-parse, timeout, stderr/stdout bounds, secret redaction, and health catalog diagnostics.
- [x] 3.2 Run `go test ./...` under `host-agent/windows-display-agent`.
- [x] 3.3 Run `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-platform-execute.test.exe .` under `host-agent/windows-display-agent`.
- [x] 3.4 Run the 1C verification matrix checker in preflight and archive modes.
- [x] 3.5 Run `openspec validate host-agent-platform-execute --strict`.
- [x] 3.6 Run `git diff --check`.
- [x] 3.7 Record retained verification summaries under `.artifacts/openspec/host-agent-platform-execute/20260704T191759Z/`.

## 4. OpenSpec Handoff

- [x] 4.1 Sync the `qa-mcp-windows-host-agent-security` requirement delta into the main spec before archive.
- [x] 4.2 Archive `host-agent-platform-execute` after tasks and validation are complete.
- [x] 4.3 Keep protocol capture/replay evidence index updates as N/A because the change adds no new native TestClient protocol claim.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | `host-agent/windows-display-agent` `/platform/execute` host executor | Authenticated endpoint, allowlisted executable resolution, policy-field validation, timeout kill, bounded/redacted output | Go unit tests, Windows cross-compile, retained verification summary | `.artifacts/openspec/host-agent-platform-execute/20260704T191759Z/platform-execute-verification.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Delivery or runtime apply | Real Windows host `ibcmd` smoke | Read-only `ibcmd`/platform version or file-base read-only command against an operator-owned Windows host | Retained Windows smoke transcript when host is available | `.artifacts/openspec/host-agent-platform-execute/20260704T191759Z/windows-host-smoke.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows host, PowerShell runtime, or licensed host 1C platform is available inside this Linux workspace. | The first Windows package run must execute this smoke before relying on real host execution. |
| Source/import workflow | `admin-mcp` platform command planning and mutation policy | Admin provider sends already validated command plans and operator-intent evidence | Admin component tests and policy evidence under its peer card | N/A | N/A | `/opt/ai-dev-suite-for-1c/admin-mcp` | The admin client and mutation policy are explicitly out of scope for this qa-mcp executor card. | End-to-end admin execution remains incomplete until the peer admin-mcp transport card lands. |
