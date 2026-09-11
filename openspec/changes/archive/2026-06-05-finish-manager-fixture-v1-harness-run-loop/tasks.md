## 1. Harness Runner

- [x] 1.1 Add the manifest-driven V1 run entrypoint to the manager harness.
- [x] 1.2 Load `manager_harness_manifest.json` from the runtime directory and
  validate required run and command fields.
- [x] 1.3 Open the TestClient connection through the manifest proxy port.
- [x] 1.4 Execute read-only commands in manifest order using the existing V1
  dispatcher.
- [x] 1.5 Emit before and after `case_events.jsonl` records with timestamps,
  status, target marker, expected marker, preview and exception summary.
- [x] 1.6 Write `manager_harness_result.json` with completed, failed, rejected
  and accepted-mapping counts.
- [x] 1.7 Keep action and mutation command kinds rejected before execution.

## 2. Verification

- [x] 2.1 Run XML/source parse checks for the manager harness form and module.
- [x] 2.2 Run focused EDT/BSL diagnostics for
  `ProtocolFixtureTestManager` when the provider is available.
- [x] 2.3 Run a dry-run or local parser check against sample manifest and event
  output.
- [x] 2.4 Preserve compact source/runtime evidence under
  `docs/protocol-research/evidence/manager-fixture-v1-harness-run-loop/<run-id>/`.
- [x] 2.5 Run `openspec validate finish-manager-fixture-v1-harness-run-loop --strict`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | `ProtocolFixtureTestManager.Form.ManagerHarness` run loop and command execution | Manifest-driven read-only command scenario | `bsl_diagnostics`, `scenario_file`, `scenario_log` | `.artifacts/openspec/finish-manager-fixture-v1-harness-run-loop/<run-id>/manager-harness/` | required | `/opt/edt-lab`, `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A | Medium: runtime invocation path is verified by a later capture-runner change |
| Delivery or runtime apply | Manager harness source applied to `C:\1C_BASES\vanessa_manager` when live proof is requested | Target-bound EDT apply or explicit provider gap | `runtime_apply_log`, `scenario_log` | `.artifacts/openspec/finish-manager-fixture-v1-harness-run-loop/<run-id>/runtime-apply/` | required | `/opt/edt-lab`, `project:qa-mcp` | N/A | Medium: manager deploy may still require a broad reload |
| Managed form layout | Manager harness UI layout | N/A | N/A | N/A | N/A | `project:qa-mcp` | This change affects form-module execution, not visible layout | Low: command visibility is covered by runtime smoke |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |
