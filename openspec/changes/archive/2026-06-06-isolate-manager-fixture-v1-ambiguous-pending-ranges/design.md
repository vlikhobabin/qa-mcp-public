## Context

The broad pending rows contain useful markers but cover too much traffic to
attribute a stable operation shape:

- `tm-v1-diag-window-get-form-path`: frames `26..106`
- `tm-v1-button-inert`: frames `131..390`

The accepted gate requires a reviewed manager frame range, normalized hash and
matching replay/direct-probe proof. Broad ranges can hide unrelated background
traffic and should not be promoted without isolation.

## Goals / Non-Goals

**Goals:**

- Reduce or explain broad frame windows for the affected rows.
- Preserve isolated corpus rows or retained isolation-gap evidence.
- Feed isolated rows into replay/direct-probe validation.

**Non-Goals:**

- No marker correction by range isolation alone.
- No action/click semantics for `button-inert`; it remains read-only
  observation unless later V2 action work explicitly changes scope.

## Decisions

1. Isolate before accepting.
   A target marker inside a broad window is not sufficient proof of operation
   semantics.

2. Treat isolation failure as evidence.
   If platform timing or harness behavior prevents isolation, the row remains
   pending with a precise isolation gap.

3. Keep row-specific outputs.
   Reviewed evidence should identify the isolated case id, selected frames,
   request/response sizes and normalized hash.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Focused capture/replay for broad pending windows | Row-isolation command and reviewed range report | `scenario_log`, `data_assertion`, `cleanup_evidence` | `docs/protocol-research/evidence/manager-fixture-v1-live-join/<isolation-run-id>/` | required | `project:qa-mcp` | N/A | High: platform background traffic may remain inseparable |
| Form module or command | Manager harness command sequence and boundary events | Per-row before/after event timing and boundary waits | `scenario_file`, `scenario_log` | `runtime/protocol-research/captures/<isolation-run-id>/case_events.jsonl` | required | `project:qa-mcp` | N/A | Medium: changing waits can affect timing but should remain read-only |
| Managed form layout | Fixture form state during isolated command | Active window/form or response-marker proof for fixture route | `active_window`, `form_tree` or compact response-marker summary | `.artifacts/openspec/isolate-manager-fixture-v1-ambiguous-pending-ranges/<run-id>/ui-proof/` | required | `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A | Medium: UI provider gaps can limit independent form proof |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |

## Risks / Trade-offs

- Narrowing the range may require rerunning a focused capture, not only
  reprocessing existing evidence.
- Some operation families may inherently involve multiple background frames.
  The accepted row should then state the minimal reviewed range and retained
  residual risk.
