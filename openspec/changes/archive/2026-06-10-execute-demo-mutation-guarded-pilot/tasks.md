## 1. Guarded Execution

- [x] 1.0 Run `scripts\preflight-live-runtime.ps1` (capture or attach mode per
  the selected runtime route) before any 1C process start or attach; retain
  `preflight_result.json` and stop with a recorded `runtime_gap` blocker when
  it fails.
- [x] 1.1 Load the selected target set and reviewed real-demo mutation manifest
  rows.
- [x] 1.2 Recheck active form/window, target marker, target enabled state and
  pre-state immediately before any action.
- [x] 1.3 Execute only rows that are complete, recoverable and scoped to the
  disposable demo10413 lab; otherwise retain a blocked summary.
- [x] 1.4 Use unique `QA_MCP_*` markers or object names when new demo data is
  created.
- [x] 1.5 Run reviewed recovery or cleanup and record final state, owner and
  residual risk for every executed row.
- [x] 1.6 Keep raw captures, full UI dumps, process logs and generated replay
  payloads under ignored runtime or artifact paths.

## 2. Verification

- [x] 2.1 Retain runtime evidence under
  `.artifacts/openspec/execute-demo-mutation-guarded-pilot/<run-id>/runtime-pilot/`.
- [x] 2.2 Retain cleanup and owned-process evidence under
  `.artifacts/openspec/execute-demo-mutation-guarded-pilot/<run-id>/runtime-cleanup/`.
- [x] 2.3 Run `bin\openspec.cmd validate execute-demo-mutation-guarded-pilot --strict`.
- [x] 2.4 Run `git diff --check -- openspec/changes/execute-demo-mutation-guarded-pilot openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | Reviewed real-demo document, catalog or processing action | Guarded execution or fail-closed blocked result | Scenario file or command wrapper summary; scenario log; action result markers; blocked summary when gates fail | `.artifacts/openspec/execute-demo-mutation-guarded-pilot/<run-id>/runtime-pilot/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | High: real demo commands may expose unexpected side effects even in disposable lab data |
| Managed form layout | Active demo form and target element before and after mutation | Pre-state recheck, post-state observations and recovery-state proof | Active-window proof, form tree, screenshot or fallback UI evidence | `.artifacts/openspec/execute-demo-mutation-guarded-pilot/<run-id>/ui-proof/` | required | `project:qa-mcp`, `vanessa-mcp`, `meta-mcp` | N/A | Medium: UI provider evidence can be incomplete if runtime capture fails |
| Delivery or runtime apply | Local 1C runtime run against `vanessa_client` and manager/client processes | Owned-process run plan, cleanup expectation and final-state record | Live runtime preflight result; runtime run summary; owned PID cleanup proof; recovery or residue summary | `.artifacts/openspec/execute-demo-mutation-guarded-pilot/<run-id>/runtime-cleanup/` | required | `project:qa-mcp` | N/A | Medium: local 1C runtime or provider readiness may block execution; the preflight converts this into a pre-execution `runtime_gap` |
