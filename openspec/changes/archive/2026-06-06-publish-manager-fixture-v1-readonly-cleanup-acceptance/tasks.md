## 1. Report Publication

- [x] 1.1 Collect classification evidence and retained replay/probe summaries.
- [x] 1.2 Regenerate the cleanup live-join report and corpus rows with all
  accepted summaries folded in.
- [x] 1.3 Verify accepted rows match `case_id`, manager frame range and
  `normalized_hash`.
- [x] 1.4 Preserve non-accepted rows with blocker reason and next route.
- [x] 1.5 Update `docs/protocol-research/status-report-2026-06-06.md`,
  `docs/protocol-research/README.md`, `docs/protocol-research/protocol-corpus-runner.md`
  or successor docs as needed.
- [x] 1.6 Update `docs/protocol-research/evidence-index.md` with new
  classification, probe and report evidence paths.

## 2. Verification

- [x] 2.1 Run focused tests for reporter changes, if any.
- [x] 2.2 Run JSON parse checks for regenerated reviewed evidence.
- [x] 2.3 Run `openspec validate publish-manager-fixture-v1-readonly-cleanup-acceptance --strict`.
- [x] 2.4 Run `openspec validate --all`.
- [x] 2.5 Run `git diff --check -- openspec/changes openspec/board docs/protocol-research tools/protocol-research tests`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BSL-only module edit | 1C BSL source | N/A | N/A | N/A | N/A | `project:qa-mcp` | This change publishes report/docs only and does not edit BSL | Low: no 1C source behavior changes |
| Managed form layout | Client fixture V1 form | N/A for final reporting; linked from retained runtime evidence | N/A | N/A | N/A | `/opt/vanessa-mcp-stack` | The report consumes existing capture/probe evidence instead of inspecting UI directly | Medium: stale runtime evidence must be called out if found |
| Delivery or runtime apply | Reviewed cleanup report and protocol evidence | Reporter command over retained cleanup capture plus replay summaries | `scenario_log`, `data_assertion` | `docs/protocol-research/evidence/manager-fixture-v1-live-join/20260606-live-fixture-ci-bootstrap-full-readonly-cleanup/` | required | `project:qa-mcp` | N/A | Medium: missing replay summaries leave rows pending |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |
