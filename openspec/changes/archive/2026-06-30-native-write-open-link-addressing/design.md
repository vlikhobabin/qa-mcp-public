## Context

The read path already has a fixture-free nav-link route: it bootstraps a TestClient, window-lists the desktop, navigates to `open_link`, resolves `SecondaryFrame[S].ManagedForm[F]`, and points value reads at that form. The write path has reusable field retargeting and a `NativeWriteSession`, but its setup prefix still comes from an input capture that opens the fixture form.

## Goals / Non-Goals

**Goals:**
- Add a write-session setup mode that opens a target form by `open_link` before writes.
- Preserve the existing `NativeWriteSession.write(value, field=...)` field retargeting contract.
- Return enough metadata to prove which form was opened and which field was addressed.
- Keep offline tests independent from a live 1C runtime.

**Non-Goals:**
- Do not redesign the binary write block format.
- Do not add business-data mutation outside explicit write tool calls.
- Do not commit raw captures or local runtime logs.

## Decisions

- Reuse the existing fixture-free navigation/foreground machinery rather than adding a second nav-link implementation. The write session should share the same normalization and resolve semantics as `read_form_descriptor(open_link=...)`.
- Keep `open_link` optional. Existing fixture-backed tools and tests remain the compatibility baseline.
- Make open-link setup explicit in result payloads. Callers need to distinguish a write against a fixture form from a write against a target create/edit form.
- Treat live proof as a runtime evidence gate, not as a unit-test substitute. Offline tests should validate routing, parameter shape and safe fail-closed behavior.

## Risks / Trade-offs

- Open-link navigation can leave tabs/forms open -> mitigate with the existing clean-state sweep or held-session cleanup where applicable.
- A field may be visible in the descriptor but not writable by the pure protocol write block -> return a field-level blocked result instead of silently succeeding.
- Config-specific form layout differences can affect path/group retargeting -> keep live descriptor evidence and field name in the result.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | Native write session opening arbitrary managed forms through `open_link` | Live scenario: open a catalog create/edit form by nav-link and write a string field | `provider_gap`, `source_preflight`, `screenshot`, `cleanup_evidence` | `.artifacts/openspec/native-write-open-link-addressing/20260630-0708-do/live-gap-summary.json` | blocked | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | demo10413 rejected the ownerless subordinate-catalog create URL; callers need explicit owner/open_link context before live targeting. |
| Delivery/runtime apply | MCP tool surface change for write helpers | Offline tests plus Linux runtime preflight before live probe | `source_preflight`, `scenario_log` | `.artifacts/openspec/native-write-open-link-addressing/20260630-0708-do/matrix-preflight.json, .artifacts/openspec/native-write-open-link-addressing/20260630-0708-do/live-gap-summary.json, .artifacts/openspec/native-write-open-link-addressing/20260630-0708-do/matrix-archive-gate.json` | provided | `/opt/ai-dev-suite-for-1c/qa-mcp` |  | Runtime proof is limited to preflight and blocked-gap evidence for the subordinate create target. |
| BSL-only module edit | N/A | N/A | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/bsl-mcp` | Python protocol manager change only; no BSL source is edited. | No BSL diagnostics expected for this change. |

## Migration Plan

1. Add optional `open_link` parameters and keep old defaults.
2. Verify existing fixture-backed tests.
3. Run live proof only after Linux runtime preflight succeeds.
4. If live proof fails due to lab availability, retain the provider/runtime gap and do not claim runtime acceptance.
