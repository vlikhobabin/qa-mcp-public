## Context

The current dynamic-list read path already resolves the live table descriptor
and preserves structured display-backend refresh errors. The remaining failure
is semantic: when the replay returns zero rows after a failed refresh or sweep,
the top-level payload still resembles valid empty data. In remote-client mode
the underlying failure is often Windows host-window discovery, even though a
visible `V8TopLevelFrame*` 1C window exists on the host.

This change affects QA/TestClient UI automation behavior. It changes no raw
protocol captures and performs no business-data mutation.

## Goals / Non-Goals

**Goals:**
- Mark zero-row list reads as `ok:false` and `data_confidence:"unknown"` when
  refresh, clean-state sweep, or target-window confirmation failed.
- Keep confirmed refreshed-empty reads compatible for local/Linux and normal
  remote-client runs where display refresh and sweep succeed.
- Attach a bounded remote-client diagnostic with the searched host-agent target,
  discovered Windows 1C windows, and visible UIA cell text when the host-agent
  can provide it.
- Add offline Python and Go tests for the new result and host-agent contracts.

**Non-Goals:**
- Do not change native list replay frames, capture bundles, or table-retargeting
  semantics.
- Do not add 1C metadata, role, posting, report, migration, COM query, or OData
  behavior.
- Do not run live Windows UI automation from this Linux workspace.
- Do not expose unauthenticated host-agent desktop introspection.

## Decisions

1. **Fail loud only when zero data is uncertain.** Populated list reads and
   confirmed refreshed-empty reads keep their existing shape. When a zero-row,
   `None` value, or all-`None` row coincides with refresh/sweep/window
   uncertainty, the result gets `ok:false`, `error:"list-read-uncertain-zero"`,
   `data_confidence:"unknown"`, the existing human `reason`, and a structured
   `underlying_error`.

2. **Reuse the list freshness metadata.** `_ensure_list_fresh` already records
   `refresh_error`, `sweep_error`, `refresh_method`, and poll state. A small MCP
   helper will interpret that metadata for `read_list_grid`, `read_list_column`,
   and `read_list_row` instead of duplicating checks in each tool.

3. **Make remote window discovery diagnostic-only.** The Python side will ask the
   remote display backend for host windows and visible cells only when an
   uncertain zero-row result is about to be returned. Diagnostic failure is
   recorded as a provider/runtime gap inside the payload; it does not mask the
   original list-read failure.

4. **Extend the authenticated host-agent surface narrowly.** `WindowInfo` will
   include `class`, `/window_list` will therefore expose `V8TopLevelFrame*`
   class names, and a new authenticated visible-cell endpoint will return a
   bounded list of UI Automation names under the resolved 1C top-level window.
   The endpoint runs a fixed host-side UIA probe, not arbitrary caller-supplied
   code.

5. **Capture source and replay strategy remain unchanged.** The list read still
   uses the existing capture-derived replay templates. The new behavior changes
   result classification and diagnostics only.

## Risks / Trade-offs

- [Risk] Some callers may not expect `ok:false` together with `row_count:0`.
  Mitigation: retain existing `row_count`, `rows`, `list_refresh`, and `reason`
  fields while adding explicit failure/confidence fields.
- [Risk] Host UIA output can contain business data. Mitigation: bound the cell
  count and retain it only in authenticated tool responses or local ignored
  evidence; do not commit screenshots or customer data.
- [Risk] PowerShell/UIA may be unavailable on some Windows hosts. Mitigation:
  report a structured diagnostic gap and still fail loud instead of fabricating
  empty data.
- [Risk] Offline tests cannot prove the [redacted third-party configuration] live case. Mitigation: record
  a runtime gap for this Linux workspace and require a retained Windows smoke on
  the next operator-owned Windows run.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | `read_list_grid`, `read_list_column`, `read_list_row` uncertain zero-row classification in `src/qa_mcp/mcp_server.py` | Focused Python unit tests with fake refresh/window failures and successful confirmed-empty reads | Focused pytest output and retained verification summary | `.artifacts/openspec/read-list-grid-fail-loud-and-remote-window-discovery/<run-id>/python-list-read-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | Windows host-agent `/window_list` class metadata and visible-cell diagnostic endpoint | Go unit tests with fake driver window/cell results; Windows build compile check | Go test output and retained verification summary | `.artifacts/openspec/read-list-grid-fail-loud-and-remote-window-discovery/<run-id>/host-agent-tests.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | Real Windows [redacted third-party configuration] `Справочник.Валюты` remote-client read | Operator-owned Windows MCP transcript showing populated rows or top-level `ok:false` with window/cell diagnostics | Retained sanitized MCP transcript and optional screenshot/UIA summary | `.artifacts/openspec/read-list-grid-fail-loud-and-remote-window-discovery/<run-id>/windows-third-party-config-read-list-grid.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows GUI desktop, Docker Desktop host-agent route, licensed [redacted third-party configuration] infobase, or operator approval is available inside this Linux workspace. | The first Windows package/customer-support run must retain the transcript before claiming live [redacted third-party configuration] proof. |
