## 1. Evidence Inventory

- [x] 1.1 Locate every committed compact corpus, comparison, accepted-mapping
  and Python-manager probe artifact that mentions `form-element-details` or
  `typed-input-field-readonly`.
- [x] 1.2 Inspect `src/qa_mcp/protocol/` descriptors and protocol docs to
  confirm the current descriptor status for both rows.
- [x] 1.3 Record the reviewed evidence sources and current statuses in
  `docs/protocol-research/evidence/readonly-element-hash-audit/current-element-hash-gaps/audit_summary.md`.

## 2. Contract Audit

- [x] 2.1 For each row, check capture id, frame range, request size, response
  size, normalized hash, dynamic fields, operation token, response markers,
  replay status and direct Python-manager probe status.
- [x] 2.2 Classify each row using the audit taxonomy:
  `already_reviewed_hash`, `extractable_existing_capture`,
  `missing_request_frames`, `ambiguous_operation_join`,
  `unsupported_fixture_state` or `incomplete_normalizer_coverage`.
- [x] 2.3 Add a next-action recommendation for each row without changing
  descriptor acceptance status.

## 3. Documentation

- [x] 3.1 Update `docs/protocol-research/evidence-index.md` with the compact
  audit path if the audit adds new reviewed evidence.
- [x] 3.2 Keep raw capture/probe output under ignored `runtime/protocol-research/`.

## 4. Verification

- [x] 4.1 Run `bin\openspec.cmd validate audit-readonly-element-hash-evidence --strict`.
- [x] 4.2 Run `bin\openspec.cmd validate --all`.
- [x] 4.3 Run `git diff --check -- openspec\changes\audit-readonly-element-hash-evidence docs\protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Offline protocol evidence audit for two direct-probe rows | Reviewed audit report and evidence-index decision | OpenSpec validation and compact audit summary | `docs/protocol-research/evidence/readonly-element-hash-audit/current-element-hash-gaps/audit_summary.md` | required | project:qa-mcp | N/A for runtime deployment: audit is offline docs/evidence only | Low: existing evidence may not represent a fresh lab state |
| Managed form layout | Read-only form element evidence behind `form-element-details` and `typed-input-field-readonly` | Evidence-source table with frame/hash/marker availability | Existing corpus/probe evidence paths and response-marker summary | `docs/protocol-research/evidence/corpus/`; `docs/protocol-research/evidence/python-manager-probe/` | required | /opt/vanessa-mcp-stack | N/A for form mutation: no managed form source or UI action is changed | Medium: current fixture may not expose every typed input variant |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | project:qa-mcp | No BSL source is changed | None |
| Metadata object | 1C metadata and EDT workspace | N/A | N/A | N/A | N/A | /opt/edt-lab | No metadata object or EDT source is changed | None |
| Role rights | Target users and roles | N/A | N/A | N/A | N/A | project:qa-mcp | Evidence audit is read-only and role-independent | Low: future restricted-role payload differences remain out of scope |
