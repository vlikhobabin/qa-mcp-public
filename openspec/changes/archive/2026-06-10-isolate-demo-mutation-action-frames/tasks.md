## 1. Frame Isolation

- [x] 1.1 Load guarded-pilot phase events, manifest rows and available capture
  or analyzer output.
- [x] 1.2 Identify action, background/refresh and recovery ranges for each
  attempted row where evidence permits.
- [x] 1.3 Record dynamic fields, normalized hash, operation token and response
  markers when they are supported by reviewed frame evidence.
- [x] 1.4 Classify ambiguous, missing or unsupported ranges as candidate,
  rejected, blocked, partial or timeout with owner route and residual risk,
  using the retained live runtime preflight result to separate runtime gaps
  from frame-evidence gaps.
- [x] 1.5 Preserve that accepted status requires same-action replay, direct
  Python-manager probe or accepted typed contract proof.

## 2. Verification

- [x] 2.1 Retain frame-isolation evidence under
  `.artifacts/openspec/isolate-demo-mutation-action-frames/<run-id>/frame-isolation/`.
- [x] 2.2 Run `bin\openspec.cmd validate isolate-demo-mutation-action-frames --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/isolate-demo-mutation-action-frames openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | Executed or blocked real-demo mutation rows | Action/background/recovery range classification per manifest row | Frame-isolation summary; action result markers; accepted-proof or non-accepted reason | `.artifacts/openspec/isolate-demo-mutation-action-frames/<run-id>/frame-isolation/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | High: command semantics cannot be accepted if frame joins stay ambiguous |
| Delivery or runtime apply | Analyzer/reviewer output from guarded runtime capture | Normalized hash, dynamic-field and response-marker review when available | Compact analyzer report; unresolved-frame provider-gap notes | `.artifacts/openspec/isolate-demo-mutation-action-frames/<run-id>/analyzer-review/` | required | `project:qa-mcp` | N/A | Medium: current tooling may not support every real-demo action family |
| Managed form layout | UI phase boundaries around action and recovery | Evidence that action, refresh and recovery phases map to the selected target | Linked active-window/form proof or fallback UI evidence from guarded pilot | `.artifacts/openspec/execute-demo-mutation-guarded-pilot/<run-id>/ui-proof/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: UI evidence may be indirect if only capture events are retained |
