## 1. Control Attributes And Data

- [x] 1.1 Add deterministic local attributes for edit, checkbox, choice, table and state-marker values.
- [x] 1.2 Initialize all V1 control values from local fixture state on form creation.
- [x] 1.3 Populate `PF_TABLE_ITEMS` with stable rows `PF_ROW_001`, `PF_ROW_002` and `PF_ROW_003`.

## 2. Managed Form Layout

- [x] 2.1 Add edit field variants for string, number, date, read-only and disabled states.
- [x] 2.2 Add checkbox variants for true, false, read-only and disabled states.
- [x] 2.3 Add choice/radio-style, button, command bar, label, group and pages controls with unique `PF_*` markers.
- [x] 2.4 Ensure command and button controls are present for read-only inspection without requiring command execution.

## 3. Verification

- [x] 3.1 Run EDT/source validation for the changed form and form module.
- [x] 3.2 Run read-only TestClient or Vanessa form analysis and retain marker coverage evidence, or retain an explicit provider/runtime gap when the form is not applied to the infobase.
- [x] 3.3 Record unavailable or provider-dependent variants as explicit gaps instead of inferring coverage.
- [x] 3.4 Run `openspec validate add-client-fixture-v1-readonly-controls --strict`.
- [x] 3.5 Run `git diff --check -- openspec/changes/add-client-fixture-v1-readonly-controls`.

## Verification Results

- XML parse passed for the fixture form, fixture processor metadata,
  configuration metadata and subsystem metadata.
- Fixture form item ids are unique within form item nodes.
- Marker grep confirmed V1 edit, checkbox, choice, button, command bar, table,
  table row, label, group and page markers in the fixture source.
- BSL marker grep confirmed deterministic initialization for
  `protocol-fixture.v1`, `PF_CHOICE_B`, `PF_ROW_001`, `PF_ROW_002` and
  `PF_ROW_003`.
- Compact source evidence was retained at
  `docs/protocol-research/evidence/fixture-sources/20260604-client-fixture-v1-controls/control_surface_summary.md`.
- Read-only TestClient/Vanessa form analysis is deferred because the fixture
  source was not applied to the infobase in this change. The current OPSX run
  already recorded an `edt-mcp` binding validation timeout; no retrieve, DB
  update, hot deploy or runtime apply was performed.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | V1 fixture form controls for edit fields, checkbox, choice, button, command bar, table, label, group and pages | Control-family marker checklist and expected UI state | EDT validation; Vanessa/TestClient form tree; active-form proof; screenshot or fallback summary | `.artifacts/openspec/add-client-fixture-v1-readonly-controls/<run-id>/ui-smoke/`; `docs/protocol-research/evidence/fixture-sources/<run-id>/control_surface_summary.md` | required | `/opt/edt-lab`, `/opt/vanessa-mcp-stack`, `project:qa-mcp` | N/A | Medium: some controls may not be discoverable through current UI provider |
| BSL-only module edit | Form initialization routines for local fixture values | Deterministic local state setup | BSL diagnostics; runtime read-only proof of initialized markers | `.artifacts/openspec/add-client-fixture-v1-readonly-controls/<run-id>/bsl-diagnostics/` | required | `/opt/edt-lab`, `project:qa-mcp` | N/A | Low: initialization must avoid business-data dependencies |
| Form module or command | Button/command controls present but not action-accepted | Command controls documented as read-only targets only | BSL diagnostics; no click scenario required | `.artifacts/openspec/add-client-fixture-v1-readonly-controls/<run-id>/bsl-diagnostics/` | required | `/opt/edt-lab`, `/opt/vanessa-mcp-stack` | N/A | Medium: later action cards must not reuse V1 evidence as action proof |
| Delivery or runtime apply | Applying control surface to `C:\1C_BASES\vanessa_client` | Operator-approved EDT update/apply plan | Runtime apply log or explicit not-run note | `.artifacts/openspec/add-client-fixture-v1-readonly-controls/<run-id>/runtime-apply/` | required | `/opt/edt-lab`, `project:qa-mcp` | N/A | Medium: live apply may be deferred if operator does not request DB update |
| Document posting or register movement | Business data mutation | N/A | N/A | N/A | N/A | `project:qa-mcp` | V1 controls use local fixture state only and do not post documents or write registers | None |
