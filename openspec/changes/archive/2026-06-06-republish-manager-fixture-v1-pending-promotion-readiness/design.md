## Context

The final publication change depends on the runtime, missing-proof probe,
broad-range isolation and marker-contract changes. It should consume retained
evidence rather than inventing new protocol claims.

## Goals / Non-Goals

**Goals:**

- Regenerate the cleanup report with all retained summaries folded in.
- Publish accepted/pending counts and row-level blockers.
- State V2 readiness as unblocked, blocked, or allowed only by explicit
  residual-risk decision.

**Non-Goals:**

- No new live probing in this change unless needed only to regenerate report
  outputs from existing retained evidence.
- No acceptance gate relaxation.
- No raw capture publication.

## Decisions

1. Final readiness is evidence-derived.
   The report must link accepted rows to proof and pending rows to blockers.

2. V2 readiness is explicit.
   The docs should say whether V2 live safe-action acceptance can proceed or
   which residual risk decision is required.

3. Publication can close with pending rows.
   If rows remain pending after current-run proof attempts, the change can
   still finish by publishing precise blockers and a blocked readiness verdict.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Report regeneration from retained runtime/probe evidence | Reporter command and regenerated reviewed output paths | `scenario_log`, `data_assertion` | `docs/protocol-research/evidence/manager-fixture-v1-live-join/<final-run-id>/` | required | `project:qa-mcp` | N/A | Medium: stale summaries can produce incorrect readiness if not validated |
| Managed form layout | UI proof for final report | N/A unless final publication makes new UI claims | N/A | N/A | N/A | `project:qa-mcp` | Final publication consumes already retained UI/probe evidence and does not require new UI interaction | Low: no new UI behavior is claimed |
| BSL-only module edit | 1C BSL source | N/A unless earlier marker/catalog changes touched BSL | `bsl_diagnostics` if prior changes modified BSL | `.artifacts/openspec/republish-manager-fixture-v1-pending-promotion-readiness/<run-id>/bsl-diagnostics/` | N/A | `project:qa-mcp`, `/opt/edt-lab` | This publication change should not edit BSL directly | Low: prior changes own source diagnostics |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |

## Risks / Trade-offs

- If upstream changes leave rows pending, V2 may remain blocked. That is an
  acceptable outcome if the blockers are retained and actionable.
- Evidence paths can become confusing if multiple reruns exist. Mitigation:
  publish one final reviewed summary and link supporting runs clearly.
