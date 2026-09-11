## 1. Scope Contract

- [x] 1.1 Update protocol research docs with the `safe_ui_action` safety
  class, allowed action families and excluded mutation families.
- [x] 1.2 Add a safe-action candidate matrix template with `case_id`,
  `api_call`, `ui_target`, `pre_state`, `action`, `post_state`,
  `recovery_expectation`, prerequisite status and owner route fields.
- [x] 1.3 Link controlled fixture and read-only element hash outcomes as
  explicit prerequisite gates for target selection.

## 2. Safety Review

- [x] 2.1 Mark text input, command execution with side effects, checkbox
  toggles, table edits, save/post/delete and persisted business-data mutation
  as out of scope.
- [x] 2.2 Document how unresolved read-only evidence can be deferred without
  being promoted to accepted action evidence.
- [x] 2.3 Update `docs/protocol-research/evidence-index.md` only if new
  compact policy evidence is created.

## 3. Verification

- [x] 3.1 Run `scripts\check.ps1`.
- [x] 3.2 Run `scripts\check-protocol-lab.ps1`.
- [x] 3.3 Run `bin\openspec.cmd validate define-safe-ui-action-scope --strict`.
- [x] 3.4 Run `git diff --check -- openspec/changes/define-safe-ui-action-scope docs/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | Candidate managed form elements, windows, tabs/pages and menus used as safe action targets | Safe-action candidate matrix with pre/post state and recovery expectation | Reviewed scope doc and target-selection matrix; no live capture required in this change | `docs/protocol-research/safe-ui-action-scope.md`; `.artifacts/openspec/define-safe-ui-action-scope/<run-id>/target-review.md` | required | `project:qa-mcp`, `/opt/vanessa-mcp-stack` | N/A for form source edits: this change only plans targets | Medium: current lab form may not expose all safe target families |
| Delivery or runtime apply | Protocol lab safety policy and evidence gates | Offline docs/spec update and Windows check plan | `scripts\check.ps1`, `scripts\check-protocol-lab.ps1`, OpenSpec validation | `openspec/changes/define-safe-ui-action-scope/`; `docs/protocol-research/` | required | `project:qa-mcp` | N/A for live runtime apply: no 1C process is started | Low: policy can drift if later capture ignores the gate |
| Form module or command | Business commands, write handlers, input handlers and persisted toggles | Exclusion list and mutation-card routing rule | Scope doc showing excluded actions | `docs/protocol-research/safe-ui-action-scope.md` | N/A | `/opt/vanessa-mcp-stack` | Mutating commands are explicitly out of scope for safe action planning | Medium: future mutation work still needs rollback design |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | `project:qa-mcp` | No BSL source is changed | None |
