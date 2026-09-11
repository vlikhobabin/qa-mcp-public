## 1. Publication

- [x] 1.1 Gather target-selection, classification and capture or blocked
  evidence.
- [x] 1.2 Publish compact pilot evidence with final status, recovery status,
  proof route and residual risk.
- [x] 1.3 Update protocol evidence index and accepted-mapping or candidate
  output as appropriate.
- [x] 1.4 Record V3 routing when the result is mutating, business-owned,
  rollback-dependent or outside the V2 allowlist.
- [x] 1.5 Keep raw captures, platform logs and generated replay payloads out of
  reviewed git.

## 2. Verification

- [x] 2.1 Retain publication evidence under
  `docs/protocol-research/evidence/demo-button-safe-action/<run-id>/` or
  `.artifacts/openspec/publish-demo-button-safe-action-decision/<run-id>/`.
- [x] 2.2 Run `bin\openspec.cmd validate publish-demo-button-safe-action-decision --strict`.
- [x] 2.3 Run `bin\openspec.cmd validate --all`.
- [x] 2.4 Run `git diff --check -- openspec/changes/publish-demo-button-safe-action-decision docs/protocol-research openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | Published demo button pilot row | Final status and proof route for selected button | Classification decision; capture or blocked summary; accepted proof or non-accepted reason | `docs/protocol-research/evidence/demo-button-safe-action/<run-id>/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: candidate publication may still require future replay/probe proof |
| Managed form layout | Demo form target evidence used by publication | Linked target and UI evidence | Form tree, active-window proof, screenshot or fallback evidence summary | `docs/protocol-research/evidence/demo-button-safe-action/<run-id>/ui-evidence.md` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Low if linked evidence remains compact and reviewable |
| Delivery or runtime apply | Publication-only docs update | N/A for publication execution | N/A | N/A | N/A | `project:qa-mcp` | This change publishes reviewed evidence and does not execute new runtime actions | Low: runtime risks are owned by the capture change |
