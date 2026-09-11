## 1. Scenario Wiring

- [x] 1.1 Add the `manager-fixture-v2-safe-action` capture scenario entrypoint.
- [x] 1.2 Require reviewed safe-action manifest rows before the scenario starts
  capture or manager-runner execution.
- [x] 1.3 Emit pre-read, action, post-read, recovery and background phase
  events without injecting markers into TCP traffic.

## 2. Verification

- [x] 2.1 Run a Windows-native dry run that proves the scenario can create
  phase-aware runtime output under ignored paths.
- [x] 2.2 Run `bin\openspec.cmd validate add-manager-fixture-v2-safe-action-scenario --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/add-manager-fixture-v2-safe-action-scenario openspec/board`.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Protocol capture scenario `manager-fixture-v2-safe-action` | Windows-native scenario dry run with phase events | Runtime dry-run summary; sanitized phase-event sample; OpenSpec strict validation | `.artifacts/openspec/add-manager-fixture-v2-safe-action-scenario/<run-id>/scenario-dry-run/` | required | `project:qa-mcp` | N/A | Medium: manager harness event ordering can drift from captured traffic |
| Delivery or runtime apply | Raw capture boundary | Runtime output remains under ignored paths | Directory summary proving raw traffic is not committed | `runtime/protocol-research/`; `.artifacts/openspec/add-manager-fixture-v2-safe-action-scenario/<run-id>/raw-boundary/` | required | `project:qa-mcp` | N/A | Low: reviewed evidence links can drift if runtime output is moved |
