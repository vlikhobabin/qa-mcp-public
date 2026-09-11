## 1. Publication

- [x] 1.1 Collect retained positive and negative summaries from prior changes.
- [x] 1.2 Regenerate manager fixture V1 live-join evidence with
  `report_manager_fixture_v1.py`.
- [x] 1.3 Verify accepted rows all link to proof matching case id, frame range
  and normalized hash.
- [x] 1.4 Verify pending rows all retain precise blocker and next route.
- [x] 1.5 Update `docs/protocol-research/status-report-2026-06-06.md`,
  `docs/protocol-research/README.md`,
  `docs/protocol-research/protocol-corpus-runner.md` and
  `docs/protocol-research/evidence-index.md` as needed.
- [x] 1.6 State final V2 safe-action readiness.

## 2. Verification

- [x] 2.1 Parse regenerated JSON summaries.
- [x] 2.2 Run focused reporter tests when code changed.
- [x] 2.3 Run `bin\openspec.cmd validate --all`.
- [x] 2.4 Run `git diff --check -- openspec/changes openspec/board docs/protocol-research tools/protocol-research tests`.
- [x] 2.5 Run `openspec validate republish-manager-fixture-v1-pending-promotion-readiness --strict`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Report regeneration from retained runtime/probe evidence | Reporter command and regenerated reviewed output paths | `scenario_log`, `data_assertion` | `docs/protocol-research/evidence/manager-fixture-v1-live-join/<final-run-id>/` | required | `project:qa-mcp` | N/A | Medium: stale summaries can produce incorrect readiness if not validated |
| Managed form layout | UI proof for final report | N/A unless final publication makes new UI claims | N/A | N/A | N/A | `project:qa-mcp` | Final publication consumes already retained UI/probe evidence and does not require new UI interaction | Low: no new UI behavior is claimed |
| BSL-only module edit | 1C BSL source | N/A unless earlier marker/catalog changes touched BSL | `bsl_diagnostics` if prior changes modified BSL | `.artifacts/openspec/republish-manager-fixture-v1-pending-promotion-readiness/<run-id>/bsl-diagnostics/` | N/A | `project:qa-mcp`, `/opt/edt-lab` | This publication change should not edit BSL directly | Low: prior changes own source diagnostics |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |
