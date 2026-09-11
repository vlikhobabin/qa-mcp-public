## 1. Target Selection

- [x] 1.1 Inspect the demo configuration surface through read-only runtime,
  Vanessa or metadata evidence.
- [x] 1.2 Select one concrete button-like target with form path, element path,
  visible caption or marker, enabled/visible state and source evidence route.
- [x] 1.3 Record rejected or deferred demo button candidates with reason, owner
  and residual risk.
- [x] 1.4 Publish a compact target-selection summary for
  `classify-demo-button-safety-contract`.

## 2. Verification

- [x] 2.1 Retain target-selection evidence under
  `.artifacts/openspec/select-demo-safe-button-target/<run-id>/target-selection/`.
- [x] 2.2 Run `bin\openspec.cmd validate select-demo-safe-button-target --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/select-demo-safe-button-target openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | Demo configuration form that contains the candidate button | Read-only form/window and element selection record | Vanessa form tree or static metadata summary; active-window/form proof when available | `.artifacts/openspec/select-demo-safe-button-target/<run-id>/target-selection/` | required | `project:qa-mcp`, `vanessa-mcp`, `meta-mcp` | N/A | Medium: target visibility can differ across local demo infobases |
| Form module or command | Candidate button command or handler reference | Command family and owner note for later safety classification | Selection summary with caption/marker and likely command family | `.artifacts/openspec/select-demo-safe-button-target/<run-id>/target-selection/command-context.md` | required | `project:qa-mcp`, `vanessa-mcp`, `meta-mcp` | N/A | High until the downstream classification proves the command is non-mutating |
| Delivery or runtime apply | Live button execution | N/A for this selection-only change | N/A | N/A | N/A | `project:qa-mcp` | This change performs read-only target selection and must not click the target | Low: execution is gated by later changes |
