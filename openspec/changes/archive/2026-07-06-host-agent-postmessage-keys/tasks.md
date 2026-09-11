## 1. Host-Agent Input Contract

- [x] 1.1 Add a target-window key delivery path for `F5` and `Escape` using
  Win32 key-down/key-up window messages.
- [x] 1.2 Route `/send_keys` requests containing only focus-independent refresh
  keys through the no-focus target-window path while preserving resolved target
  metadata.
- [x] 1.3 Keep other key/chord requests on the existing foreground-coupled input
  path and preserve fail-closed unsupported-key behavior.
- [x] 1.4 Convert denied `SetForegroundWindow` failures into a structured
  `foreground-denied` host-agent result with a non-500 HTTP status.
- [x] 1.5 Bump `AgentVersion`, `HOST_AGENT_VERSION`, and the bounded compatible
  version set for the changed input contract.

## 2. Tests And Evidence

- [x] 2.1 Add Go tests for focus-independent key classification and `/send_keys`
  no-focus routing.
- [x] 2.2 Add Go tests for structured `foreground-denied` error mapping.
- [x] 2.3 Add Python tests proving the new host-agent version is accepted by the
  default remote display backend handshake.
- [x] 2.4 Run the 1C verification matrix checker in preflight mode and retain
  output under `.artifacts/openspec/host-agent-postmessage-keys/20260706T140652Z/`.
- [x] 2.5 Run `go test ./...` under `host-agent/windows-display-agent`.
- [x] 2.6 Run `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-postmessage-keys.test.exe .` under `host-agent/windows-display-agent`.
- [x] 2.7 Run focused Python tests for host-agent version compatibility.
- [x] 2.8 Record the Windows E2E transcript for non-foreground
  `read_list_grid` when an operator-owned Windows desktop is available, or
  record the runtime gap in the retained evidence summary.
- [x] 2.9 Run the 1C verification matrix checker in archive-gate mode.
- [x] 2.10 Run `openspec validate host-agent-postmessage-keys --strict`.
- [x] 2.11 Run `git diff --check`.

## 3. OpenSpec Handoff

- [x] 3.1 Sync the `qa-mcp-windows-host-agent-security` requirement delta into
  the main spec before archive.
- [x] 3.2 Archive `host-agent-postmessage-keys` after tasks, verification, and
  spec sync are complete.
