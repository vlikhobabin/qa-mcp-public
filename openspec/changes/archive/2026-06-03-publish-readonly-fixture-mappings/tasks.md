## 1. Evidence Publication

- [x] 1.1 Update `docs/protocol-research/evidence-index.md` with fixture
  source, corpus, probe, comparison/classification and accepted-mapping
  evidence directories produced by the previous changes.
- [x] 1.2 Update `docs/protocol-research/protocol-corpus-runner.md` or related
  corpus docs with the final fixture-derived status set and evidence ids.
- [x] 1.3 Update accepted-mapping docs only for fixture rows classified as
  accepted.

## 2. Unresolved Rows

- [x] 2.1 Keep every non-accepted family visible as `partial`, `pending`,
  `unsupported`, `timeout`, `rejected` or `blocked`.
- [x] 2.2 Record unresolved reason, next owner and residual risk for each
  non-accepted family.
- [x] 2.3 Confirm no raw capture payload, full probe output, local credential
  or generated EDT workspace path is committed.

## 3. Verification

- [x] 3.1 Verify all published accepted rows link back to classification
  evidence with capture ids, frame ranges, normalized hashes, dynamic fields,
  operation tokens, response markers and replay/probe status.
- [x] 3.2 Run `scripts\check.ps1`.
- [x] 3.3 Run
  `bin\openspec.cmd validate publish-readonly-fixture-mappings --strict`.
- [x] 3.4 Run `bin\openspec.cmd validate --all`.
- [x] 3.5 Run
  `git diff --check -- openspec/changes/publish-readonly-fixture-mappings docs/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Live read proof | Published accepted or unresolved fixture family mapping status | Evidence lineage table and publication checklist | Evidence index links to source, corpus, probe, comparison/classification and accepted-mapping evidence | `docs/protocol-research/evidence-index.md`; `docs/protocol-research/evidence/accepted-mappings/fixture-readonly-<run-id>/` | required | `project:qa-mcp` | N/A | Medium: publication can only be as complete as prior classification evidence |
| Delivery or runtime apply | Docs-only publication of reviewed fixture results | Offline documentation update and validation command list | OpenSpec validation, `scripts\check.ps1`, `git diff --check` | `openspec/changes/publish-readonly-fixture-mappings/`; `docs/protocol-research/` | required | `project:qa-mcp` | N/A | Low: live runtime is not required unless evidence must be regenerated |
| Managed form layout | Fixture families as displayed in published status tables | Accepted/unresolved status and next owner per family | Source and classification links, not new UI screenshots | `docs/protocol-research/evidence/fixture-sources/<run-id>/`; `docs/protocol-research/evidence/corpus-comparison/fixture-readonly-<run-id>/` | required | `/opt/vanessa-mcp-stack`, `/opt/edt-lab`, `project:qa-mcp` | N/A | Medium: unresolved form identity remains visible instead of accepted |
| Form module or command | Action/write UI behavior | N/A | N/A | N/A | N/A | `/opt/vanessa-mcp-stack` | Publication covers read-only mapping results only | Medium: later safe-action evidence is still required for clicks and commands |
