## 1. Manifest Contract

- [x] 1.1 Define the machine-readable V2 safe-action tooling manifest fields.
- [x] 1.2 Add fail-closed validation for missing fields, unsupported families
  and `mutates_business_data` values other than `false`.
- [x] 1.3 Document how manifest rows map to fixture target maps and corpus
  evidence rows.

## 2. Verification

- [x] 2.1 Retain manifest validation examples for accepted, rejected,
  unsupported and pending rows.
- [x] 2.2 Run `bin\openspec.cmd validate define-v2-safe-action-tooling-manifest --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/define-v2-safe-action-tooling-manifest openspec/board docs/protocol-research`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Safe-action manifest validation contract | Required field checklist and fail-closed examples | Manifest validation summary; accepted/rejected sample rows; OpenSpec strict validation | `.artifacts/openspec/define-v2-safe-action-tooling-manifest/<run-id>/manifest-validation/` | required | `project:qa-mcp` | N/A for live runtime apply: this change can be verified offline | Medium: runner implementations can drift if they bypass validation |
| Delivery or runtime apply | Safe-action docs and corpus contract alignment | Docs update plan linking manifest rows to corpus fields | Diff check and reviewed docs links | `docs/protocol-research/safe-ui-action-scope.md`; `docs/protocol-research/corpus-evidence-contract.md` | required | `project:qa-mcp` | N/A | Low: docs can drift if future runner changes skip the contract |
