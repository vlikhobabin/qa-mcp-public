## 1. Recovery Proof

- [x] 1.1 Define the V4 before, action/dialog, result, recovery and recovery-
  read sequence for warning, question, modal, expected-error and wait cases.
- [x] 1.2 Retain recovery proof that reset returns every V4 marker family to
  the V1 baseline or records a candidate-only residual state.
- [x] 1.3 Keep dialog/action, background, expected-error and recovery ranges
  separated in reviewed evidence.
- [x] 1.4 Treat upstream V2 runner/proof and V3 recovery prerequisites as
  closed; keep V4 rows candidate unless V4-specific replay, direct probe or
  typed contract proof supports accepted promotion.

## 2. Verification

- [x] 2.1 Retain the Windows-native V4 recovery proof bundle with before,
  action/dialog, result, recovery and rerun evidence.
- [x] 2.2 Run `bin\openspec.cmd validate v4-dialog-recovery-verification
  --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/v4-dialog-recovery-
  verification docs/protocol-research openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | V4 recovery markers, modal active form and wait/result marker reads | Before/action/result/recovery/rerun proof bundle | Live runtime proof; form tree; active-window proof; reviewed capture summary | `.artifacts/openspec/v4-dialog-recovery-verification/20260609-v4-designer-apply/recovery-proof/` | done | `project:qa-mcp`, `vanessa-mcp` | N/A | Low: modal remains marker-only and candidate; fallback evidence separates action/reset bundles |
| Form module or command | Reset and recovery commands for V4 scenario families | Deterministic cleanup and rerun model | BSL diagnostics; Vanessa scenario log; marker read after recovery | `.artifacts/openspec/v4-dialog-recovery-verification/20260609-v4-static-contract/handler-recovery/` | done | `project:qa-mcp`, `vanessa-mcp`, `/opt/edt-lab` | N/A | Low: reset proof validates baseline state plus candidate-only residual recovery marker |
| Delivery or runtime apply | Recovery verification and capture review | Strict validation, compact evidence and no raw TCP in git | OpenSpec strict validation; reviewed compact evidence and frame-range review summary | `docs/protocol-research/evidence/client-fixture-v4-dialog-recovery/20260609-manifest-contract/` | done | `project:qa-mcp` | N/A | Low: recovery proof does not introduce broader business semantics |
