## 1. Classification

- [x] 1.1 Load the current cleanup live-join report, corpus rows, runtime
  manifest and retained replay/probe summaries.
- [x] 1.2 Build a pending-row table for the nine current non-accepted rows.
- [x] 1.3 Classify each row as wrong expected marker, wrong endpoint, missing
  replay/direct-probe evidence, ambiguous frame range or retained pending.
- [x] 1.4 Record supporting fields: case id, manager/client ranges,
  normalized hash, expected marker, observed markers and prior evidence paths.
- [x] 1.5 Publish Markdown and JSON classification evidence under
  `docs/protocol-research/evidence/manager-fixture-v1-pending-readonly/<run-id>/`.

## 2. Verification

- [x] 2.1 Run JSON parse checks for the classification artifact.
- [x] 2.2 Run focused tests or script dry-runs for any new classification
  helper logic.
- [x] 2.3 Run `openspec validate classify-manager-fixture-v1-pending-readonly-rows --strict`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BSL-only module edit | 1C BSL source | N/A | N/A | N/A | N/A | `project:qa-mcp` | This change classifies retained evidence only and does not edit BSL | Low: BSL behavior is covered by existing harness evidence |
| Managed form layout | Client fixture V1 form | N/A for classification; referenced from retained cleanup evidence | N/A | N/A | N/A | `/opt/vanessa-mcp-stack` | Classification does not inspect UI directly | Medium: wrong form state must be detected from linked runtime evidence |
| Delivery or runtime apply | Retained cleanup run evidence | Offline classification over reviewed runtime artifacts | `data_assertion`, `scenario_log` | `docs/protocol-research/evidence/manager-fixture-v1-pending-readonly/<run-id>/` | required | `project:qa-mcp` | N/A | Medium: retained evidence may lack fields needed for one blocker |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |
