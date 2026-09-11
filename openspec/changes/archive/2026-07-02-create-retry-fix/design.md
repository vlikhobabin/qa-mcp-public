# Design - Reachable create-form activation retry

## Problem

The label writer locates each label from a screenshot. On a create form, the first screenshot can race form rendering.
The code has a retry path that activates the foreground resource or sends Ctrl+Tab, but it only runs when
`foreground_method == "create_splice"`. Current production methods are `create_listreplay` for bare-create links and
`listreplay` for normal foregrounding, so the branch is dead.

## Retry contract

The implementation should make one of two explicit choices:

1. Preferred: retry for production create foreground methods. The guard should accept `create_listreplay` and any other
   current create foreground method, perform exactly one activation retry on a first-attempt miss, and populate
   `activation_retry` with `protocol_window_command` or `ctrl+tab`.
2. Alternative: remove the dead `create_splice` branch and any result metadata that implies a retry can occur.

The preferred route is expected because `_CreateForegroundHold.activate()` exists to issue a protocol activation
command. If the existing foreground resource does not expose `activate`, fallback remains Ctrl+Tab.

## Scope guard

The retry must not turn every unrelated label miss into repeated UI action. It should run only for the first locate
attempt on foreground methods that can be stale/racy. After one retry, the code must return the normal `"label not
located"` result when the label is still absent.

## Tests

Offline tests will monkeypatch screenshot capture and `locate_text` so the first attempt returns no location and the
second returns a point. The test should assert:

- the result item is targeted after retry;
- `activation_retry` is populated;
- no code path references only the dead `create_splice` method string.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| QA/TestClient managed form label write | `write_form_fields_by_label` create-form activation retry | Offline simulated first-screenshot miss with retry; card-level live write regression remains the final smoke | `source_preflight`, `qa_testclient_scenario`, `scenario_log` | `.artifacts/openspec/create-retry-fix/2026-07-02/` | required | `/opt/ai-dev-suite-for-1c/qa-mcp` |  |  |
| BSL diagnostics | no BSL files changed | N/A because this change edits Python MCP/server code only | N/A | N/A | N/A | `/opt/ai-dev-suite-for-1c/bsl-mcp` | no BSL module is modified | no BSL behavioral surface |
