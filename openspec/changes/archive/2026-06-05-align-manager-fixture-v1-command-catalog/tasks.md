## 1. Catalog Alignment

- [x] 1.1 Define the reviewed V1 command catalog fields and source of truth.
- [x] 1.2 Align PowerShell `New-ManagerFixtureV1Manifest` output with the
  reviewed catalog.
- [x] 1.3 Align the BSL `ПолучитьКаталогКомандV1` command ids, kinds and
  markers with the reviewed catalog.
- [x] 1.4 Add or document a first-smoke subset containing two or three
  read-only commands.
- [x] 1.5 Keep rejected action and mutation command kinds visible in the
  catalog policy.

## 2. Verification

- [x] 2.1 Parse the generated/catalog JSON or equivalent reviewed catalog
  source with a Windows-native parser.
- [x] 2.2 Add an offline comparison check between the PowerShell manifest and
  BSL catalog evidence where feasible.
- [x] 2.3 Update compact catalog evidence under
  `docs/protocol-research/evidence/manager-fixture-v1-command-catalog/<run-id>/`.
- [x] 2.4 Run `openspec validate align-manager-fixture-v1-command-catalog --strict`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | Manager harness V1 command catalog | Catalog comparison between BSL and tooling command ids | `bsl_diagnostics`, `edt_validation_report`, `data_assertion` | `.artifacts/openspec/align-manager-fixture-v1-command-catalog/<run-id>/catalog-check/` | required | `/opt/edt-lab`, `project:qa-mcp` | N/A | Medium: BSL parsing may need a source-aware helper if EDT diagnostics are unavailable |
| Delivery or runtime apply | Runtime live capture | N/A | N/A | N/A | N/A | `project:qa-mcp` | This change aligns catalog inputs only; live apply is covered by the capture change | Medium: runtime drift is still possible until the live smoke runs |
| Managed form layout | Client fixture form elements referenced by catalog targets | Target-map link review | `form_tree` or reviewed live-open evidence link | `docs/protocol-research/evidence/fixture-runtime/20260604-client-fixture-v1-live-open/` | required | `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A | Medium: fixture markers may change in later client fixture versions |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |
