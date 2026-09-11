## 1. Manifest Contract

- [x] 1.1 Define the V3 mutation manifest row shape and required status
  markers for capture review.
- [x] 1.2 Update the corpus evidence contract so mutation rows publish compact
  reviewed evidence links instead of raw payloads.
- [x] 1.3 Record that rows remain fixture-local candidates unless
  mutation-specific replay, direct probe or typed contract proof supports
  accepted promotion.

## 2. Verification

- [x] 2.1 Record the docs/evidence boundary for this manifest change; runtime
  proof for underlying mutation rows remains in the state, handler and
  recovery changes.
- [x] 2.2 Run `bin\openspec.cmd validate mutation-corpus-manifest-updates
  --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/mutation-corpus-manifest-
  updates docs/protocol-research openspec/board`.

Reviewed manifest publication is retained under
`docs/protocol-research/evidence/client-fixture-v3-mutation/20260609-manifest-contract/`.
The corpus contract now records V3 fail-closed row fields, candidate/accepted
boundaries and the empty accepted-mapping publication under
`docs/protocol-research/evidence/accepted-mappings/client-fixture-v3-mutation-20260609/`.
No 1C process was started by this docs/contract change; runtime marker and
reset proof remains linked from the state, handler and recovery evidence.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Mutation manifest and evidence contract publication | Reviewed manifest fields and evidence-index updates | OpenSpec strict validation; diff check; compact reviewed docs links | `docs/protocol-research/evidence-index.md`; `docs/protocol-research/corpus-evidence-contract.md`; `.artifacts/openspec/mutation-corpus-manifest-updates/<run-id>/manifest-review/` | required | `project:qa-mcp` | N/A for live runtime apply: no 1C process is started | Medium: row shapes can drift if the tooling pipeline changes |
| Delivery or runtime apply | Fail-closed mutation row validation | Required field checklist and rejected-row behavior | Manifest review notes with missing-field and unsupported-target examples | `.artifacts/openspec/mutation-corpus-manifest-updates/<run-id>/manifest-review/` | required | `project:qa-mcp` | N/A for live runtime apply: validation is docs/tooling contract only | Medium: validation can be bypassed if future runners ignore the manifest |
| Runtime apply | Corpus publication boundary | Docs-only publication of safe mutation rows | Runtime apply skipped; verification limited to docs and manifest validation | `openspec/changes/mutation-corpus-manifest-updates/` | N/A | `project:qa-mcp` | No live mutation implementation is introduced here | Low: the contract may need to be revisited when runner support lands |
