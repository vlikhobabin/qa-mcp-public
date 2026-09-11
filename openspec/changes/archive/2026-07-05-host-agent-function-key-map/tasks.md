## 1. Host-Agent Keymap

- [x] 1.1 Add `F1` through `F12` virtual-key resolution for the Windows
  host-agent.
- [x] 1.2 Preserve existing key aliases for enter/return, escape/esc, tab,
  arrows, delete, backspace, space, letters, digits, and `F4`.
- [x] 1.3 Keep unsupported keys fail-closed before any desktop input is sent.

## 2. Tests And Verification

- [x] 2.1 Add Go regression coverage for `virtualKey("f5") == 0x74`.
- [x] 2.2 Add Go regression coverage for `F1` through `F12` contiguous mapping.
- [x] 2.3 Run `go test ./...` under `host-agent/windows-display-agent`.
- [x] 2.4 Run `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-function-key-map.test.exe .` under `host-agent/windows-display-agent`.
- [x] 2.5 Run the 1C verification matrix checker in preflight and archive modes.
- [x] 2.6 Run `openspec validate host-agent-function-key-map --strict`.
- [x] 2.7 Run `git diff --check`.
- [x] 2.8 Record retained verification summary under
  `.artifacts/openspec/host-agent-function-key-map/20260705T074532Z/`.

## 3. OpenSpec Handoff

- [x] 3.1 Sync the `qa-mcp-windows-host-agent-security` requirement delta into
  the main spec before archive.
- [x] 3.2 Archive `host-agent-function-key-map` after tasks and validation are
  complete.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | `host-agent/windows-display-agent` display keymap for qa-mcp list refresh | Go unit test for `virtualKey` F1-F12 and Linux host-agent test pass | Go unit test output, Linux build/test output, retained verification summary | `.artifacts/openspec/host-agent-function-key-map/20260705T074532Z/function-key-map-verification.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | Real Windows TestClient dynamic-list `F5` delivery | Read-only attach + list refresh smoke against operator-owned Windows host | Retained QA/TestClient run log or host-agent transcript when Windows desktop is available | `.artifacts/openspec/host-agent-function-key-map/20260705T074532Z/windows-f5-smoke.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows host, PowerShell runtime, GUI desktop, or licensed 1C TestClient is available inside this Linux workspace. | The first Windows package run must execute this smoke before relying on live `F5` refresh delivery. |
