## 1. Acceptance Gates

- [x] 1.1 Extend comparison logic so joined safe-action rows remain
  non-accepted until proof gates are satisfied.
- [x] 1.2 Require stable normalized hash, action result markers and accepted
  replay/probe or typed contract evidence before accepted-mapping output.
- [x] 1.3 Keep candidate, blocked, partial, timeout, rejected and unsupported
  safe-action rows visible with reason fields.

## 2. Verification

- [x] 2.1 Retain comparison samples for accepted and non-accepted safe-action
  rows.
- [x] 2.2 Verify read-only comparison and accepted-mapping behavior remains
  stable.
- [x] 2.3 Run `bin\openspec.cmd validate add-v2-safe-action-acceptance-gates --strict`.
- [x] 2.4 Run `git diff --check -- openspec/changes/add-v2-safe-action-acceptance-gates openspec/board docs/protocol-research`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Safe-action comparison and accepted-mapping gates | Accepted and non-accepted sample rows with proof status | Comparison summary; accepted-output summary; OpenSpec strict validation | `.artifacts/openspec/add-v2-safe-action-acceptance-gates/<run-id>/acceptance-gates/` | required | `project:qa-mcp` | N/A | Medium: side-channel proof can be over-interpreted without contract labels |
| Delivery or runtime apply | Existing read-only comparison behavior | Regression check for read-only comparison and accepted mappings | Focused comparison smoke summary | `.artifacts/openspec/add-v2-safe-action-acceptance-gates/<run-id>/readonly-regression/` | required | `project:qa-mcp` | N/A | Low: shared comparison code can affect legacy output |
