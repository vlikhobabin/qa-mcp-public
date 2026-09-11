## 1. Join And Corpus Tooling

- [x] 1.1 Extend `protocol_corpus_runner.py` to accept
  `manager-fixture-v1-readonly` as a capture scenario.
- [x] 1.2 Add manager fixture V1 runtime input loading for manifest, result,
  case events and proxy traffic.
- [x] 1.3 Add event-to-traffic join logic with precise unresolved reasons.
- [x] 1.4 Generate or update compact join reports with manager/client ranges.
- [x] 1.5 Generate corpus rows for joined commands using the existing evidence
  contract.
- [x] 1.6 Keep rows without replay/probe support non-accepted.

## 2. Verification

- [x] 2.1 Add offline tests or fixture files for joined, missing-event,
  missing-traffic and overlapping-window cases.
- [x] 2.2 Run focused pytest for corpus runner/reporting tools.
- [x] 2.3 Run the analyzer against the first live manager fixture smoke
  capture when available.
- [x] 2.4 Publish compact join/corpus evidence under
  `docs/protocol-research/evidence/manager-fixture-v1-live-join/<run-id>/`.
- [x] 2.5 Run `openspec validate join-manager-fixture-v1-case-events --strict`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BSL-only module edit | 1C BSL source | N/A | N/A | N/A | N/A | `project:qa-mcp` | This change modifies Python protocol tooling only | Low: BSL behavior is covered by harness/capture changes |
| Delivery or runtime apply | Consumed manager fixture runtime output | Analyzer run over retained live capture directory | `scenario_log`, `data_assertion`, `live_read_proof` | `docs/protocol-research/evidence/manager-fixture-v1-live-join/<run-id>/` | required | `project:qa-mcp` | N/A | Medium: live capture may be provider-gapped, leaving only offline parser tests |
| Managed form layout | UI form state during analyzed capture | N/A for analyzer code; referenced from capture evidence | N/A | N/A | N/A | `/opt/vanessa-mcp-stack` | Analyzer does not inspect UI directly | Medium: wrong form state can only be caught by linked capture evidence |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |
