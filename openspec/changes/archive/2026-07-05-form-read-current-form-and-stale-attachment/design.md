## Context

The open-link path is the reliable fixture-free route for managed form reads:
it opens the target form, captures live session identifiers, and then performs
the descriptor/table read. Without `open_link`, the current implementation can
reach a template render that lacks a live ManagedForm GUID and returns a
low-level error. Separately, the attachment registry can remember an endpoint
after the process behind it is dead.

## Goals / Non-Goals

**Goals:**

- Fail before template rendering when `read_form_descriptor` or
  `read_table_cell` cannot infer a live form GUID and no `open_link` is present.
- Make stale attachment state (`attached=true`, `listening=false`) unusable for
  endpoint-touching tools and include an action hint.
- Keep explicit `host`/`port` overrides working for callers that intentionally
  bypass the attachment.

**Non-Goals:**

- Do not implement a new current-form ManagedForm GUID discovery protocol in
  this change.
- Do not run UI actions or business-data mutations.
- Do not change list-grid table resolution; that is a separate P1 card.

## Decisions

- **Choose explicit diagnostics over implicit current-form inference.** Current
  form GUID discovery is not yet a proven capture-free primitive. The safe
  behavior for this card is a structured `open-link-required` style result with
  a concrete action hint.
- **Gate stale attachments centrally.** Endpoint resolution should reject a
  recorded attachment when its liveness probe says the endpoint is not
  listening, so all wrapped endpoint tools benefit consistently.
- **Keep wrapper errors structured.** The MCP boundary should return normal tool
  result dictionaries, not raw Python exceptions, for both stale attachment and
  missing `open_link` cases.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient UI automation | `read_form_descriptor`/`read_table_cell` wrapper diagnostics without `open_link` | Offline pytest with monkeypatched protocol path and no live 1C process | Pytest output and retained summary | `.artifacts/openspec/form-read-current-form-and-stale-attachment/<run-id>/form-read-wrapper-diagnostics.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| QA/TestClient UI automation | Stale attached endpoint with `listening=false` | Offline pytest for attachment liveness rejection and action hint | Pytest output and retained summary | `.artifacts/openspec/form-read-current-form-and-stale-attachment/<run-id>/stale-attachment.md` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| Managed form layout | Real Windows/BSP current-form read smoke | Read-only `read_form_descriptor(open_link=...)` and no-`open_link` diagnostic transcript against an operator-owned Windows host | QA/TestClient transcript or MCP tool output bundle | `.artifacts/openspec/form-read-current-form-and-stale-attachment/<run-id>/windows-form-read-smoke.md` | N/A | `/opt/ai-dev-suite-for-1c/qa-mcp` | No attached Windows host, GUI desktop, PowerShell runtime, or licensed 1C TestClient is available inside this Linux workspace. | First Windows model-B validation must confirm the diagnostic text against a real form. |

## Risks / Trade-offs

- **No implicit current-form read is added.** This is intentional: a clear
  failure is safer than inventing an unverified GUID source.
- **Liveness probing can add a small delay.** Keep the probe bounded and reuse
  existing status/attach helpers.
