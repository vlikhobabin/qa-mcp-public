## 1. Manager Target And Shell Source

- [x] 1.1 Reconfirm `validate_project_infobase_binding(target_id="manager")` before editing or applying manager source.
- [x] 1.2 Add the dedicated manager fixture processor/form/module source under `C:\1C_BASES\EDT\vanessa_qa\vanessa_manager`.
- [x] 1.3 Add explicit run context fields for `run_id`, proxy TestClient port, client fixture navigation target and output directory.
- [x] 1.4 Add a bootstrap command path that opens the client fixture form and labels its traffic as bootstrap.
- [x] 1.5 Ensure the shell contains no TCP parsing, socket handling, protocol normalization, clicks, text input, page switching or business writes.

## 2. Apply And Runtime Smoke

- [x] 2.1 Run focused EDT/BSL diagnostics for the manager fixture source.
- [x] 2.2 Apply/deploy the manager fixture shell to `C:\1C_BASES\vanessa_manager` only after binding validation succeeds.
- [x] 2.3 Run a Windows-native runtime smoke that opens the manager harness and executes bootstrap without read-only corpus commands.
- [x] 2.4 Retain raw runtime output under `runtime/protocol-research/manager-fixture-v1-shell/<run-id>/`.
- [x] 2.5 Publish compact shell readiness evidence under `docs/protocol-research/evidence/manager-fixture-v1-shell/<run-id>/`.

## 3. Verification

- [x] 3.1 Run `openspec validate add-manager-fixture-v1-runner-shell --strict`.
- [x] 3.2 Run `openspec validate qa-mcp-protocol-lab --strict`.
- [x] 3.3 Run `git diff --check -- openspec/changes/add-manager-fixture-v1-runner-shell docs/protocol-research`.
- [x] 3.4 Record any provider gaps with owner route instead of treating missing runtime proof as manual verification.

## Verification Results

- `validate_project_infobase_binding(target_id="manager", timeout_seconds=90)`
  passed with `project=vanessa_manager`, `infobase=vanessa_manager` and
  binding status `matched`.
- Source XML parse checks passed for
  `ProtocolFixtureTestManager.mdo`, `Forms/ManagerHarness/Form.form` and
  manager `Configuration.mdo`.
- Marker grep confirmed `TM_RUN_ID`, `TM_PROXY_TESTCLIENT_PORT`,
  `TM_CLIENT_FIXTURE_TARGET`, `TM_OUTPUT_DIR`,
  `TM_BOOTSTRAP_OPEN_FIXTURE`, `ProtocolFixtureTestManager`,
  `ТестируемоеПриложение`, `УстановитьСоединение` and
  `ОжидатьОтображениеОбъекта`.
- Source grep found no TCP, socket, protocol normalization, click, input,
  page-switching or business-write implementation in the shell.
- Platform help `8.3.27.1786` confirmed `ТестируемоеПриложение` constructor
  and `УстановитьСоединение` support for TestManager/TestClient connection.
- `edt-mcp.get_problems_filtered(project="vanessa_manager",
  resource_contains="ProtocolFixtureTestManager")` returned zero problems.
- Focused BSL validation was attempted through `sync_bsl_resource_meta`,
  `validate_bsl_modules` and `validate_modules`; retained provider gap:
  resource metadata sync is incompatible with the current EDT runtime and both
  validation calls timed out after 120 seconds.
- Deploy/runtime smoke was safety-deferred. `classify_deploy_path` reported a
  full configuration reload because the project baseline is not clean and the
  configuration UUID differs; broad manager infobase reload was skipped.
- `live-mcp.check_com_connection(connection_id="manager")` failed because
  active sessions require platform `8.5.1.1302`; runtime form-open smoke and
  Vanessa UI proof are recorded as provider/runtime gaps.
- Compact reviewed evidence was retained at
  `docs/protocol-research/evidence/manager-fixture-v1-shell/20260604-manager-fixture-v1-shell/source_summary.md`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Metadata object | Manager fixture processor/form in `vanessa_manager` | Target-bound EDT source plan and object registration | `edt_validation_report`, source preflight | `.artifacts/openspec/add-manager-fixture-v1-runner-shell/<run-id>/edt-validation/` | required | `/opt/edt-lab`, `project:qa-mcp` | N/A | Medium: imported manager project can drift from live infobase if deploy is skipped |
| Managed form layout | Manager harness form and run context fields | Form open smoke and expected field visibility | `vanessa_ui_smoke_bundle`, `form_tree`, `active_window` | `.artifacts/openspec/add-manager-fixture-v1-runner-shell/<run-id>/vanessa-smoke/` | required | `/opt/vanessa-mcp-stack` | N/A | Medium: screenshot capture may be unavailable; form tree fallback is acceptable |
| Form module or command | Bootstrap command path that opens client fixture | Bootstrap scenario with no corpus command execution | `bsl_diagnostics`, `scenario_log`, `active_window` | `.artifacts/openspec/add-manager-fixture-v1-runner-shell/<run-id>/bootstrap-smoke/` | required | `/opt/edt-lab`, `/opt/vanessa-mcp-stack` | N/A | Medium: client fixture must already be applied and openable |
| Delivery or runtime apply | Apply shell into `C:\1C_BASES\vanessa_manager` | Bounded deploy/apply command and generation proof | `runtime_apply_log`, binding validation summary | `.artifacts/openspec/add-manager-fixture-v1-runner-shell/<run-id>/deploy/` | required | `/opt/edt-lab`, `project:qa-mcp` | N/A | Medium: live 1C process locks can block apply and must be recorded |
