## 1. Live Smoke

- [x] 1.1 Select the bounded smoke subset from the reviewed V1 command catalog.
- [x] 1.2 Run non-dry-run `manager-fixture-v1-readonly` when the EPF/runtime
  profile is available.
- [x] 1.3 Run join/analyzer tooling against the retained runtime directory.
- [x] 1.4 Attempt replay or direct Python-manager proof for supported command
  families.
- [x] 1.5 Publish compact reviewed smoke evidence under
  `docs/protocol-research/evidence/manager-fixture-v1-live-smoke/<run-id>/`.
- [x] 1.6 Update evidence index and protocol research docs with the live smoke
  result or provider gap.

## 2. Verification

- [x] 2.1 Verify raw traffic and platform logs remain under ignored
  `runtime/protocol-research/` paths.
- [x] 2.2 Verify reviewed evidence contains no raw payloads, secrets or full
  platform logs.
- [x] 2.3 Run `openspec validate publish-manager-fixture-v1-live-smoke-evidence --strict`.
- [x] 2.4 Run `git diff --check -- openspec/changes/publish-manager-fixture-v1-live-smoke-evidence docs/protocol-research`.

## Verification Matrix

| surface | affected_scope | planning_output | required_evidence | artifact_path | status | provider_owner | n/a_reason | residual_risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Bounded live manager fixture V1 smoke | Non-dry-run capture command, retained runtime summary and cleanup proof | `runtime_apply_log`, `scenario_log`, `data_assertion` | `.artifacts/openspec/publish-manager-fixture-v1-live-smoke-evidence/<run-id>/capture/` | required | `project:qa-mcp`, `/opt/vanessa-mcp-stack` | N/A | High: missing EPF/runtime profile blocks live evidence |
| Form module or command | Read-only manager harness commands selected for smoke | Executed command ids with before/after events | `scenario_file`, `scenario_log` | `docs/protocol-research/evidence/manager-fixture-v1-live-smoke/<run-id>/` | required | `project:qa-mcp` | N/A | Medium: command may fail but must be retained as evidence |
| Managed form layout | Client fixture V1 active form during smoke | Active-window/form and form-analysis proof | `active_window`, `form_tree`, `vanessa_ui_smoke_bundle` | `.artifacts/openspec/publish-manager-fixture-v1-live-smoke-evidence/<run-id>/client-fixture/` | required | `/opt/vanessa-mcp-stack` | N/A | Medium: screenshot may be unavailable; form-analysis fallback is acceptable |
| Report or DCS change | Reports/DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS object is changed | Low: none |
