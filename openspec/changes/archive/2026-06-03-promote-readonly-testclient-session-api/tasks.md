## 1. Package Session API

- [x] 1.1 Move `TestClientSession` and read-only exchange methods into `src/qa_mcp/protocol/`.
- [x] 1.2 Expose package methods for `initial-ui`, `active-window-context`, `active-form-context`, `form-summary` and `form-element-details`.
- [x] 1.3 Ensure query results include evidence status, source template/capture fields and runtime output policy.
- [x] 1.4 Keep all methods read-only and reject or omit action/write operations.

## 2. Tests

- [x] 2.1 Add fake-socket or fixture tests for session connect, send/read and cleanup semantics.
- [x] 2.2 Add tests for active-window and active-form result parsing and accepted evidence links.
- [x] 2.3 Add tests that form-element details and typed input are exposed as unresolved or partial, not accepted.

## 3. Optional Live Smoke

- [x] 3.1 Add or document a Windows-native read-only smoke command for a running `/TESTCLIENT`.
- [x] 3.2 If lab runtime is available during delivery, run the live smoke and retain compact evidence under `docs/protocol-research/evidence/`.
- [x] 3.3 If lab runtime is unavailable, record a provider/environment gap with the expected evidence path and residual risk.

## 4. Verification

- [x] 4.1 Run `scripts\check.ps1`.
- [x] 4.2 Run `scripts\check-protocol-lab.ps1`.
- [x] 4.3 Run focused package session tests.
- [x] 4.4 Run optional live read-only smoke or record explicit environment gap.
- [x] 4.5 Run `bin\openspec.cmd validate promote-readonly-testclient-session-api --strict`.
- [x] 4.6 Run `bin\openspec.cmd validate --all`.
- [x] 4.7 Run `git diff --check -- openspec/changes/promote-readonly-testclient-session-api src tools/protocol-research tests docs/protocol-research`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Delivery or runtime apply | Package `TestClientSession` and read-only query API | Offline tests plus optional live read-only smoke | `scripts\check.ps1`, focused tests, py_compile, optional smoke summary | `tests/`; `src/qa_mcp/protocol/`; `docs/protocol-research/evidence/python-manager-package-smoke/<run-id>/` | required | project:qa-mcp | N/A for deploy/apply: local Python runtime only | Medium: live socket timing can differ by platform/runtime |
| Managed form layout | Active-window, active-form, form-summary and element-detail read-only UI responses | Existing accepted evidence plus optional fresh read-only smoke | accepted mappings, probe result, optional compact smoke evidence | `docs/protocol-research/evidence/accepted-mappings/`; `docs/protocol-research/evidence/python-manager-probe/expanded-20260602-193802/`; optional smoke path | required | /opt/vanessa-mcp-stack | N/A for UI mutation: read-only queries only | Medium: current fixture does not cover all element families |
| BSL-only module edit | 1C BSL modules | N/A | N/A | N/A | N/A | project:qa-mcp | No BSL source is changed | None |
| Metadata object | 1C metadata and EDT workspace | N/A | N/A | N/A | N/A | /opt/edt-lab | No metadata source or EDT workspace is changed | None |
| Role rights | Target users and roles | N/A | N/A | N/A | N/A | project:qa-mcp | Session API is read-only and not role-specific in this card | Low: future restricted-role behavior remains untested |
