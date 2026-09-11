## 1. Handler Surface

- [x] 1.1 Add local mutation handlers for text, number, date and checkbox
  targets and route them through the shared state helper.
- [x] 1.2 Add inert button handling that only updates local action markers and
  counters.

## 2. Verification

- [x] 2.1 Retain Windows-native handler proof for text, number, date,
  checkbox and inert-button cases, including reset evidence after each case.
- [x] 2.2 Run `bin\openspec.cmd validate mutation-form-handlers --strict`.
- [x] 2.3 Run `git diff --check -- openspec/changes/mutation-form-handlers
  openspec/board`.

Runtime evidence retained under
`.artifacts/openspec/mutation-form-handlers/20260608-v3-surface/`. Text,
checkbox and inert-button handlers have live marker proof with reset evidence.
Follow-up EPF inspection showed that the original `PF_EDIT_NUMBER` and
`PF_EDIT_DATE` form elements had `TextEdit=false`, while manually-created
editable siblings did not. The EDT source was fixed with
`<textEdit>true</textEdit>` for both number/date `InputFieldExtInfo` entries,
and the live `vanessa_client` infobase was updated through a Designer
`LoadConfigFromFiles` partial load after `edt-mcp` was unavailable. Retest
evidence in
`.artifacts/openspec/mutation-form-handlers/20260608-v3-surface/runtime-handler-proof/direct-text-input-after-textedit-fix-run/`
confirms the normal Vanessa/TestClient text-input route:
`PF_EDIT_NUMBER=240,75` with `PF_LAST_ACTION=PF_EDIT_NUMBER`,
`PF_MUTATION_STATE=PF_MUTATION_CHANGED`,
`PF_MUTATION_TARGET=PF_EDIT_NUMBER`,
`PF_MUTATION_POST_STATE=PF_EDIT_NUMBER_POST`; and
`PF_EDIT_DATE=20.02.2026 11:45:00` with the corresponding date markers.
The final reset capture returns the fixture to baseline. VanessaExt and
clipboard/keyboard probes remain retained only as negative research evidence
and are not accepted as the normal delivery route.

## 3. Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Form module or command | Mutation input, checkbox and inert-button handlers | Local mutation interactions with fail-closed exclusions | BSL diagnostics; Vanessa click scenario; scenario log; form tree and active-window proof | `.artifacts/openspec/mutation-form-handlers/<run-id>/handler-proof/` | required | `project:qa-mcp`, `vanessa-mcp`, `/opt/edt-lab` | N/A | Medium: handler paths may differ between platform builds |
| Runtime apply | Fixture event handlers | Spec-driven action dispatch and marker updates | Windows-native smoke proof and OpenSpec strict validation | `openspec/changes/mutation-form-handlers/` | required | `project:qa-mcp` | N/A | Low: changes remain fixture-local and non-mutating |
