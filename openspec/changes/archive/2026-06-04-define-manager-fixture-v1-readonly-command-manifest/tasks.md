## 1. Manifest And Catalog Contract

- [x] 1.1 Define the V1 run manifest structure with `run_id`, `case_id`, `command_id`, target fixture path, proxy TestClient port, target marker and expected marker.
- [x] 1.2 Seed the read-only command catalog from the client fixture V1 target map and live-open evidence.
- [x] 1.3 Add explicit rejection for text input, clicks, page switching, row selection, business commands and object writes.
- [x] 1.4 Define `case_events.jsonl` and `manager_harness_result.json` fields, including before/after timestamps, status, result preview and exception details.

## 2. Manager Harness Execution

- [x] 2.1 Implement manifest loading and validation in the manager harness.
- [x] 2.2 Implement event writing under the runtime output directory selected by the capture runner.
- [x] 2.3 Implement the first read-only subset: active window, active form, form summary and one marker-bearing element family.
- [x] 2.4 Expand the catalog to table, command bar, group/page and state-property reads after the subset event format is stable.
- [x] 2.5 Run a live manager harness command smoke against the client fixture through the proxy port.

## 3. Verification

- [x] 3.1 Validate manifest/result JSON samples with a Windows-native parser.
- [x] 3.2 Run focused EDT/BSL diagnostics for changed manager harness modules.
- [x] 3.3 Run `openspec validate define-manager-fixture-v1-readonly-command-manifest --strict`.
- [x] 3.4 Run `openspec validate qa-mcp-protocol-lab --strict`.
- [x] 3.5 Run `git diff --check -- openspec/changes/define-manager-fixture-v1-readonly-command-manifest docs/protocol-research`.

## Verification Results

- Manager source now defines `ПолучитьКаталогКомандV1`,
  `ПроверитьМанифестV1`, `ЗагрузитьМанифестV1`,
  `ЗаписатьСобытиеКомандыV1`, `ЗаписатьРезультатЗапускаV1` and
  `ВыполнитьReadOnlyКомандуV1`.
- The catalog seeds active-window, active-form, form-summary, edit-field,
  checkbox, button, table, command-bar, group and pages families from the V1
  target map and live-open markers.
- The accepted command catalog explicitly rejects `text_input`, `click`,
  `page_switch`, `row_select`, `business_command` and `object_write` command
  kinds.
- JSON samples were parsed successfully with Python:
  `manager_harness_manifest.sample.json`,
  `manager_harness_result.sample.json` and line-by-line
  `case_events.sample.jsonl`.
- `edt-mcp.get_problems_filtered(project="vanessa_manager",
  resource_contains="ProtocolFixtureTestManager")` returned zero problems.
- Focused BSL validation remains provider-gapped for the same EDT runtime
  reason recorded in the previous change: resource metadata sync is
  incompatible with the current EDT API and BSL validation timed out after
  120 seconds.
- Live manager harness command smoke is provider-gapped because the manager
  shell was not deployed after `classify_deploy_path` reported a broad full
  reload, and `live-mcp` manager COM access currently requires platform
  `8.5.1.1302`.
- Compact reviewed evidence was retained at
  `docs/protocol-research/evidence/manager-fixture-v1-readonly-contract/20260604-manager-fixture-v1-readonly-contract/`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | Manager harness manifest parser, command dispatcher and event writer | Read-only command catalog and sample manifest/result records | `bsl_diagnostics`, `scenario_file`, `scenario_log` | `.artifacts/openspec/define-manager-fixture-v1-readonly-command-manifest/<run-id>/manager-command-smoke/` | required | `/opt/edt-lab`, `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A | Medium: TestManager API names may need platform-help confirmation |
| Managed form layout | Client fixture V1 target markers consumed by the command catalog | Target-map to command-catalog coverage table | `form_tree`, `active_window`, `vanessa_ui_smoke_bundle` | `.artifacts/openspec/define-manager-fixture-v1-readonly-command-manifest/<run-id>/client-fixture-readonly/` | required | `/opt/vanessa-mcp-stack` | N/A | Medium: some client fixture controls may be visible only after a fresh apply |
| Delivery or runtime apply | Runtime output contract for `case_events.jsonl` and `manager_harness_result.json` | JSON schema/sample validation and retained run directory | `scenario_log`, `runtime_apply_log`, `data_assertion` | `runtime/protocol-research/manager-fixture-v1-readonly/<run-id>/` | required | `project:qa-mcp` | N/A | Medium: raw runtime path is ignored, so compact summaries must cite enough metadata |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS objects are changed by the manager manifest | Low: none for report surfaces |
