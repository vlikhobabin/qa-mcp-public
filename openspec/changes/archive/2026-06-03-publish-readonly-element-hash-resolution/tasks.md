## 1. Outcome Gate

- [x] 1.1 Read the classification output from
  `refine-readonly-element-gap-classification` and decide the per-row accepted
  or unresolved publication path.
- [x] 1.2 Verify that any accepted row has capture id, frame range,
  request/response sizes, normalized hash, dynamic fields, operation token,
  response markers and replay/probe status.
- [x] 1.3 Verify that any unresolved row has a precise reason and next
  actionable blocker.

## 2. Publication

- [x] 2.1 Generate accepted mapping evidence under
  `docs/protocol-research/evidence/accepted-mappings/readonly-element-hash-resolution-<evidence-id>/`
  when a row is accepted.
- [x] 2.2 Generate unresolved resolution evidence under
  `docs/protocol-research/evidence/readonly-element-hash-resolution/<resolution-id>/`
  for any row that remains non-accepted.
- [x] 2.3 Update `src/qa_mcp/protocol/` descriptors only for rows whose
  accepted evidence changed; otherwise preserve non-accepted descriptor status.
- [x] 2.4 Update `docs/protocol-research/evidence-index.md`,
  `docs/protocol-research/python-protocol-package.md` and
  `docs/protocol-research/protocol-corpus-runner.md` with the final outcome.

## 3. Tests

- [x] 3.1 Add or update focused descriptor tests for accepted versus
  non-accepted status on `form-element-details` and
  `typed-input-field-readonly`.
- [x] 3.2 Add a compact evidence smoke that verifies the publication report
  contains the required row fields or unresolved reasons.

## 4. Verification

- [x] 4.1 Run `scripts\check.ps1`.
- [x] 4.2 Run `scripts\check-protocol-lab.ps1`.
- [x] 4.3 Run focused descriptor/evidence tests.
- [x] 4.4 Run `bin\openspec.cmd validate publish-readonly-element-hash-resolution --strict`.
- [x] 4.5 Run `bin\openspec.cmd validate --all`.
- [x] 4.6 Run `git diff --check -- openspec\changes\publish-readonly-element-hash-resolution src docs\protocol-research tests`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Package descriptor status, docs and reviewed publication evidence | Outcome gate and descriptor/evidence test plan | `scripts\check.ps1`, focused descriptor tests, publication evidence | `src/qa_mcp/protocol/`; `docs/protocol-research/evidence/accepted-mappings/readonly-element-hash-resolution-<evidence-id>/`; `docs/protocol-research/evidence/readonly-element-hash-resolution/<resolution-id>/` | required | project:qa-mcp | N/A for deploy/apply: local package/docs publication only | Medium: mixed accepted/unresolved outcome could be misread without per-row evidence |
| Managed form layout | Read-only form element evidence being published | Per-row accepted/unresolved table with response markers and source evidence | Accepted mapping report or unresolved resolution report | `docs/protocol-research/evidence/corpus-comparison/readonly-element-hash-resolution-<comparison-id>/`; `docs/protocol-research/evidence/python-manager-probe/<probe-id>/` | required | /opt/vanessa-mcp-stack | N/A for form mutation: publication does not alter UI or metadata | Low: future fixture changes can require new evidence |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | project:qa-mcp | No BSL source is changed | None |
| Metadata object | 1C metadata and EDT workspace | N/A | N/A | N/A | N/A | /opt/edt-lab | No metadata source is changed | None |
| Role rights | Target users and roles | N/A | N/A | N/A | N/A | project:qa-mcp | Publication is not role-rights behavior | Low: role-specific payload differences remain out of scope |
