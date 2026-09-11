## 1. Evidence Contract

- [x] 1.1 Update `docs/protocol-research/corpus-evidence-contract.md` with
  direct-probe evidence link fields and accepted mapping rules.
- [x] 1.2 Update `docs/protocol-research/protocol-corpus-runner.md` to explain
  how direct-probe evidence participates in accepted read-only mappings.
- [x] 1.3 Record how unresolved direct-probe request-frame gaps should be
  represented.

## 2. Spec Sync

- [x] 2.1 Sync the new direct-probe acceptance requirements into
  `openspec/specs/qa-mcp-protocol-lab/spec.md`.
- [x] 2.2 Keep unsupported fixture gaps and incomplete hashes as visible
  non-accepted states.

## 3. Verification

- [x] 3.1 Run `scripts\check.ps1`.
- [x] 3.2 Run `scripts\check-protocol-lab.ps1`.
- [x] 3.3 Run `bin\openspec.cmd validate define-corpus-probe-acceptance-contract --strict`.
- [x] 3.4 Run `bin\openspec.cmd validate --all`.
- [x] 3.5 Run `git diff --check -- openspec/changes/define-corpus-probe-acceptance-contract docs/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Protocol evidence contract and accepted-mapping requirements | Offline documentation/spec validation plan | OpenSpec validation, static checks, reviewed docs diff | `docs/protocol-research/corpus-evidence-contract.md`; `openspec/specs/qa-mcp-protocol-lab/spec.md` | required | project:qa-mcp | N/A for runtime deployment: contract/docs only | Low: wording could over-constrain future probe formats |
| Managed form layout | Read-only form/window/element evidence referenced by the contract | Evidence-link policy for existing captures and direct probe outputs | Existing compact corpus/probe evidence paths referenced in docs | `docs/protocol-research/evidence/corpus/`; `docs/protocol-research/evidence/python-manager-probe/` | required | /opt/vanessa-mcp-stack | N/A for form mutation: no 1C form source changes | Low: current fixture still lacks several element families |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | project:qa-mcp | No BSL source is changed | None |
| Metadata object | 1C metadata and EDT workspace | N/A | N/A | N/A | N/A | /opt/edt-lab | No metadata object is changed | None |
| Role rights | Target users and roles | N/A | N/A | N/A | N/A | project:qa-mcp | Read-only evidence contract is role-independent in this change | Low: future role-specific payload differences remain out of scope |
