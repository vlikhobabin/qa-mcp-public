## 1. Capture Runner

- [x] 1.1 Update `run_protocol_capture.ps1` live
  `manager-fixture-v1-readonly` flow to prepare the manager harness manifest.
- [x] 1.2 Invoke the custom manager harness path with run id, proxy port,
  manifest path and output directory.
- [x] 1.3 Keep Vanessa MCP smoke probes as optional/bootstrap evidence rather
  than the primary corpus generator.
- [x] 1.4 Add fail-closed preflight handling for missing Vanessa EPF or manager
  runtime assets.
- [x] 1.5 Preserve owned-PID cleanup and raw-output policy.

## 2. Verification

- [x] 2.1 Run PowerShell parser validation for
  `tools/protocol-research/run_protocol_capture.ps1`.
- [x] 2.2 Run `manager-fixture-v1-readonly -DryRun` after the live-path changes
  to prove the contract still works.
- [x] 2.3 Run a non-dry-run live smoke when the required EPF/runtime profile is
  available.
- [x] 2.4 If live startup is blocked, publish a compact provider/runtime gap
  under `docs/protocol-research/evidence/manager-fixture-v1-live-capture/<run-id>/`.
- [x] 2.5 Run `openspec validate execute-manager-fixture-v1-live-capture --strict`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Windows capture lifecycle for TestClient, proxy and manager | Non-dry-run capture command and cleanup summary | `runtime_apply_log`, `scenario_log`, `data_assertion` | `.artifacts/openspec/execute-manager-fixture-v1-live-capture/<run-id>/capture-runner/` | required | `project:qa-mcp`, `/opt/vanessa-mcp-stack` | N/A | High: default Vanessa EPF is currently absent unless operator supplies it |
| Form module or command | Manager harness invocation from capture runner | Harness invocation record with manifest path and proxy port | `scenario_file`, `scenario_log` | `runtime/protocol-research/captures/<run-id>/manager_harness_invocation.json` | required | `project:qa-mcp`, `/opt/vanessa-mcp-stack` | N/A | Medium: invocation mechanism may depend on Vanessa/runtime provider behavior |
| Managed form layout | Client fixture form open during capture bootstrap | Active-window/form proof for `QA MCP Protocol Fixture V1` | `active_window`, `form_tree`, `vanessa_ui_smoke_bundle` | `.artifacts/openspec/execute-manager-fixture-v1-live-capture/<run-id>/client-fixture-open/` | required | `/opt/vanessa-mcp-stack` | N/A | Medium: screenshot may remain unavailable; form-analysis fallback is acceptable if retained |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |
