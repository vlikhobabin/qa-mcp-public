## 1. Reason Taxonomy

- [x] 1.1 Add or confirm stable reason values for element hash gaps:
  `missing_request_frames`, `ambiguous_operation_join`,
  `unsupported_fixture_state`, `incomplete_normalizer_coverage`,
  `runtime_unavailable` and `accepted_reviewed_hash`.
- [x] 1.2 Ensure reason output identifies provider ownership when a gap is a
  Vanessa/TestClient harness issue rather than a qa-mcp tooling issue.

## 2. Tooling And Tests

- [x] 2.1 Update `tools/protocol-research/compare_corpus_runs.py` or related
  reporting code to emit precise reasons for the target element rows.
- [x] 2.2 Preserve existing accepted, stable, unsupported and pending
  classifications for unaffected rows.
- [x] 2.3 Add focused tests for missing frames, ambiguous joins, unsupported
  fixture state, incomplete normalizer coverage and accepted reviewed hashes.

## 3. Classification Evidence

- [x] 3.1 Run the focused comparison/classification command over the audit and
  request-hash evidence from the preceding changes.
- [x] 3.2 Retain compact output under
  `docs/protocol-research/evidence/corpus-comparison/readonly-element-hash-resolution-<comparison-id>/`.
- [x] 3.3 Update `docs/protocol-research/evidence-index.md` if new reviewed
  classification evidence is committed.

## 4. Verification

- [x] 4.1 Run focused corpus comparison/classification tests.
- [x] 4.2 Run `scripts\check.ps1`.
- [x] 4.3 Run `scripts\check-protocol-lab.ps1`.
- [x] 4.4 Run `bin\openspec.cmd validate refine-readonly-element-gap-classification --strict`.
- [x] 4.5 Run `bin\openspec.cmd validate --all`.
- [x] 4.6 Run `git diff --check -- openspec\changes\refine-readonly-element-gap-classification tools\protocol-research tests docs\protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Corpus comparison/classification tooling and compact reviewed reports | Offline test plan plus comparison command plan | Focused tests, `scripts\check.ps1`, compact classification report | `tests/`; `docs/protocol-research/evidence/corpus-comparison/readonly-element-hash-resolution-<comparison-id>/classification_summary.md` | required | project:qa-mcp | N/A for deploy/apply: local analyzer/tooling only | Medium: reason taxonomy can under-describe multi-cause gaps |
| Managed form layout | Read-only element operation evidence consumed by classification | Mapping from response markers and frame ranges to element row ids | Existing probe/corpus evidence and new classification reasons | `docs/protocol-research/evidence/readonly-element-request-hashes/<evidence-id>/`; `docs/protocol-research/evidence/python-manager-probe/<probe-id>/` | required | /opt/vanessa-mcp-stack | N/A for form mutation: classification is offline and read-only | Medium: active form fixture drift can make operation joins ambiguous |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | project:qa-mcp | No BSL source is changed | None |
| Metadata object | 1C metadata and EDT workspace | N/A | N/A | N/A | N/A | /opt/edt-lab | No metadata source is changed | None |
| Role rights | Target users and roles | N/A | N/A | N/A | N/A | project:qa-mcp | Classification is not role-rights behavior | Low: future role-specific response differences remain out of scope |
