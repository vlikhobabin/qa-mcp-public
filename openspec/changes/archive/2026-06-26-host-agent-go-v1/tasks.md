## 1. Go Agent Skeleton

- [x] 1.1 Add `host-agent/windows-display-agent/` with `go.mod`, package
  layout and deterministic build instructions.
- [x] 1.2 Implement HTTP routing for `/version`, `/health`, `/send_keys`,
  `/type`, `/click`, `/screenshot`, and `/window_list`.
- [x] 1.3 Add token validation and stable JSON error responses.

## 2. Win32 Primitives

- [x] 2.1 Implement Unicode `SendInput` typing and key/chord mapping.
- [x] 2.2 Implement mouse click via `SendInput`.
- [x] 2.3 Implement top-level window enumeration with title, pid and geometry.
- [x] 2.4 Implement target-window screenshot capture with `PrintWindow` and
  fallback diagnostics.

## 3. Tests And Evidence

- [x] 3.1 Add Go tests for HTTP handlers, auth and request validation.
- [x] 3.2 Add Windows-native smoke commands for version, health, type,
  screenshot and window list.
- [x] 3.3 Run `go test ./...` for the agent module and retain output.
- [x] 3.4 Retain bounded Windows smoke evidence under
  `.artifacts/openspec/host-agent-go-v1/20260626-card120/`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BSL-only module edit | N/A | No BSL or 1C metadata source changes in this Go agent change. | N/A | N/A | N/A | /opt/ai-dev-suite-for-1c/bsl-mcp | Host agent is Go and does not edit BSL. | None for BSL. |
| Delivery or runtime apply | `host-agent/windows-display-agent` | Go build/test plus Windows-native smoke command transcript. | source_preflight, scenario_log | `.artifacts/openspec/host-agent-go-v1/20260626-card120/go-test.json` | required | /opt/ai-dev-suite-for-1c/qa-mcp |  | Live 1C value commit is covered by `remote-display-e2e`. |
| Managed form layout | Windows GDI screenshot and input primitives | Smoke against a visible 1C or diagnostic target window, retaining screenshot metadata. | screenshot, active_window, scenario_log | `.artifacts/openspec/host-agent-go-v1/20260626-card120/windows-agent-smoke.md` | required | /opt/ai-dev-suite-for-1c/qa-mcp |  | Window/session policy can block input on unattended hosts. |
