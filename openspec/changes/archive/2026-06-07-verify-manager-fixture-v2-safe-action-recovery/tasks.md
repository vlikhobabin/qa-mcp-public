## 1. Recovery Verification

- [x] 1.1 Define recovery expectations for each executable V2 safe-action row
  and record known-state rationale where reset is not needed.
- [x] 1.2 Retain recovery result markers and separate recovery frame ranges in
  reviewed evidence.
- [x] 1.3 Verify rerun determinism for the first supported focused subset.
- [x] 1.4 Mark rows blocked, rejected, partial, timeout or candidate when
  recovery cannot be proved.

## 2. Verification

- [x] 2.1 Retain Windows-native recovery proof under
  `.artifacts/openspec/verify-manager-fixture-v2-safe-action-recovery/<run-id>/`.
- [x] 2.2 Run `bin\openspec.cmd validate
  verify-manager-fixture-v2-safe-action-recovery --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/verify-manager-fixture-v2-safe-action-recovery docs/protocol-research openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | Manager recovery/reset sequence after V2 actions | Recovery route, known-state markers and rerun sequence | BSL diagnostics; scenario log; recovery-read marker proof | `.artifacts/openspec/verify-manager-fixture-v2-safe-action-recovery/<run-id>/recovery-sequence/` | required | `project:qa-mcp`, `vanessa-mcp`, `/opt/edt-lab` | N/A | High: recovery failures can leave fixture state ambiguous |
| Managed form layout | Client fixture state after recovery | Baseline or known-state marker proof | Form tree; active-window proof; selected page/row/focus markers after recovery | `.artifacts/openspec/verify-manager-fixture-v2-safe-action-recovery/<run-id>/post-recovery-state/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: hidden UI state may not be visible in a single marker |
| Delivery or runtime apply | Recovery proof and capture review | Compact recovery evidence with separated recovery ranges | Reviewed capture summary; OpenSpec strict validation; diff check | `openspec/changes/verify-manager-fixture-v2-safe-action-recovery/` | required | `project:qa-mcp` | N/A | Low: recovery proof is fixture-local and non-mutating |
