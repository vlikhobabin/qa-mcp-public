## 1. Boundary Events

- [x] 1.1 Emit `pre_read`, `action_start`, `action_end`, `post_read`,
  `recovery` and `background` events for manager V2 safe-action rows.
- [x] 1.2 Include action id, target id, action family, result markers and
  chunk/frame correlation fields in `case_events.jsonl`.
- [x] 1.3 Keep action frame candidates separate from bootstrap, refresh and
  recovery traffic.
- [x] 1.4 Preserve candidate, partial, timeout, rejected or blocked statuses
  when boundaries are missing or ambiguous.

## 2. Verification

- [x] 2.1 Retain live or focused dry-run boundary evidence under
  `.artifacts/openspec/record-manager-fixture-v2-safe-action-boundaries/<run-id>/`.
- [x] 2.2 Run `bin\openspec.cmd validate
  record-manager-fixture-v2-safe-action-boundaries --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/record-manager-fixture-v2-safe-action-boundaries tools/protocol-research tests openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | Manager harness event emission around safe actions | Phase event sequence with action/background/recovery boundaries | BSL diagnostics; `case_events.jsonl`; manager harness result summary | `.artifacts/openspec/record-manager-fixture-v2-safe-action-boundaries/<run-id>/case-events/` | required | `project:qa-mcp`, `/opt/edt-lab` | N/A | Medium: side-channel timing can blur action frame joins |
| Delivery or runtime apply | Capture wrapper and V2 reporter input | Windows-native capture with phase-aware event output | Runtime capture summary; reporter dry-run or live summary; OpenSpec strict validation | `.artifacts/openspec/record-manager-fixture-v2-safe-action-boundaries/<run-id>/boundary-report/` | required | `project:qa-mcp` | N/A | Medium: boundary fields can regress reporter assumptions |
