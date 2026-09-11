## 1. Guarded Capture

- [x] 1.1 Read the classification decision from
  `classify-demo-button-safety-contract`.
- [x] 1.2 Re-check runtime pre-state, active form/window and selected target
  marker before any click.
- [x] 1.3 Execute the single reviewed row only when all gates pass.
- [x] 1.4 Retain pre-read, action, post-read and recovery evidence, or retain a
  blocked summary when execution is not allowed.
- [x] 1.5 Keep raw captures and generated payloads under ignored runtime paths.

## 2. Verification

- [x] 2.1 Retain compact capture or blocked evidence under
  `.artifacts/openspec/capture-demo-button-safe-action-pilot/<run-id>/`.
- [x] 2.2 Run `bin\openspec.cmd validate capture-demo-button-safe-action-pilot --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/capture-demo-button-safe-action-pilot openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | Selected demo button runtime action | Guarded execution or fail-closed blocked result | Scenario file or command wrapper summary; scenario log; action result markers; blocked summary when gates fail | `.artifacts/openspec/capture-demo-button-safe-action-pilot/<run-id>/runtime-capture/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | High: a real demo command can still expose unexpected side effects |
| Managed form layout | Active demo form and target element | Pre-state recheck and post-state/recovery observations | Active-window proof, form tree, screenshot or fallback UI evidence | `.artifacts/openspec/capture-demo-button-safe-action-pilot/<run-id>/ui-proof/` | required | `project:qa-mcp`, `vanessa-mcp` | N/A | Medium: UI evidence can be incomplete if provider capture fails |
| Delivery or runtime apply | Local 1C runtime run against `vanessa_client` and manager/client processes | Owned-process run plan and cleanup expectation | Runtime run summary; owned PID cleanup proof; recovery status | `.artifacts/openspec/capture-demo-button-safe-action-pilot/<run-id>/runtime-cleanup/` | required | `project:qa-mcp` | N/A | Medium: capture may be blocked by unavailable local 1C runtime |
