## 1. Dialog Surface Model

- [x] 1.1 Define the fixture-local V4 dialog state record and marker names for
  dialog family, lifecycle state, expected text, selected result and recovery.
- [x] 1.2 Define the V4 baseline and reset contract so the dialog marker set
  returns to the V1 baseline after every scenario.
- [x] 1.3 Classify planned warning, question and fixture-owned modal-form
  scenarios as fixture-local, mutation-like or special-recovery.

## 2. Verification

- [x] 2.1 Retain Windows-native open/reset evidence for the V4 baseline marker
  set once implementation begins.
- [x] 2.2 Run `bin\openspec.cmd validate v4-dialog-surface-model --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/v4-dialog-surface-model
  openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | V4 dialog markers and fixture-owned modal surface placeholders | Observable baseline marker set and dialog-family classification | EDT validation; Vanessa form open; form tree; active-window proof | `.artifacts/openspec/v4-dialog-surface-model/20260609-v4-designer-apply/dialog-surface/` | done | `project:qa-mcp`, `vanessa-mcp`, `/opt/edt-lab` | N/A | Low: runtime proof retained as accepted fallback evidence because screenshot bootstrap was disabled |
| Form module or command | Dialog state helpers, initialization and reset routines | Deterministic marker update and baseline restore model | BSL diagnostics; focused runtime open/reset proof | `.artifacts/openspec/v4-dialog-surface-model/20260609-v4-static-contract/bsl-reset-proof/` | done | `project:qa-mcp`, `/opt/edt-lab` | N/A | Low: Designer apply and runtime reset proof validated the helper contract |
| Delivery or runtime apply | BSL and managed form update | Spec-driven fixture state change with no business data writes | Windows-native runtime apply/open evidence and OpenSpec strict validation | `.artifacts/openspec/v4-dialog-recovery-verification/20260609-v4-designer-apply/runtime-apply/` | done | `project:qa-mcp` | N/A | Low: change is local to the fixture surface |
