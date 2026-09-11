## 1. Focused Subset Selection

- [x] 1.1 Review archived client fixture V2 target-map evidence and manager
  fixture V2 safe-action catalog outputs.
- [x] 1.2 Select one or two complete rows, preferably `switch_page` then
  `focus_element`, with every V2 safety field present.
- [x] 1.3 Record excluded, deferred or unsupported rows with reason, owner and
  residual risk.
- [x] 1.4 Publish a compact focused-subset manifest or selection summary for the
  downstream live capture change.

## 2. Verification

- [x] 2.1 Retain selection review evidence under
  `.artifacts/openspec/select-focused-v2-safe-action-subset/<run-id>/`.
- [x] 2.2 Run `bin\openspec.cmd validate select-focused-v2-safe-action-subset --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/select-focused-v2-safe-action-subset docs/protocol-research openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | Manager fixture V2 safe-action catalog rows selected for execution | Reviewed focused subset with target ids, target markers, action families and recovery expectations | Catalog selection summary; excluded-row review; OpenSpec strict validation | `.artifacts/openspec/select-focused-v2-safe-action-subset/<run-id>/selection-review/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: selected targets may be hidden or disabled at live runtime |
| Managed form layout | Client fixture V2 target markers referenced by the selected rows | Target-map cross-check for selected `PF_*` markers | Existing target-map evidence plus focused selection summary | `.artifacts/openspec/select-focused-v2-safe-action-subset/<run-id>/target-map-review/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: fixture marker drift can invalidate the selected row |
| Delivery or runtime apply | Live 1C execution | N/A for this selection-only change | N/A | N/A | N/A | `project:qa-mcp` | This change prepares reviewed input and does not execute runtime actions | Low: live runtime failure is handled by the capture change |
