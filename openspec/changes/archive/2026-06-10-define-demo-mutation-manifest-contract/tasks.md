## 1. Manifest Contract

- [x] 1.1 Define the real-demo mutation manifest fields for target identity,
  object/form path, element path, operation family, pre-state, action, expected
  post-state, recovery expectation, residual risk, proof route and status.
- [x] 1.2 Specify when `mutates_business_data=true` is allowed for the
  disposable demo10413 pilot and when the row must fail closed.
- [x] 1.3 Define the accepted, candidate, rejected, blocked, partial and
  timeout status meanings for real-demo mutation rows.
- [x] 1.4 Update compact evidence contract notes or samples so downstream
  execution and publication can validate rows consistently.
- [x] 1.5 Record that accepted output remains empty without same-action replay,
  direct Python-manager probe or accepted typed contract proof.
- [x] 1.6 Align `proof_route` values with the proof classes in
  `docs/protocol-research/corpus-evidence-contract.md` ("Proof Classes By Risk
  Tier"): mutation rows need one proof class plus recovery/rerun proof, and the
  manifest must not demand additional proof classes beyond that minimum.

## 2. Verification

- [x] 2.1 Retain manifest-review evidence under
  `.artifacts/openspec/define-demo-mutation-manifest-contract/<run-id>/manifest-review/`.
- [x] 2.2 Run `bin\openspec.cmd validate define-demo-mutation-manifest-contract --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/define-demo-mutation-manifest-contract docs/protocol-research openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Real-demo mutation manifest and compact evidence contract | Reviewed field checklist, fail-closed examples and status taxonomy | OpenSpec strict validation; compact manifest review notes; optional docs/evidence contract diff | `.artifacts/openspec/define-demo-mutation-manifest-contract/<run-id>/manifest-review/` | required | `project:qa-mcp` | N/A | Medium: future runner code can drift if it bypasses this contract |
| Form module or command | Candidate command/action semantics represented in manifest rows | Operation family, target marker, pre-state, post-state and recovery expectation | Manifest sample rows with selected/rejected command rationale | `.artifacts/openspec/define-demo-mutation-manifest-contract/<run-id>/manifest-review/row-samples.md` | required | `project:qa-mcp`, `vanessa-mcp`, `meta-mcp` | N/A | High until guarded runtime pre-state and recovery proof are retained |
| Delivery or runtime apply | Live mutation execution | N/A for this contract-only change | N/A | N/A | N/A | `project:qa-mcp` | This change defines validation and does not start 1C or mutate data | Low: execution risk is owned by the guarded pilot change |
