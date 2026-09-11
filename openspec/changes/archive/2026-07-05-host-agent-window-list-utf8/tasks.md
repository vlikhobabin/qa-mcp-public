## 1. Host-Agent Encoding

- [x] 1.1 Inspect the Windows `/window_list` title path and remove any byte or code-page conversion that can corrupt `GetWindowTextW` output.
- [x] 1.2 Preserve existing `/window_list` authentication, geometry, and response shape while returning readable Unicode titles.
- [x] 1.3 Add Go tests that prove Russian and ASCII window titles survive JSON response encoding.

## 2. Window Selection Diagnostics

- [x] 2.1 Update bootstrap/consumer diagnostics so a generic `Клиент тестирования` fallback is clearly reported as weak.
- [x] 2.2 Keep explicit `-WindowTitle` guidance visible when automatic title selection is missing or weak.

## 3. Verification

- [x] 3.1 Run `go test ./...` under `host-agent/windows-display-agent`.
- [x] 3.2 Run `GOOS=windows GOARCH=amd64 go test -c -o /tmp/qa-mcp-host-agent-window-list-utf8.test.exe .` under `host-agent/windows-display-agent`.
- [x] 3.3 Run focused bootstrap/runbook tests affected by window-title diagnostics.
- [x] 3.4 Record retained verification evidence under `.artifacts/openspec/host-agent-window-list-utf8/<run-id>/`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | Windows host-agent `/window_list` title enumeration | Go unit test with Russian title fixture and JSON response assertion | Go test output, Linux host-agent package test output | `.artifacts/openspec/host-agent-window-list-utf8/20260705T193326Z/host-agent-window-list-utf8.md` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | Real Windows 1C TestClient window matching | Read-only authenticated `/window_list` request against an operator-owned Windows host | Retained host-agent transcript with readable Russian title and selected title guidance | `.artifacts/openspec/host-agent-window-list-utf8/<run-id>/windows-window-list-smoke.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows host, GUI desktop, PowerShell runtime, or licensed 1C TestClient is available inside this Linux workspace. | The next Windows package run must retain this smoke before relying on Russian-title auto-selection. |
