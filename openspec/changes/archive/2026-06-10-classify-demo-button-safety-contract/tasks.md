## 1. Safety Classification

- [x] 1.1 Read the target-selection summary from
  `select-demo-safe-button-target`.
- [x] 1.2 Review the selected button command semantics through read-only
  runtime, Vanessa, metadata or EDT context.
- [x] 1.3 Produce a complete safe-action manifest row or a fail-closed
  classification decision.
- [x] 1.4 Route business mutation, unsupported or rollback-needed behavior to
  V3 or later mutation/recovery work.

## 2. Verification

- [x] 2.1 Retain classification evidence under
  `.artifacts/openspec/classify-demo-button-safety-contract/<run-id>/classification/`.
- [x] 2.2 Run `bin\openspec.cmd validate classify-demo-button-safety-contract --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/classify-demo-button-safety-contract openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | Selected demo button command or handler | Safety classification and complete manifest row or V3 routing decision | Command semantic review; manifest validation summary; rejected-row reason when unsafe | `.artifacts/openspec/classify-demo-button-safety-contract/<run-id>/classification/` | required | `project:qa-mcp`, `vanessa-mcp`, `meta-mcp`, `edt-mcp` | N/A | High until command side effects are reviewed |
| Managed form layout | Selected demo form and element path | Target marker, enabled/visible state and expected transient post-state | Form tree or metadata evidence linked from selection and classification | `.artifacts/openspec/classify-demo-button-safety-contract/<run-id>/classification/form-context.md` | required | `project:qa-mcp`, `vanessa-mcp`, `meta-mcp` | N/A | Medium: runtime state can drift between classification and capture |
| Delivery or runtime apply | Live click execution | N/A for this classification-only change | N/A | N/A | N/A | `project:qa-mcp` | This change must not execute the selected button | Low: guarded capture owns live execution |
