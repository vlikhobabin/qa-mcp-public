## Context

The Python list-read refresh helpers call the display backend to send `F5` and
`Escape` before and between cold list reads. Today `_force_list_refresh` and
`_cold_state_sweep` catch all exceptions and reduce them to generic text such
as "no display backend reachable". That hides the difference between an
unconfigured host-agent, an unsupported key, a version mismatch, and a Windows
foreground-lock denial.

This change affects Python manager/MCP behavior and QA/TestClient UI
automation diagnostics. It does not change protocol replay frames, list table
resolution, model-A X11 behavior, host-agent authentication, or COM behavior.

## Goals / Non-Goals

**Goals:**
- Preserve structured `DisplayBackendError` codes and details in refresh and
  clean-state metadata.
- Make zero-row list diagnostics name actionable host-agent causes such as
  `foreground-denied`.
- Keep refresh and sweep best-effort: list reads should not raise solely
  because display refresh failed.
- Add offline tests for diagnostic propagation and retained Windows E2E
  evidence expectations.

**Non-Goals:**
- Do not change the native list replay algorithm or descriptor-table
  resolution behavior.
- Do not execute live Windows UI automation from this Linux workspace.
- Do not route business-data mutations, text input, posting, import/export, or
  COM operations through this change.

## Decisions

1. **Return structured display notes from helper functions.** `_force_list_refresh`
   will continue returning `(method, note)`, but the note will be derived from
   `DisplayBackendError.to_result(...)` when available. `_cold_state_sweep` can
   preserve the latest sweep failure in poll metadata without raising.

2. **Keep MCP result compatibility.** Existing callers already consume
   `refresh_method`, `refresh_note`, and zero-row `reason`. The change will add
   explicit fields such as `refresh_error` or structured note content rather
   than replacing the result shape wholesale.

3. **Distinguish backend reachability from primitive failure.** Generic text is
   reserved for actual backend construction/reachability failures. Host-agent
   JSON errors, version mismatches, unsupported keys, and `foreground-denied`
   should be surfaced by their real codes.

4. **Retain runtime evidence separately.** Offline Python tests can prove
   propagation at the MCP boundary. A Windows E2E transcript is still required
   to prove non-foreground `read_list_grid` returns rows once the host-agent
   no-focus key path is installed.

## Risks / Trade-offs

- [Risk] Adding structured fields could surprise callers that compare exact
  result dictionaries. Mitigation: preserve existing key names and append
  diagnostics rather than removing current fields.
- [Risk] Zero-row reasons can become too verbose. Mitigation: include the
  stable error code first and keep details bounded.
- [Risk] Offline tests cannot prove Windows foreground behavior. Mitigation:
  record a runtime evidence row and retained evidence path; fail closed only
  when the delivery requires that runtime proof and no operator gap is accepted.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | `read_list_grid`/`read_list_column` refresh diagnostics in `src/qa_mcp/mcp_server.py` | Python unit tests with fake display-backend errors for `foreground-denied`, unreachable agent, and unsupported key | Focused pytest output and retained verification summary | `.artifacts/openspec/read-list-refresh-diagnostics/20260706T140652Z/refresh-diagnostic-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | Real Windows model-B non-foreground dynamic-list read | Windows E2E `read_list_grid` on populated `Справочник.Валюты` with 1C window not foreground | Retained MCP transcript showing populated rows and no generic display-backend note | `.artifacts/openspec/read-list-refresh-diagnostics/20260706T140652Z/windows-nonforeground-read-list-grid.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No operator-owned Windows GUI desktop, host-agent service, or licensed 1C TestClient is available inside this Linux workspace. | The first Windows package run must retain this transcript before relying on the busy-desktop proof. |
