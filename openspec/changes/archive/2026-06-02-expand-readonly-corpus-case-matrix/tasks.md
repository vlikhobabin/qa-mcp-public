## 1. Expanded Case Matrix

- [x] 1.1 Define a manifest section for read-only element-family cases with
  `case_id`, `api_call`, `ui_target`, expected state, safety class, replay
  expectation and family label.
- [x] 1.2 Add candidate cases for `Button`, `Table`, `CommandBar`, `Page`,
  `Label`, `CheckBox` and typed input fields where the current lab form
  exposes them.
- [x] 1.3 Mark unavailable families as `unsupported` or `pending` with a
  fixture/probe follow-up reason.

## 2. Runner And Evidence

- [x] 2.1 Extend the corpus runner or companion manifest loader to emit family
  labels and expected response markers for the expanded matrix.
- [x] 2.2 Generate compact reviewed rows for each supported read-only family
  under `docs/protocol-research/evidence/`.
- [x] 2.3 Update `docs/protocol-research/evidence-index.md` with the expanded
  corpus evidence.
- [x] 2.4 Keep raw captures, case events and temporary logs under ignored
  `runtime/protocol-research/` paths.

## 3. Replay Or Probe Confirmation

- [x] 3.1 Identify which expanded read-only families can be confirmed with the
  current Python-manager probe path.
- [x] 3.2 Run at least one direct Python-manager probe for a supported new
  family.
- [x] 3.3 Record `accepted`, `pending`, `unsupported`, `partial`, `timeout` or
  `rejected` status for every expanded case.

## 4. Verification

- [x] 4.1 Run `scripts\check.ps1`.
- [x] 4.2 Run `scripts\check-protocol-lab.ps1`.
- [x] 4.3 Run a short Windows Vanessa attach-running capture for the expanded
  read-only matrix.
- [x] 4.4 Retain compact evidence under `docs/protocol-research/evidence/`.
- [x] 4.5 Run `bin\openspec.cmd validate expand-readonly-corpus-case-matrix --strict`.
- [x] 4.6 Run `bin\openspec.cmd validate --all`.
- [x] 4.7 Run `git diff --check -- openspec/changes/expand-readonly-corpus-case-matrix tools/protocol-research docs/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Expanded Windows protocol corpus capture over local TestClient and Vanessa manager | Non-interactive capture/probe command plan and owned-PID cleanup expectation | `scripts\check.ps1`, `scripts\check-protocol-lab.ps1`, capture summary, cleanup proof, compact corpus report | `runtime/protocol-research/captures/<run-id>/capture_summary.json`; `docs/protocol-research/evidence/corpus/<run-id>-expanded-readonly/` | required | project:qa-mcp | N/A for deployment apply: local protocol tooling only | Medium: live 1C process startup and fixture availability are environment-dependent |
| Managed form layout | Active form element families used as read-only protocol targets | Element-family matrix, expected active form/window and response markers | Vanessa attach-running result, active-window/form proof, compact corpus rows per supported family | `runtime/protocol-research/captures/<run-id>/case_events.jsonl`; reviewed summary under `docs/protocol-research/evidence/` | required | /opt/vanessa-mcp-stack | N/A for layout mutation: no form source is changed | Medium: current demo form may not expose every target family |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | project:qa-mcp | No BSL source is changed | None |
| Role rights | Target users and roles | N/A | N/A | N/A | N/A | project:qa-mcp | First expanded read-only matrix uses existing lab administrator access only | Low: role-specific protocol differences remain out of scope |
