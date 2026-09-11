## 1. Host-Agent Endpoint

- [x] 1.1 Register `POST /agent/complete` behind the existing `withAuth` middleware.
- [x] 1.2 Add request/response types and validation for allowlisted `agent`, non-empty `prompt`, optional `model`, optional Codex `reasoning_effort`, and bounded `timeout_seconds`.
- [x] 1.3 Implement host-owned Codex argv construction with `exec.LookPath`, `--output-last-message`, stdin prompt delivery, temp-file cleanup, bounded stderr, and empty-output failure.
- [x] 1.4 Implement host-owned Claude argv construction with `exec.LookPath`, stdin prompt delivery, bounded stderr, single wrapping code-fence stripping, and empty-output failure.
- [x] 1.5 Run the selected CLI in a new process group where supported and terminate the process group on timeout.
- [x] 1.6 Extend authenticated `/health` with bounded Codex and Claude PATH availability diagnostics.

## 2. Installer And Documentation

- [x] 2.1 Bump `AgentVersion` so SHA-pin consumers detect the new host-agent binary.
- [x] 2.2 Update `host-agent/install-windows-host-agent.ps1` to verify that at least one selected agent CLI is present on PATH during install.
- [x] 2.3 Update `host-agent/README.md` with the `/agent/complete` contract, security boundary, health diagnostics, and install-time CLI check.

## 3. Tests And Verification

- [x] 3.1 Add fake-CLI unit tests for Codex success, Claude success, unknown-agent fail-closed before spawn, missing auth before prompt validation, missing CLI, timeout process cleanup, empty output, and health CLI availability.
- [x] 3.2 Run `go test ./...` under `host-agent/windows-display-agent`.
- [x] 3.3 Run `openspec validate host-agent-agent-cli-execute --strict`.
- [x] 3.4 Run `git diff --check`.
- [x] 3.5 Record Windows-native verification as installer/script review plus fake-CLI command-shape coverage; no live Windows CLI execution is required in this Linux workspace.

## 4. OpenSpec Handoff

- [x] 4.1 Sync the `qa-mcp-windows-host-agent-security` requirement delta into the main spec before archive.
- [x] 4.2 Prepare the completed change for archive with validation evidence.
- [x] 4.3 Keep protocol capture/replay evidence index updates as N/A because the change adds no new native 1C protocol claim.

## Verification Notes

- `go test ./...` passed under `host-agent/windows-display-agent`.
- `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent.test.exe .` passed.
- `openspec validate host-agent-agent-cli-execute --strict` passed.
- `git diff --check` passed.
- `pwsh` is not installed in this Linux workspace, so the PowerShell installer parse check could not be executed here.
