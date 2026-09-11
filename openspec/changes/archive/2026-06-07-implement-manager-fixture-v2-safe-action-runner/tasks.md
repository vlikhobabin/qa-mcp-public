## 1. Runner Implementation

- [x] 1.1 Add a manager V2 safe-action dispatcher that consumes validated
  catalog rows and rejects incomplete or unsafe rows.
- [x] 1.2 Implement allowlisted action handlers for the first supported
  families: focus or activate existing element, activate existing window/form,
  switch fixture page, select local table row and expand/collapse safe menu or
  group targets where available.
- [x] 1.3 Record typed runner results for success, rejected, blocked,
  unsupported, partial and timeout outcomes.
- [x] 1.4 Preserve V1 read-only manager fixture behavior and keep V2 action
  execution behind the safe-action catalog.

## 2. Verification

- [x] 2.1 Retain Windows-native runner smoke evidence under
  `.artifacts/openspec/implement-manager-fixture-v2-safe-action-runner/<run-id>/`.
- [x] 2.2 Run `bin\openspec.cmd validate
  implement-manager-fixture-v2-safe-action-runner --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/implement-manager-fixture-v2-safe-action-runner openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | Manager safe-action dispatcher and action handlers | Validated command sequence for allowlisted action families | BSL diagnostics; Vanessa scenario log; manager harness result; action result markers | `.artifacts/openspec/implement-manager-fixture-v2-safe-action-runner/<run-id>/runner-smoke/` | required | `project:qa-mcp`, `vanessa-mcp`, `/opt/edt-lab` | N/A | High: action semantics are new and must fail closed |
| Managed form layout | Client fixture targets used by runner actions | Pre/post target state observations for selected rows | Form tree; active-window/active-form proof; marker reads before and after action | `.artifacts/openspec/implement-manager-fixture-v2-safe-action-runner/<run-id>/target-state/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: target visibility can differ between runs |
| Delivery or runtime apply | Manager harness update | Windows-native manager/client run with no business data mutation | Runtime apply/run log; generation/version proof; OpenSpec strict validation | `openspec/changes/implement-manager-fixture-v2-safe-action-runner/` | required | `project:qa-mcp` | N/A | Medium: local runtime setup can block live runner proof |
