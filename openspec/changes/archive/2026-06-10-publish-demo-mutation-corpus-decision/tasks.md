## 1. Publication

- [x] 1.1 Gather target-selection, manifest, guarded execution or blocked
  result, recovery and frame-isolation evidence.
- [x] 1.2 Publish compact real-demo mutation evidence with final status, proof
  route, recovery status, residual demo data note and residual risk for every
  selected or attempted row.
- [x] 1.3 Update protocol evidence index and accepted-output or candidate-output
  summaries as appropriate.
- [x] 1.4 Keep accepted output empty unless same-action replay, direct
  Python-manager probe or accepted typed contract proof supports the same row.
- [x] 1.5 Keep raw captures, full UI dumps, platform logs and generated replay
  payloads out of reviewed git.
- [x] 1.6 Update `docs/protocol-research/api-inventory/case-api-map.json` with
  any newly proven demo-mutation correspondences and regenerate
  `docs/protocol-research/coverage-report.md` via
  `python tools\protocol-research\coverage_report.py`.
- [x] 1.7 State the batch-readiness decision: whether the mutation scheme is
  proven well enough to plan the 30-50 row batch corpus card per
  `docs/protocol-research/methodology.md`.

## 2. Verification

- [x] 2.1 Retain publication evidence under
  `docs/protocol-research/evidence/demo-real-mutation-corpus/<run-id>/` or
  `.artifacts/openspec/publish-demo-mutation-corpus-decision/<run-id>/`.
- [x] 2.2 Run `bin\openspec.cmd validate publish-demo-mutation-corpus-decision --strict`.
- [x] 2.3 Run `bin\openspec.cmd validate --all`.
- [x] 2.4 Run `git diff --check -- openspec/changes/publish-demo-mutation-corpus-decision docs/protocol-research openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | Published real-demo mutation rows | Final status, proof route and blocker/recovery notes per row | Manifest review, guarded execution or blocked summary, frame-isolation summary and accepted proof or non-accepted reason | `docs/protocol-research/evidence/demo-real-mutation-corpus/<run-id>/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: candidate publication may still need future replay/probe proof |
| Managed form layout | Demo form target evidence linked from publication | Linked target, active-window/form and UI evidence summary | Form tree, active-window proof, screenshot or fallback evidence from previous changes | `docs/protocol-research/evidence/demo-real-mutation-corpus/<run-id>/ui-evidence.md` | required | `project:qa-mcp`, `vanessa-mcp`, `meta-mcp` | N/A | Low if linked evidence remains compact and reviewable |
| Delivery or runtime apply | Publication-only docs and index updates | Evidence-index update and accepted/candidate output decision | OpenSpec strict validation; all-change validation; diff check; compact docs links | `docs/protocol-research/evidence-index.md`; `docs/protocol-research/evidence/demo-real-mutation-corpus/<run-id>/` | required | `project:qa-mcp` | N/A for live runtime execution: publication itself does not execute actions | Low: runtime risks are owned by guarded execution |
