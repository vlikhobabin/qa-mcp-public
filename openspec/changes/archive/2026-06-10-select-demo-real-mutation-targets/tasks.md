## 1. Target Selection

- [x] 1.1 Inspect card-60 output, demo10413 form context and available
  read-only runtime, Vanessa, metadata or EDT evidence routes.
- [x] 1.2 Select one primary document-form mutation candidate with
  `target_id`, object/form path, element path, visible marker, operation
  family, expected mutation, recovery feasibility and residual risk.
- [x] 1.3 Select up to two low-blast-radius catalog or processing candidates
  when the target marker and recovery feasibility are reviewable.
- [x] 1.4 Record rejected, deferred or blocked candidates with reason, owner
  route and residual risk.
- [x] 1.5 Record the expected runtime route per candidate (capture-managed
  processes or attach to a running TestClient) so the guarded pilot knows which
  live runtime preflight mode applies.
- [x] 1.6 Publish the target-selection summary for
  `define-demo-mutation-manifest-contract`.

## 2. Verification

- [x] 2.1 Retain target-selection evidence under
  `.artifacts/openspec/select-demo-real-mutation-targets/<run-id>/target-selection/`.
- [x] 2.2 Run `bin\openspec.cmd validate select-demo-real-mutation-targets --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/select-demo-real-mutation-targets openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | Demo10413 forms containing selected or rejected mutation targets | Target-selection summary with observed form/window and element markers | Vanessa form tree or static metadata summary; active-window/form proof when available | `.artifacts/openspec/select-demo-real-mutation-targets/<run-id>/target-selection/` | required | `project:qa-mcp`, `vanessa-mcp`, `meta-mcp`, `edt-mcp` | N/A | Medium: target visibility can differ across disposable demo infobases |
| Form module or command | Candidate document, catalog or processing action command | Operation-family and recovery-feasibility note for each selected row | Selection summary with command caption/marker, likely owner and side-effect rationale | `.artifacts/openspec/select-demo-real-mutation-targets/<run-id>/target-selection/command-context.md` | required | `project:qa-mcp`, `vanessa-mcp`, `meta-mcp`, `edt-mcp` | N/A | High until manifest review proves recovery and allowed mutation scope |
| Delivery or runtime apply | Live mutation execution | N/A for this target-selection-only change | N/A | N/A | N/A | `project:qa-mcp` | This change performs read-only selection and must not execute the target | Low: execution is gated by later manifest and guarded-pilot changes |
