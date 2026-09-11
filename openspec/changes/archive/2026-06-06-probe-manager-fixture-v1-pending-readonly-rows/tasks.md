## 1. Replay And Direct Probes

- [x] 1.1 Read the pending-row classification output and select probe strategy
  for each row.
- [x] 1.2 Attempt focused replay/direct probes for rows that can be validated
  safely with current tooling.
- [x] 1.3 Add narrow replay/probe support where current tooling cannot express
  a required read-only endpoint.
- [x] 1.4 Retain positive summaries with run id, case id, manager frame range,
  normalized hash, response marker and dynamic-field adaptation.
- [x] 1.5 Retain negative summaries for transport success with marker,
  endpoint, range or hash mismatches.

Implementation note: no new positive pending-row summary was produced in this
change. The retained summary has zero `accepted_probe_cases`, four current-run
negative observations and five not-attempted rows with a runtime availability
gap.

## 2. Verification

- [x] 2.1 Run focused pytest or script-level checks for any replay/probe tool
  changes.
- [x] 2.2 Run Windows-native replay/probe commands against the lab TestClient
  when runtime is available.
- [x] 2.3 Confirm raw replay output stays under ignored runtime paths and only
  compact summaries are reviewed.
- [x] 2.4 Run `openspec validate probe-manager-fixture-v1-pending-readonly-rows --strict`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BSL-only module edit | 1C BSL source | N/A | N/A | N/A | N/A | `project:qa-mcp` | This change uses protocol replay/probe tooling and does not edit BSL | Low: no 1C source behavior changes |
| Managed form layout | Client fixture V1 form during replay/probe | Existing fixture open and current cleanup evidence; optional active form proof if rerun needs it | `active_window`, `form_tree` when runtime UI evidence is needed | `.artifacts/openspec/probe-manager-fixture-v1-pending-readonly-rows/<run-id>/` | required | `/opt/vanessa-mcp-stack` | N/A | Medium: UI provider gaps can block live proof |
| Delivery or runtime apply | Windows-native replay/direct-probe run against TestClient | Replay/probe command transcript and retained compact summary | `scenario_log`, `data_assertion`, `cleanup_evidence` | `docs/protocol-research/evidence/manager-fixture-v1-replay-probe/<probe-id>/` | required | `project:qa-mcp` | N/A | High: live 1C timing or process startup can fail |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |
