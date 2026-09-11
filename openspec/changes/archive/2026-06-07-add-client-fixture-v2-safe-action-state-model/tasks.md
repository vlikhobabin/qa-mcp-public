## 1. State Model

- [x] 1.1 Add a fixture-local state record and marker update helpers for
  `PF_LAST_ACTION`, `PF_ACTION_COUNTER`, `PF_SELECTED_PAGE`,
  `PF_SELECTED_ROW`, `PF_FOCUSED_ELEMENT` and `PF_RESET_STATE`.
- [x] 1.2 Wire form initialization and reset so the V1 baseline is restored
  from one shared routine.

## 2. Verification

- [x] 2.1 Record the Windows-native evidence boundary for this docs-focused
  change; runtime proof remains downstream.
- [x] 2.2 Run `bin\openspec.cmd validate
  add-client-fixture-v2-safe-action-state-model --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/add-client-fixture-v2-safe-action-state-model openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | V2 fixture state markers and reset hook | Observable local marker set and baseline restore | Read-only form inspection before and after reset | `.artifacts/openspec/add-client-fixture-v2-safe-action-state-model/<run-id>/state-model/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: marker names may drift until the form module is updated |
| Runtime apply | BSL and managed form update | Spec-driven fixture state change | Windows-native open/reset evidence and OpenSpec strict validation | `openspec/changes/add-client-fixture-v2-safe-action-state-model/` | required | `project:qa-mcp` | N/A | Low: change is local to the fixture surface |
