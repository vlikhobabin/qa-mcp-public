## 1. Evidence Summary Contract

- [x] 1.1 Define the compact manager V1 evidence summary fields for run id, command catalog version, bootstrap status, output files and command counts.
- [x] 1.2 Define frame-join status fields for each case, including chunk/frame range when known and unresolved reason when not known.
- [x] 1.3 Add or update a helper/reporting path that converts runtime outputs into reviewed Markdown and optional JSON.
- [x] 1.4 Ensure summaries link ignored runtime paths without copying raw TCP streams, full event logs, platform logs or replay output.

## 2. Publication

- [x] 2.1 Generate a reviewed manager V1 evidence summary from the first live or retained run.
- [x] 2.2 Update `docs/protocol-research/evidence-index.md` with the reviewed manager V1 evidence entry.
- [x] 2.3 Update related protocol research docs only where they need the new manager V1 evidence link.
- [x] 2.4 Record unresolved frame-join gaps with owner route and residual risk.
- [x] 2.5 Keep accepted mapping publication out of this change unless frame ranges, normalized hashes, dynamic fields and replay/probe status are already present.

## 3. Verification

- [x] 3.1 Validate generated JSON summaries with a Windows-native parser.
- [x] 3.2 Run documentation/link checks available in the project.
- [x] 3.3 Run `openspec validate publish-manager-fixture-v1-evidence-reporting --strict`.
- [x] 3.4 Run `openspec validate qa-mcp-protocol-lab --strict`.
- [x] 3.5 Run `git diff --check -- openspec/changes/publish-manager-fixture-v1-evidence-reporting docs/protocol-research`.

## Verification Results

- Reporter command passed:
  `python tools\protocol-research\report_manager_fixture_v1.py --run-dir runtime\protocol-research\captures\opsx-manager-fixture-v1-dryrun --output-dir docs\protocol-research\evidence\manager-fixture-v1\opsx-manager-fixture-v1-dryrun`.
- `python -m py_compile tools\protocol-research\report_manager_fixture_v1.py`
  passed.
- Windows-native JSON parser assertions passed for `runtime_summary.json` and
  `frame_join_report.json`.
- Path/link existence checks passed for the generated manager V1 Markdown and
  JSON reports, `docs/protocol-research/evidence-index.md` and
  `docs/protocol-research/README.md`.
- The retained report records one unresolved dry-run event, five blocked
  command cases and no accepted protocol mappings.
- `openspec validate publish-manager-fixture-v1-evidence-reporting --strict`
  passed.
- `openspec validate qa-mcp-protocol-lab --strict` passed.
- `git diff --check -- openspec/changes/publish-manager-fixture-v1-evidence-reporting docs/protocol-research tools/protocol-research/report_manager_fixture_v1.py`
  passed with CRLF conversion warnings only.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Live read proof | Manager V1 read-only run used as corpus input | Reviewed run summary and command result table | `scenario_log`, `live_read_proof`, compact evidence summary | `docs/protocol-research/evidence/manager-fixture-v1/opsx-manager-fixture-v1-dryrun/runtime_summary.md` | provider-gap recorded | `project:qa-mcp`, `/opt/vanessa-mcp-stack` | Retained run is dry-run evidence because live TestManager startup is blocked by the missing configured Vanessa EPF | Medium: first live run may have partial command coverage |
| Delivery or runtime apply | Evidence publication from ignored runtime outputs | Report generation command and validation output | `data_assertion`, `scenario_log`, docs validation | `docs/protocol-research/evidence/manager-fixture-v1/opsx-manager-fixture-v1-dryrun/runtime_summary.json` | verified | `project:qa-mcp` | N/A | Low: reviewed summary is generated and JSON-validated from the retained runtime dry-run |
| Protocol evidence | Frame-join report linking manager events to proxy chunks | Per-case join status with unresolved reasons | frame/chunk range report, normalized status when available | `docs/protocol-research/evidence/manager-fixture-v1/opsx-manager-fixture-v1-dryrun/frame_join_report.md` | verified with unresolved gaps | `project:qa-mcp` | N/A | Medium: no accepted mappings are published because the dry-run has no proxy chunk/frame evidence |
| Form module or command | New 1C command execution behavior | N/A | N/A | N/A | N/A | `/opt/edt-lab` | This change publishes evidence only; manager command behavior is implemented by earlier changes | Low: publication can reveal upstream command gaps but does not mutate behavior |
