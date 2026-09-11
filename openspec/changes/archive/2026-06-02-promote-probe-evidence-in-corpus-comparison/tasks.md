## 1. Probe Evidence Integration

- [x] 1.1 Add a compact probe-evidence input or mapping path for corpus rows
  and comparison runs.
- [x] 1.2 Attach accepted probe/replay status only when case identity,
  operation shape and expected response markers match.
- [x] 1.3 Preserve explicit unresolved reasons for ambiguous or incomplete
  probe joins.

## 2. Comparison Classification

- [x] 2.1 Promote repeated stable rows to stable accepted only when the row has
  accepted probe/replay evidence.
- [x] 2.2 Keep unsupported fixture gaps and incomplete-hash rows out of
  accepted mappings.
- [x] 2.3 Report accepted case ids, probe evidence paths and unresolved rows in
  comparison output.

## 3. Tests And Evidence

- [x] 3.1 Add focused tests for accepted, pending, incomplete, unsupported and
  ambiguous probe-join classifications.
- [x] 3.2 Regenerate or add compact evidence for the first accepted read-only
  mappings using captures `20260602-193802` and `20260602-195407`.
- [x] 3.3 Update `docs/protocol-research/evidence-index.md` with the new
  accepted-mapping or comparison evidence.
- [x] 3.4 Keep raw regenerated capture/probe output under ignored
  `runtime/protocol-research/`.

## 4. Verification

- [x] 4.1 Run `scripts\check.ps1`.
- [x] 4.2 Run `scripts\check-protocol-lab.ps1`.
- [x] 4.3 Run focused corpus comparison/probe-status tests.
- [x] 4.4 Run repeatability comparison over `20260602-193802` and
  `20260602-195407` with probe evidence attached.
- [x] 4.5 Run `bin\openspec.cmd validate promote-probe-evidence-in-corpus-comparison --strict`.
- [x] 4.6 Run `bin\openspec.cmd validate --all`.
- [x] 4.7 Run `git diff --check -- openspec/changes/promote-probe-evidence-in-corpus-comparison tools/protocol-research docs/protocol-research tests`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Corpus runner/comparison tooling and reviewed evidence generation | Offline tests plus repeatability comparison command plan | `scripts\check.ps1`, focused tests, comparison report, accepted-mapping evidence | `tests/`; `docs/protocol-research/evidence/corpus-comparison/<comparison-id>/`; `docs/protocol-research/evidence/accepted-mappings/<evidence-id>/` | required | project:qa-mcp | N/A for deployment apply: local analyzer/tooling only | Medium: stale probe evidence could falsely promote a mapping |
| Managed form layout | Read-only active-window, active-form and form-element evidence from TestClient UI | Existing capture/probe evidence reuse or fresh retained probe run if regeneration is needed | Compact corpus evidence, direct Python-manager probe evidence, optional fresh run summary | `docs/protocol-research/evidence/corpus/20260602-193802-expanded-readonly/`; `docs/protocol-research/evidence/corpus/20260602-195407-expanded-readonly/`; `docs/protocol-research/evidence/python-manager-probe/expanded-20260602-193802/` | required | /opt/vanessa-mcp-stack | N/A for form mutation: read-only evidence only | Low: fixture still lacks non-EditField families |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | project:qa-mcp | No BSL source is changed | None |
| Metadata object | 1C metadata and EDT workspace | N/A | N/A | N/A | N/A | /opt/edt-lab | No metadata source or EDT workspace is changed | None |
| Role rights | Target users and roles | N/A | N/A | N/A | N/A | project:qa-mcp | Read-only protocol comparison is not role-rights behavior in this card | Low: future role-specific protocol differences remain out of scope |
