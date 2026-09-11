## 1. Python List-Read Fail-Loud Contract

- [x] 1.1 Add a shared helper that marks zero-row, `None` value, or all-empty
  list-read results as `ok:false` / `data_confidence:"unknown"` when refresh,
  clean-state sweep, or target-window confirmation failed.
- [x] 1.2 Apply the helper to `read_list_grid`, `read_list_column`, and
  `read_list_row` without changing populated or confirmed refreshed-empty
  results.
- [x] 1.3 Add remote-client diagnostics to uncertain list reads: searched target
  identity, discovered 1C windows, and visible UIA cells or a structured
  diagnostic gap.
- [x] 1.4 Add focused Python tests for refresh failure, refresh opt-out with
  sweep failure, confirmed empty, and remote diagnostic attachment.

## 2. Windows Host-Agent Diagnostics

- [x] 2.1 Include top-level window class names in host-agent `WindowInfo` and
  `/window_list` responses.
- [x] 2.2 Add an authenticated visible-cell diagnostic endpoint that resolves
  the requested/default 1C window and returns a bounded list of UI Automation
  text values.
- [x] 2.3 Add Go tests for class metadata, authentication on the visible-cell
  endpoint, successful visible-cell diagnostics, and `window-not-found` target
  misses.
- [x] 2.4 Keep the host-agent endpoint token/origin boundary unchanged.

## 3. Verification And Handoff

- [x] 3.1 Run the 1C verification matrix checker in preflight mode and retain
  output under `.artifacts/openspec/read-list-grid-fail-loud-and-remote-window-discovery/<run-id>/`.
- [x] 3.2 Run focused Python tests for the modified list-read contract.
- [x] 3.3 Run `go test ./...` under `host-agent/windows-display-agent`.
- [x] 3.4 Run a Windows build/compile check for the host-agent visible-cell
  code path, or record a compile/runtime gap with owner route.
- [x] 3.5 Record the Windows [redacted third-party configuration] remote-client smoke as retained
  evidence when an operator-owned Windows desktop is available, or record the
  runtime gap in the retained evidence summary.
- [x] 3.6 Run the 1C verification matrix checker in archive-gate mode.
- [x] 3.7 Run `openspec validate read-list-grid-fail-loud-and-remote-window-discovery --strict`.
- [x] 3.8 Run `git diff --check`.

## 4. OpenSpec Handoff

- [x] 4.1 Sync `qa-mcp-tool-endpoint-contract` and
  `qa-mcp-windows-host-agent-security` requirement deltas into main specs.
- [x] 4.2 Archive the change after tasks, verification, and spec sync are
  complete.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | `read_list_grid`, `read_list_column`, `read_list_row` uncertain zero-row classification in `src/qa_mcp/mcp_server.py` | Focused Python unit tests with fake refresh/window failures and successful confirmed-empty reads | Focused pytest output and retained verification summary | `.artifacts/openspec/read-list-grid-fail-loud-and-remote-window-discovery/20260707T182950Z/python-list-read-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | Windows host-agent `/window_list` class metadata and visible-cell diagnostic endpoint | Go unit tests with fake driver window/cell results; Windows build compile check | Go test output and retained verification summary | `.artifacts/openspec/read-list-grid-fail-loud-and-remote-window-discovery/20260707T182950Z/host-agent-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | Real Windows [redacted third-party configuration] `Справочник.Валюты` remote-client read | Operator-owned Windows MCP transcript showing populated rows or top-level `ok:false` with window/cell diagnostics | Retained sanitized MCP transcript and optional screenshot/UIA summary | `.artifacts/openspec/read-list-grid-fail-loud-and-remote-window-discovery/20260707T182950Z/windows-third-party-config-read-list-grid.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows GUI desktop, Docker Desktop host-agent route, licensed [redacted third-party configuration] infobase, or operator approval is available inside this Linux workspace. | The first Windows package/customer-support run must retain the transcript before claiming live [redacted third-party configuration] proof. |
