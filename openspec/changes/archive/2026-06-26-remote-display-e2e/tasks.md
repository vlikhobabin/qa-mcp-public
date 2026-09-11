## 1. Preflight

- [x] 1.1 Run Linux runtime preflight before any live probe and record
  `runtime_gap` if it fails.
- [x] 1.2 Confirm host-agent `/version` and `/health` from the container.
- [x] 1.3 Confirm Windows TestClient TPort is reachable at the configured
  host/port.

## 2. Live Verification

- [x] 2.1 Run `capture_screenshot` through the remote backend and retain PNG
  metadata or sanitized screenshot evidence.
- [x] 2.2 Run `write_form_value_xtest` through the remote backend with ASCII
  and Cyrillic input and retain screenshot plus data/read-back evidence.
- [x] 2.3 Smoke `send_keys` and `get_window_list` through the remote backend.
- [x] 2.4 Smoke `write_form_fields_by_label`, `set_table_date_cell`, and
  `open_external_processor` where the lab state safely permits; otherwise
  publish blocked/deferred rows.

## 3. Evidence And Docs

- [x] 3.1 Write a compact evidence summary under
  `docs/protocol-research/evidence/card120-windows-host-agent-2026-06-26/`.
- [x] 3.2 Update `docs/protocol-research/evidence-index.md` when present.
- [x] 3.3 Update Docker/model-B docs with final host-agent verification
  commands.
- [x] 3.4 Retain matrix checker and live-run evidence under
  `.artifacts/openspec/remote-display-e2e/20260626-card120/`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Model-B remote-client display backend plus host agent readiness | Linux preflight, host-agent version/health, TestClient TPort reachability. | runtime_apply_log, scenario_log | `.artifacts/openspec/remote-display-e2e/20260626-card120/preflight-and-health.md` | required | /opt/ai-dev-suite-for-1c/qa-mcp |  | Lab availability can block live proof. |
| Managed form layout | Windows-rendered 1C client and display-bound MCP tools | Genuine input, screenshot and active-window/window-list live smoke bundle. | qa_testclient_bundle, screenshot, active_window, scenario_log, ui_data_assertion | `.artifacts/openspec/remote-display-e2e/20260626-card120/windows-e2e-bundle.md` | required | /opt/ai-dev-suite-for-1c/qa-mcp |  | Shared desktop contention can affect read-back timing. |
| BSL-only module edit | N/A | No BSL or 1C metadata source changes in this verification change. | N/A | N/A | N/A | /opt/ai-dev-suite-for-1c/bsl-mcp | Verification exercises runtime UI tools only; no BSL changes. | None for BSL. |
