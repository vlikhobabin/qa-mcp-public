## 1. Recovery Proof

- [x] 1.1 Define the before, action, post and recovery evidence sequence for
  the V2 safe-action cases.
- [x] 1.2 Retain a reset or baseline proof for each safe-action case so the
  fixture returns to the V1 baseline.
- [x] 1.3 Keep the candidate action frame range separate from bootstrap,
  refresh and cleanup traffic in the reviewed evidence.

## 2. Verification

- [x] 2.1 Record the Windows-native recovery-proof boundary for this docs-
  focused change; runtime proof remains downstream.
- [x] 2.2 Run `bin\openspec.cmd validate
  verify-client-fixture-v2-safe-action-recovery --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/verify-client-fixture-v2-safe-action-recovery docs/protocol-research openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | Recovery sequence, reset and candidate-range isolation | Before/action/post/recovery proof bundle | Live runtime proof and reviewed capture summary | `.artifacts/openspec/verify-client-fixture-v2-safe-action-recovery/<run-id>/recovery-proof/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: background refresh traffic can blur the range if isolation is weak |
| Runtime apply | Recovery verification and capture review | Strict validation and diff check | OpenSpec strict validation; reviewed compact evidence | `openspec/changes/verify-client-fixture-v2-safe-action-recovery/` | required | `project:qa-mcp` | N/A | Low: no broader mutation semantics are introduced |
