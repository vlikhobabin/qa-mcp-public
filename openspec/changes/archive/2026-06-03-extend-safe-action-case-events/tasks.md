## 1. Event Contract

- [x] 1.1 Extend case manifest parsing for safe action fields:
  `pre_state`, `action`, `post_state`, `recovery_expectation` and
  `action_result_markers`.
- [x] 1.2 Extend case events with action start/end markers and status values
  for `supported`, `pending`, `unsupported`, `partial`, `timeout` and
  `rejected`.
- [x] 1.3 Preserve action frame range candidates separately from background
  refresh or idle frame ranges.

## 2. Tooling And Docs

- [x] 2.1 Extend compact corpus row generation with safe action fields while
  retaining the existing evidence contract fields.
- [x] 2.2 Add offline fixture rows or synthetic event tests for clean actions,
  refresh-surrounded actions and unsupported actions.
- [x] 2.3 Update `docs/protocol-research/corpus-evidence-contract.md` or an
  action-specific companion doc with the additive row fields.

## 3. Verification

- [x] 3.1 Run focused tests for action event parsing and row generation.
- [x] 3.2 Run `scripts\check.ps1`.
- [x] 3.3 Run `scripts\check-protocol-lab.ps1`.
- [x] 3.4 Run `bin\openspec.cmd validate extend-safe-action-case-events --strict`.
- [x] 3.5 Run `git diff --check -- openspec/changes/extend-safe-action-case-events tools/protocol-research tests docs/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Offline protocol runner/analyzer event and row tooling | Synthetic safe-action event fixtures and Windows check plan | Focused tests, `scripts\check.ps1`, `scripts\check-protocol-lab.ps1`, OpenSpec validation | `tests/`; `tools/protocol-research/`; `openspec/changes/extend-safe-action-case-events/` | required | `project:qa-mcp` | N/A for live apply: no runtime capture is required | Medium: offline fixtures may miss live timing edge cases |
| Managed form layout | Form/window/tab/menu action event labels and target references | Action manifest/event contract with target labels and result markers | Offline event fixtures plus documented action row schema | `docs/protocol-research/corpus-evidence-contract.md`; `tests/` | required | `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A for screenshot bundle: this change does not open forms | Medium: target labels still need live UI proof in the capture change |
| Form module or command | Command execution and input handlers | N/A | N/A | N/A | N/A | `/opt/vanessa-mcp-stack` | Mutating command/input actions stay excluded by the prior scope change | Medium: event fields do not prove command safety |
| BSL-only module edit | Python tools only; no 1C BSL source | N/A | N/A | N/A | N/A | `project:qa-mcp` | No BSL module is changed | None |
