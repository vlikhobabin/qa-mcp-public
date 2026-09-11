## 1. Corpus Evidence Contract

- [x] 1.1 Document the reviewed corpus case row fields and accepted value
  semantics in `docs/protocol-research/`.
- [x] 1.2 Define how dynamic field replacements, normalized hashes and
  operation tokens are represented for repeated captures.
- [x] 1.3 Document the boundary between raw runtime captures and compact
  reviewed evidence.
- [x] 1.4 Update `docs/protocol-research/evidence-index.md` with the future
  corpus evidence location.

## 2. Semantic Evidence Policy

- [x] 2.1 Document how `help-mcp`, `meta-mcp` and `edt-mcp` may enrich semantic
  labels without replacing wire evidence.
- [x] 2.2 Document the read-only first scope for `TestedApplication`,
  `TestedClientApplicationWindow`, `TestedForm` and form elements.
- [x] 2.3 Record replay/probe status rules for accepted, rejected, partial,
  timeout and unsupported mappings.

## 3. Verification

- [x] 3.1 Run `bin\openspec.cmd validate define-protocol-corpus-contract --strict`.
- [x] 3.2 Run `bin\openspec.cmd validate --all`.
- [x] 3.3 Run `git diff --check -- openspec/changes/define-protocol-corpus-contract docs/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Protocol corpus evidence contract and documentation workflow | Static docs/spec validation plan | `openspec` validation, `git diff --check`, reviewed docs diff | `openspec/changes/archive/2026-06-02-define-protocol-corpus-contract/`, `docs/protocol-research/corpus-evidence-contract.md` | provided | project:qa-mcp | N/A for live runtime apply: this change defines contract only and does not launch 1C | Low: live behavior is covered by dependent runner change |
| Managed form layout | Target 1C forms and UI controls | N/A | N/A | N/A | N/A | project:qa-mcp | No form layout, form module or metadata object is changed | None for this contract-only change |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | project:qa-mcp | No BSL source is changed | None |
