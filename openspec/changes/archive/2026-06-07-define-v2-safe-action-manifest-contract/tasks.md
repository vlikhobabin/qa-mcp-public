## 1. Manifest Contract

- [x] 1.1 Update `docs/protocol-research/safe-ui-action-scope.md` with the V2
  safe-action manifest field list.
- [x] 1.2 Require `mutates_business_data=false` and
  `expected_action_result_markers` for every V2 candidate row.
- [x] 1.3 Update `docs/protocol-research/corpus-evidence-contract.md` only
  where the evidence row contract needs to reference the V2 manifest fields.

## 2. Allowlist And Exclusions

- [x] 2.1 Document the allowed first action families for V2.
- [x] 2.2 Document the excluded families and route them to later V3/V4 work.
- [x] 2.3 State that rows outside the allowlist fail closed before capture or
  manager-runner execution.

## 3. Verification

- [x] 3.1 Run `bin\openspec.cmd validate define-v2-safe-action-manifest-contract --strict`.
- [x] 3.2 Run `git diff --check -- openspec/changes/define-v2-safe-action-manifest-contract docs/protocol-research`.
- [x] 3.3 If available, run the repository documentation/static check that does
  not start 1C runtime.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | Existing element, page, table row and menu/group targets referenced by V2 manifest rows | Manifest fields for target marker, pre-state, post-state and expected action result markers | Reviewed manifest contract; no live form tree in this docs-only change | `docs/protocol-research/safe-ui-action-scope.md`; `.artifacts/openspec/define-v2-safe-action-manifest-contract/<run-id>/manifest-review.md` | required | `project:qa-mcp`, `/opt/vanessa-mcp-stack` | N/A for live UI evidence: downstream fixture/runner cards will retain it | Medium: target availability remains unproven until V2 fixture evidence exists |
| Form module or command | Excluded business command clicks, value toggles and input/write actions | Fail-closed exclusion list and routing rule to V3/V4 cards | Scope doc showing excluded families | `docs/protocol-research/safe-ui-action-scope.md` | required | `project:qa-mcp`, `/opt/vanessa-mcp-stack` | N/A for command execution: V2 must not execute business commands | Medium: future cards need rollback/recovery design before mutation work |
| Delivery or runtime apply | Evidence contract and protocol-lab safety policy | Offline docs/spec update and validation plan | OpenSpec strict validation; diff whitespace check | `openspec/changes/define-v2-safe-action-manifest-contract/`; `docs/protocol-research/` | required | `project:qa-mcp` | N/A for runtime apply: no 1C process is started | Low: policy can drift if manager runner ignores the manifest |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | `project:qa-mcp` | No BSL source is changed | None |
