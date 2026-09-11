## 1. Safe Handlers

- [x] 1.1 Implement allowlisted handlers for focus, activation, page
  switching, popup/menu expansion and local table-row selection.
- [x] 1.2 Connect the handlers to the shared state model so successful actions
  update `PF_LAST_ACTION`, `PF_ACTION_COUNTER`, `PF_SELECTED_PAGE`,
  `PF_SELECTED_ROW` and `PF_FOCUSED_ELEMENT`.
- [x] 1.3 Reject excluded action families before they reach any mutating
  control path.

## 2. Verification

- [x] 2.1 Record the Windows-native verification boundary for this docs-focused
  change; runtime smoke proof remains downstream.
- [x] 2.2 Run `bin\openspec.cmd validate
  add-client-fixture-v2-safe-action-form-handlers --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/add-client-fixture-v2-safe-action-form-handlers openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | Focus, activation, page, popup/menu and local row handlers | Local state updates plus fail-closed exclusions | Active-form, page and row evidence bundle | `.artifacts/openspec/add-client-fixture-v2-safe-action-form-handlers/<run-id>/handler-proof/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: handler paths may differ between platform builds |
| Runtime apply | Fixture event handlers | Spec-driven action dispatch and marker updates | Windows-native smoke proof and strict validation | `openspec/changes/add-client-fixture-v2-safe-action-form-handlers/` | required | `project:qa-mcp` | N/A | Low: changes remain fixture-local and non-mutating |
