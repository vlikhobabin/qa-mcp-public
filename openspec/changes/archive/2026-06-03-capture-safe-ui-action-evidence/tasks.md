## 1. Capture Preparation

- [x] 1.1 Confirm the safe action candidate manifest and prerequisite status
  from `define-safe-ui-action-scope`.
- [x] 1.2 Confirm action event support from `extend-safe-action-case-events`.
- [x] 1.3 Select a capture id and prepare ignored runtime output under
  `runtime/protocol-research/captures/<capture-id>/`.
- [x] 1.4 Select a reviewed evidence directory under
  `docs/protocol-research/evidence/corpus/<capture-id>-safe-action/`.

## 2. Live Capture

- [x] 2.1 Run a Windows-native Vanessa attach-running capture for one or more
  safe non-mutating actions, for example a scoped `safe-action` scenario or
  custom manifest.
- [x] 2.2 Record pre-state, action, post-state and recovery/cleanup result for
  each attempted case.
- [x] 2.3 Preserve raw captures, case events and platform logs only under
  ignored `runtime/protocol-research/` paths.
- [x] 2.4 Record unsupported, pending, partial, timeout or rejected outcomes
  for unavailable or unsafe action candidates.

## 3. Compact Evidence

- [x] 3.1 Generate compact reviewed rows with frame ranges, normalized hashes,
  dynamic fields, operation tokens, response markers, replay status and action
  result markers.
- [x] 3.2 Update `docs/protocol-research/evidence-index.md` with the new
  compact action evidence path.
- [x] 3.3 Retain cleanup proof showing only owned PIDs were stopped.

## 4. Verification

- [x] 4.1 Run `scripts\check-protocol-lab.ps1`.
- [x] 4.2 Run `scripts\check.ps1`.
- [x] 4.3 Run `bin\openspec.cmd validate capture-safe-ui-action-evidence --strict`.
- [x] 4.4 Run `git diff --check -- openspec/changes/capture-safe-ui-action-evidence docs/protocol-research tools/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Windows-native safe action capture against local TestClient/Vanessa lab | Non-interactive capture command plan, output boundary and owned-PID cleanup expectation | Capture summary, case events, cleanup proof, compact corpus rows; raw captures ignored | `runtime/protocol-research/captures/<capture-id>/`; `docs/protocol-research/evidence/corpus/<capture-id>-safe-action/` | required | `project:qa-mcp`, `/opt/vanessa-mcp-stack` | N/A | High: live 1C timing and UI target availability can fail |
| Managed form layout | Active form elements, active window, tabs/pages and menus targeted by safe actions | Target review, pre/post state plan and result markers | Vanessa attach-running proof, active-window/form evidence, optional screenshot/form tree bundle | `.artifacts/openspec/capture-safe-ui-action-evidence/<run-id>/`; `docs/protocol-research/evidence/corpus/<capture-id>-safe-action/` | required | `/opt/vanessa-mcp-stack` | N/A | Medium: safe target may not exist in current fixture |
| Form module or command | Commands, click handlers, input handlers and write actions | N/A | N/A | N/A | N/A | `/opt/vanessa-mcp-stack` | Mutating commands and inputs are excluded from this capture | Medium: command behavior remains unknown until a mutation-specific card |
| Role rights | Existing lab user/session rights | N/A | N/A | N/A | N/A | `project:qa-mcp` | No role-specific behavior is targeted; current lab access is used only for protocol capture | Low: role-specific UI availability remains out of scope |
