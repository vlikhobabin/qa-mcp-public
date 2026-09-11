## Context

Card 09 starts from cleanup run
`20260606-live-fixture-ci-bootstrap-full-readonly-cleanup`, where all 17
manager fixture V1 command windows are joined and 8 rows are accepted. The
remaining 9 rows need current-run replay or direct-probe proof. During the
previous review, 5 rows were not attempted because no fresh TestClient endpoint
was available.

## Goals / Non-Goals

**Goals:**

- Prepare a clean Windows-native TestClient endpoint for focused pending-row
  probes.
- Record endpoint readiness, selected ports, run id, fixture route, and cleanup
  ownership.
- Provide a retained runtime gap artifact when endpoint preparation cannot
  proceed.

**Non-Goals:**

- No row promotion in this change.
- No action, mutation, text input, click, page switch or table selection
  semantics.
- No unmanaged cleanup of unrelated `1cv8.exe` sessions.

## Decisions

1. Treat runtime readiness as its own evidence gate.
   Probe changes should not conflate "no endpoint" with row semantics.

2. Keep endpoint proof compact.
   Raw captures and generated logs stay under `runtime/protocol-research/`;
   reviewed summaries stay under `docs/protocol-research/evidence/`.

3. Preserve Windows-native entrypoints.
   The lab baseline is PowerShell, `.cmd`, `.bat` and Python on Windows.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Pending-row TestClient/proxy/manager startup and cleanup | Windows-native preflight/run command with selected run id and ports | `scenario_log`, `runtime_apply_log`, `cleanup_evidence` | `.artifacts/openspec/prepare-manager-fixture-v1-pending-probe-runtime/<run-id>/runtime-preflight/` | required | `project:qa-mcp` | N/A | High: local 1C startup or port ownership can block live probes |
| Managed form layout | Client fixture V1 form opened for probe readiness | Active window/form proof for the controlled fixture route | `active_window`, `form_tree` or provider gap summary | `.artifacts/openspec/prepare-manager-fixture-v1-pending-probe-runtime/<run-id>/fixture-open/` | required | `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A | Medium: UI proof may be unavailable when Vanessa/live providers are offline |
| BSL-only module edit | 1C BSL source | N/A | N/A | N/A | N/A | `project:qa-mcp` | This change prepares runtime evidence and should not edit BSL source | Low: no BSL behavior changes are planned |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |

## Risks / Trade-offs

- A clean endpoint may require operator-supplied 1C runtime assets. Mitigation:
  record an explicit provider/runtime gap and keep downstream rows pending.
- Existing local 1C processes may be running. Mitigation: only stop PIDs created
  or explicitly owned by the pending-row runtime route.
