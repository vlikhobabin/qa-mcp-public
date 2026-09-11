## 1. Scenario Handlers

- [x] 1.1 Add fixture-local warning and question handlers with deterministic
  text markers and selected-result markers.
- [x] 1.2 Add fixture-owned modal form open/close handlers with lifecycle and
  result markers.
- [x] 1.3 Add expected-error handlers with controlled diagnostic markers that
  cannot be confused with infrastructure failures.
- [x] 1.4 Add bounded wait/progress handlers with fixed maximum duration,
  observable progress, cancel/retry and completion markers.

## 2. Verification

- [x] 2.1 Retain Windows-native UI evidence for each V4 scenario family under
  `.artifacts/openspec/v4-bounded-wait-error-scenarios/<run-id>/`.
- [x] 2.2 Run `bin\openspec.cmd validate v4-bounded-wait-error-scenarios
  --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/v4-bounded-wait-error-
  scenarios openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | Warning, question, modal and wait/progress controls or fixture-owned modal form | Scenario-visible controls, modal lifecycle markers and text markers | EDT validation; Vanessa form open; form tree; active-window proof; screenshot or fallback UI evidence | `.artifacts/openspec/v4-bounded-wait-error-scenarios/20260609-v4-designer-apply/ui-surface/` | done | `project:qa-mcp`, `vanessa-mcp`, `/opt/edt-lab` | N/A | Low: fallback UI evidence retained for every V4 action family |
| Form module or command | Warning/question/modal/error/wait handlers | Deterministic scenario dispatch, controlled diagnostics and bounded wait behavior | BSL diagnostics; Vanessa scenario log; active-form evidence; controlled error log | `.artifacts/openspec/v4-bounded-wait-error-scenarios/20260609-v4-static-contract/handler-proof/` | done | `project:qa-mcp`, `vanessa-mcp`, `/opt/edt-lab` | N/A | Low: expected-error diagnostic marker and runtime token validation are retained |
| Delivery or runtime apply | Fixture form and module update | Windows-native apply/open/run smoke with no business data writes | Runtime apply log or retained operator proof; OpenSpec strict validation | `.artifacts/openspec/v4-dialog-recovery-verification/20260609-v4-designer-apply/runtime-apply/` | done | `project:qa-mcp` | N/A | Low: scenarios remain fixture-local and bounded |
