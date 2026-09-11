## 1. Dynamic Range Detection

- [x] 1.1 Use repeatability comparison output to identify candidate dynamic
  byte and text ranges.
- [x] 1.2 Classify candidates by source class: binary offset, text GUID,
  UTF-16LE reference, counter, nonce, timestamp or opaque bytes.
- [x] 1.3 Mark ambiguous candidates separately from accepted replacements.

## 2. Normalizer Rules

- [x] 2.1 Add evidence-backed replacement rules for accepted dynamic ranges.
- [x] 2.2 Preserve operation-token and semantic request bytes unless evidence
  proves they are dynamic.
- [x] 2.3 Record replacement labels, locators, offsets, lengths and observed
  values in generated rows or normalizer reports.
- [x] 2.4 Add offline tests for before/after normalization behavior.

## 3. Evidence

- [x] 3.1 Generate compact normalizer evidence with before-hash and after-hash
  sets for repeated cases.
- [x] 3.2 Link normalizer evidence from `docs/protocol-research/evidence-index.md`.
- [x] 3.3 Keep raw repeated captures under ignored `runtime/protocol-research/`.

## 4. Verification

- [x] 4.1 Run `scripts\check.ps1`.
- [x] 4.2 Run `scripts\check-protocol-lab.ps1`.
- [x] 4.3 Run normalizer tests and a repeated-capture comparison that uses the
  new rules.
- [x] 4.4 Run `bin\openspec.cmd validate improve-corpus-dynamic-normalizer --strict`.
- [x] 4.5 Run `bin\openspec.cmd validate --all`.
- [x] 4.6 Run `git diff --check -- openspec/changes/improve-corpus-dynamic-normalizer tools/protocol-research docs/protocol-research tests`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Protocol normalizer logic and reviewed evidence generation | Offline test plan plus repeated-capture comparison command plan | `scripts\check.ps1`, normalizer tests, comparison report, compact normalizer evidence | `tests/`; `docs/protocol-research/evidence/normalizer/<evidence-id>/` | required | project:qa-mcp | N/A for deployment apply: local analyzer logic only | Medium: over-normalization can hide semantic protocol bytes |
| Managed form layout | Read-only form element responses used to prove normalizer behavior | Response marker comparison and replay/probe status for affected cases | Compact corpus comparison and normalizer report | `docs/protocol-research/evidence/corpus-comparison/<comparison-id>/`; `docs/protocol-research/evidence/normalizer/<evidence-id>/` | required | /opt/vanessa-mcp-stack | N/A for layout mutation: no form source is changed | Low: UI noise can create false candidate ranges |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | project:qa-mcp | No BSL source is changed | None |
| Role rights | Target users and roles | N/A | N/A | N/A | N/A | project:qa-mcp | Normalizer behavior is independent of role-specific runtime proof in this card | Low: role-specific payload differences remain out of scope |
