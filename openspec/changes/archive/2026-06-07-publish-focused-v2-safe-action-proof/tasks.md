## 1. Proof Publication

- [x] 1.1 Consume accepted/candidate row decisions from
  `probe-focused-v2-safe-action-contract`.
- [x] 1.2 Publish a compact proof report with selected rows, action/background/
  recovery ranges, normalized hashes, dynamic fields, proof route and final
  status.
- [x] 1.3 Update accepted-mapping output only for rows that satisfy replay/probe
  or typed contract gates.
- [x] 1.4 Keep candidate, blocked, partial, timeout, rejected and unsupported
  rows visible with reasons.

## 2. Docs And Evidence Index

- [x] 2.1 Update `docs/protocol-research/evidence-index.md` with the focused
  proof path and status.
- [x] 2.2 Update V2 protocol docs or status/readiness references with the proof
  outcome and residual risk.
- [x] 2.3 Link ignored runtime output only through sanitized compact summaries.
- [x] 2.4 Preserve the V2 safety boundary and route demo real-button pilots to
  later cards.

## 3. Verification

- [x] 3.1 Retain publication proof under
  `.artifacts/openspec/publish-focused-v2-safe-action-proof/<run-id>/publication/`.
- [x] 3.2 Run `bin\openspec.cmd validate publish-focused-v2-safe-action-proof --strict`.
- [x] 3.3 Run `bin\openspec.cmd validate --all`.
- [x] 3.4 Run `git diff --check -- openspec/changes/publish-focused-v2-safe-action-proof docs/protocol-research openspec/board`.

## Evidence

- Publication summary:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-publication/publication_summary.md`
- Frame isolation:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-live-action-frame-join/frame_isolation_summary.md`
- Proof decision:
  `docs/protocol-research/evidence/manager-fixture-v2-safe-action/20260607-first-focused-proof-decision/proof_summary.md`
- Accepted mapping output:
  `docs/protocol-research/evidence/accepted-mappings/manager-fixture-v2-first-focused-proof-20260607/accepted_mappings.md`
- Publication handoff:
  `.artifacts/openspec/publish-focused-v2-safe-action-proof/20260607-first-focused-v2-safe-action-live-runner-2/publication/publication_summary.md`
- Docs updated:
  `docs/protocol-research/evidence-index.md`,
  `docs/protocol-research/safe-ui-action-scope.md`,
  `docs/protocol-research/README.md`
- Final status: 2 candidate rows, 0 accepted rows. Accepted-mapping output is
  empty by design.

## 4. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Protocol docs, evidence index and accepted/candidate outputs | Publication plan that links compact proof and excludes raw runtime output | Publication summary; accepted/candidate count check; OpenSpec strict validation; diff check | `.artifacts/openspec/publish-focused-v2-safe-action-proof/<run-id>/publication/` | required | `project:qa-mcp`, `/opt/ai-tools-1c` | N/A | Medium: docs can overstate candidate rows if status is not adjacent to links |
| Form module or command | Focused manager V2 safe-action proof rows | Final accepted/candidate decision per selected row | Proof report; action result marker summary; accepted-mapping or candidate-output summary | `.artifacts/openspec/publish-focused-v2-safe-action-proof/<run-id>/row-status/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: candidate status may still block downstream demo pilots |
| Managed form layout | Additional live UI evidence | N/A for publication-only change | N/A | N/A | N/A | `project:qa-mcp`, `vanessa-mcp` | Publication consumes prior capture/proof evidence and does not open a new form | Low: stale UI evidence remains a risk only if prior changes are incomplete |
