## 1. Recovery Proof

- [x] 1.1 Define the before, action, post and recovery evidence sequence for
  V3 mutation cases.
- [x] 1.2 Retain a reset or baseline proof for each mutation case so the
  fixture returns to the V1 baseline.
- [x] 1.3 Keep the candidate action frame range separate from bootstrap,
  refresh and cleanup traffic in the reviewed evidence.
- [x] 1.4 Start from the closed V3 surface rows for text, number, date,
  checkbox toggle and inert button flows.
- [x] 1.5 Keep rows candidate unless same-action replay, direct Python-manager
  probe or typed contract proof supports accepted mutation promotion.

## 2. Verification

- [x] 2.1 Retain the Windows-native recovery-proof bundle with before,
  action, post, reset and rerun evidence for each mutation case.
- [x] 2.2 Run `bin\openspec.cmd validate mutation-reset-recovery-verification
  --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/mutation-reset-recovery-
  verification docs/protocol-research openspec/board`.

Reviewed recovery proof is retained under
`docs/protocol-research/evidence/client-fixture-v3-mutation/20260609-recovery-proof/`.
The rows reference Windows-native runtime marker/reset artifacts retained
under ignored `.artifacts/openspec/` paths and remain candidate-only because
mutation action-frame isolation plus replay/probe or typed contract proof is
not yet retained.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | Recovery sequence, reset and candidate-range isolation | Before/action/post/recovery proof bundle | Live runtime proof, form tree, active-window proof and reviewed capture summary | `.artifacts/openspec/mutation-reset-recovery-verification/<run-id>/recovery-proof/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: background refresh traffic can blur the range if isolation is weak |
| Runtime apply | Recovery verification and capture review | Strict validation and diff check | OpenSpec strict validation; reviewed compact evidence and frame-range review summary | `openspec/changes/mutation-reset-recovery-verification/` | required | `project:qa-mcp` | N/A | Low: no broader mutation semantics are introduced |
