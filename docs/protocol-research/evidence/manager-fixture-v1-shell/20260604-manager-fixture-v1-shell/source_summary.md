# Manager Fixture V1 Shell Source Summary

Snapshot date: 2026-06-04.

## Scope

Change: `add-manager-fixture-v1-runner-shell`.

This evidence records source-level readiness for the first manager-side
TestManager fixture shell. It does not claim a live manager deploy, TestClient
form-open smoke, frame range, normalized hash or accepted protocol mapping.

## Source Boundary

- EDT workspace: `C:\1C_BASES\EDT\vanessa_qa`.
- EDT project: `vanessa_manager`.
- Target context: `manager`.
- Infobase binding from registry: `File="C:\\1C_BASES\\vanessa_manager";`.
- Source object:
  `src/DataProcessors/ProtocolFixtureTestManager/`.

## Implemented Shell Fields

| Field or marker | Source role | Status |
| --- | --- | --- |
| `TM_RUN_ID` | run identifier supplied by capture runner | source-authored |
| `TM_PROXY_TESTCLIENT_PORT` | TestClient proxy port, default `15381` | source-authored |
| `TM_CLIENT_FIXTURE_TARGET` | client fixture navigation target | source-authored |
| `TM_OUTPUT_DIR` | selected runtime output directory | source-authored |
| `TM_BOOTSTRAP_PHASE` | labels bootstrap traffic separately | source-authored |
| `TM_BOOTSTRAP_STATUS` | command status preview | source-authored |
| `TM_BOOTSTRAP_MARKER_EXPECTED` | expected client marker, default `PF_FORM_MAIN` | source-authored |
| `TM_BOOTSTRAP_OPEN_FIXTURE` | bootstrap command hook | source-authored |

## Bootstrap Behavior

The form module creates a `ТестируемоеПриложение` using host `127.0.0.1`,
the configured proxy/TestClient port and an empty client id, then calls
`УстановитьСоединение()` and `ОжидатьОтображениеОбъекта()` for
`PF_FORM_MAIN`.

The shell does not parse TCP, open sockets, normalize frames, click controls,
enter text, switch pages or execute business commands. It only prepares a
target-bound manager harness and a labelled bootstrap path.

## Verification Notes

- `validate_project_infobase_binding(target_id="manager", timeout_seconds=90)`
  passed. The target is `vanessa_manager`, the infobase is `vanessa_manager`
  and the binding status is `matched`.
- XML parse checks passed for the new processor `.mdo`, form XML and
  `Configuration.mdo`.
- Marker grep confirmed the run context fields, bootstrap command,
  `ProtocolFixtureTestManager`, `ТестируемоеПриложение`,
  `УстановитьСоединение` and `ОжидатьОтображениеОбъекта` in source.
- Source grep found no TCP/socket/protocol parsing terms in the manager shell.
- Platform help evidence for `8.3.27.1786` confirmed the
  `ТестируемоеПриложение` constructor shape and `УстановитьСоединение`
  method.
- `edt-mcp.get_problems_filtered(project="vanessa_manager",
  resource_contains="ProtocolFixtureTestManager")` returned zero problems.
- No raw TCP capture or platform log is committed.

## Provider Gaps

```yaml
provider_gaps:
  - provider_id: edt-mcp
    owner_path: /opt/edt-lab
    matrix_row: form_module_or_command
    missing_evidence_type: focused_bsl_diagnostics
    observed_result: >
      sync_bsl_resource_meta is incompatible with the current EDT
      ResourceMetaStore.putMeta API, and validate_bsl_modules /
      validate_modules timed out after 120 seconds.
    retained_evidence: trace trc_29bc39e061924329b4d257c49f7f502f
    residual_risk: >
      Medium: source XML and project problems are clean, but focused BSL
      validation is not available in this run.
  - provider_id: edt-mcp
    owner_path: /opt/edt-lab
    matrix_row: delivery_or_runtime_apply
    missing_evidence_type: runtime_apply_log
    observed_result: >
      classify_deploy_path(mode="incremental") reported
      full_reload_configuration_publish because the project baseline is not
      clean and the configuration UUID differs. The broad manager infobase
      reload was skipped.
    retained_evidence: trace trc_29bc39e061924329b4d257c49f7f502f
    residual_risk: >
      Medium: the source shell is not applied to C:\1C_BASES\vanessa_manager
      in this change.
  - provider_id: live
    owner_path: C:\Users\historical-user\YandexDisk\Work\dev-mcp-1c\live-mcp
    matrix_row: managed_form_layout
    missing_evidence_type: runtime_smoke
    observed_result: >
      check_com_connection(connection_id="manager") failed because active
      sessions require platform 8.5.1.1302.
    retained_evidence: trace trc_29bc39e061924329b4d257c49f7f502f
    residual_risk: >
      Medium: manager harness form-open and client marker smoke are deferred
      until the manager runtime platform/profile is aligned.
  - provider_id: vanessa
    owner_path: /opt/vanessa-mcp-stack
    matrix_row: managed_form_layout
    missing_evidence_type: vanessa_ui_smoke_bundle
    observed_result: >
      Vanessa UI proof was not run because the manager shell was not deployed
      and the project profile records vanessa-mcp as an expected unproxied
      provider gap.
    retained_evidence: trace trc_29bc39e061924329b4d257c49f7f502f
    residual_risk: >
      Medium: visual form-tree/screenshot evidence remains deferred.
```
