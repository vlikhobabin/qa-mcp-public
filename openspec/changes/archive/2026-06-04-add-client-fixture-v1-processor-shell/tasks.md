## 1. Target And Metadata Shell

- [x] 1.1 Run `validate_project_infobase_binding(target_id="client", timeout_seconds=90)` and retain a compact summary before EDT retrieve/update work.
- [x] 1.2 Create the dedicated V1 fixture data processor in the `vanessa_client` EDT source tree.
- [x] 1.3 Add the default managed form and form-level markers `PF_FORM_MAIN`, `PF_FIXTURE_VERSION` and `protocol-fixture.v1`.
- [x] 1.4 Add local fixture state attributes `PF_LAST_ACTION`, `PF_ACTION_COUNTER` and `PF_SELECTED_ROW_MARKER`.
- [x] 1.5 Add the named reset command hook for later versions without requiring action acceptance in this change.

## 2. Form Initialization

- [x] 2.1 Initialize shell attributes deterministically on form creation.
- [x] 2.2 Keep initialization independent from business data and external services.
- [x] 2.3 Ensure the processor has a documented path for opening the form in TestClient.

## 3. Verification

- [x] 3.1 Run EDT/source validation for the changed metadata and form module.
- [x] 3.2 Attempt fixture form-open verification or retain an explicit provider/runtime gap when the form is not applied to the infobase.
- [x] 3.3 Record compact shell readiness evidence under `docs/protocol-research/evidence/fixture-sources/<run-id>/`.
- [x] 3.4 Run `openspec validate add-client-fixture-v1-processor-shell --strict`.
- [x] 3.5 Run `git diff --check -- openspec/changes/add-client-fixture-v1-processor-shell`.

## Verification Results

- Source XML parse check passed for the new processor `.mdo`, form XML,
  `Configuration.mdo` and subsystem metadata.
- Marker grep confirmed `PF_FORM_MAIN`, `PF_FIXTURE_VERSION`,
  `protocol-fixture.v1`, `PF_LAST_ACTION`, `PF_ACTION_COUNTER`,
  `PF_SELECTED_ROW_MARKER` and `PF_RESET_STATE` in the source tree.
- Compact source evidence was retained at
  `docs/protocol-research/evidence/fixture-sources/20260604-client-fixture-v1-shell/source_summary.md`.
- `validate_project_infobase_binding(target_id="client")` was attempted
  through the live `edt-mcp` tool and timed out after 120 seconds. The compact
  evidence records this provider gap; no retrieve, DB update, hot deploy or
  runtime apply was performed.
- TestClient/Vanessa form-open evidence is deferred because the fixture shell
  was not applied to the infobase in this change.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Metadata object | V1 fixture data processor in `vanessa_client` | Target-bound metadata shell and default form registration | EDT validation report; source preflight summary | `.artifacts/openspec/add-client-fixture-v1-processor-shell/<run-id>/edt-validation/`; `docs/protocol-research/evidence/fixture-sources/<run-id>/source_summary.md` | required | `/opt/edt-lab`, `project:qa-mcp` | N/A | Medium: EDT XML shape must match local project conventions |
| Managed form layout | Fixture default form with `PF_FORM_MAIN` and version marker | Read-only form-open scenario and expected marker list | Vanessa/TestClient form open, active form proof, form tree or fallback UI summary | `.artifacts/openspec/add-client-fixture-v1-processor-shell/<run-id>/ui-smoke/` | required | `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A | Medium: UI provider may need a fixture-open helper |
| Form module or command | Form initialization and reset hook | Deterministic initialization; reset command documented as future hook | BSL diagnostics; no action acceptance required | `.artifacts/openspec/add-client-fixture-v1-processor-shell/<run-id>/bsl-diagnostics/` | required | `/opt/edt-lab`, `project:qa-mcp` | N/A | Low: reset behavior is not exercised until later cards |
| Delivery or runtime apply | Applying shell to `C:\1C_BASES\vanessa_client` | Operator-approved EDT update/apply plan | Runtime apply log or explicit not-run note | `.artifacts/openspec/add-client-fixture-v1-processor-shell/<run-id>/runtime-apply/` | required | `/opt/edt-lab`, `project:qa-mcp` | N/A | Medium: live apply may be deferred if operator does not request DB update |
| Report or DCS | Reports and DCS objects | N/A | N/A | N/A | N/A | `project:qa-mcp` | No report or DCS surface is changed | None |
