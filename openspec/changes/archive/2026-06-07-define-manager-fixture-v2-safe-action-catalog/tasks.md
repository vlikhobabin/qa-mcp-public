## 1. Catalog Contract

- [x] 1.1 Define the manager fixture V2 safe-action catalog row shape with all
  required V2 safety fields.
- [x] 1.2 Link candidate rows to client fixture V2 target ids, target markers
  and expected result markers.
- [x] 1.3 Add fail-closed validation for missing fields, unsupported targets,
  excluded action families and `mutates_business_data` values other than
  `false`.
- [x] 1.4 Preserve unsupported or blocked rows with reason, owner and residual
  risk instead of dropping them.

## 2. Verification

- [x] 2.1 Retain an offline catalog validation sample under
  `.artifacts/openspec/define-manager-fixture-v2-safe-action-catalog/<run-id>/`.
- [x] 2.2 Run `bin\openspec.cmd validate
  define-manager-fixture-v2-safe-action-catalog --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/define-manager-fixture-v2-safe-action-catalog openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | Manager safe-action catalog consumed by harness commands | Fail-closed row contract and executable candidate subset | Offline catalog validation; BSL diagnostics when catalog is embedded in manager fixture code | `.artifacts/openspec/define-manager-fixture-v2-safe-action-catalog/<run-id>/catalog-validation/` | required | `project:qa-mcp`, `/opt/edt-lab` | N/A | Medium: catalog can drift from client fixture target markers |
| Managed form layout | Client fixture V2 target markers referenced by the catalog | Reviewed target ids and marker references | Existing target-map evidence plus targeted live form tree when implementation selects rows | `.artifacts/openspec/define-manager-fixture-v2-safe-action-catalog/<run-id>/target-review/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: selected targets may be hidden or disabled at runtime |
| Delivery or runtime apply | Catalog artifact and validation path | Windows-native offline validation before live execution | OpenSpec strict validation; manifest validation output | `openspec/changes/define-manager-fixture-v2-safe-action-catalog/` | required | `project:qa-mcp` | N/A | Low: no live action is executed by this change alone |
