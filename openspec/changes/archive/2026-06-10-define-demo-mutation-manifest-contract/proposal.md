## Why

Real demo10413 mutations are useful only if each attempted action is reviewed
through a machine-readable contract. The manifest must make business-data
mutation explicit, require recovery, and prevent incomplete rows from reaching
guarded execution.

## What Changes

- Define a real-demo mutation manifest row shape with `target_id`, object/form
  path, element path, operation family, target marker, pre-state, action,
  expected post-state, recovery expectation, residual risk and proof route.
- Permit `mutates_business_data=true` for this pilot only when recovery or
  cleanup is explicit and reviewed.
- Define row statuses: `accepted`, `candidate`, `rejected`, `blocked`,
  `partial` and `timeout`.
- Require fail-closed validation for incomplete, unsupported, unrecoverable or
  externally side-effecting rows.
- Keep accepted mapping output empty unless same-action replay, direct
  Python-manager probe or accepted typed contract proof supports the row.
- Align `proof_route` values and acceptance minimums with the "Proof Classes
  By Risk Tier" section of
  `docs/protocol-research/corpus-evidence-contract.md`: one proof class plus
  recovery/rerun proof is the mutation-tier minimum, and reviewers must not
  require additional proof classes beyond that minimum.

## Capabilities

### New Capabilities

### Modified Capabilities

- `qa-mcp-protocol-lab`: Real demo mutation rows gain an explicit manifest
  contract that permits reviewed business-data mutations only with recovery
  and proof-gated publication.

## Impact

- Protocol research docs, planned manifest samples and compact review evidence
  under `.artifacts/openspec/define-demo-mutation-manifest-contract/<run-id>/`.
- May update `docs/protocol-research/corpus-evidence-contract.md` during
  implementation.
- No live 1C runtime mutation is executed by this contract change.
