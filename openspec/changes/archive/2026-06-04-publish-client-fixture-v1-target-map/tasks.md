## 1. Target Map

- [x] 1.1 Inspect the implemented V1 fixture form and list all stable `PF_*` targets.
- [x] 1.2 Create `docs/protocol-research/evidence/fixture-target-maps/<run-id>/target_map.json`.
- [x] 1.3 Create `docs/protocol-research/evidence/fixture-target-maps/<run-id>/target_map_summary.md`.
- [x] 1.4 Record target availability and provider gaps per element family.

## 2. Corpus Readiness

- [x] 2.1 Link V1 targets to read-only case ids or fixture manifest rows.
- [x] 2.2 Update corpus planning docs or manifest inputs without claiming accepted protocol mappings.
- [x] 2.3 Link compact read-only form analysis evidence or an explicit provider/runtime gap to the target map.

## 3. Verification

- [x] 3.1 Run read-only form analysis against the V1 fixture form and retain marker coverage evidence, or retain an explicit provider/runtime gap when the form is not applied to the infobase.
- [x] 3.2 Validate target-map JSON shape and summary links.
- [x] 3.3 Run `openspec validate publish-client-fixture-v1-target-map --strict`.
- [x] 3.4 Run `git diff --check -- openspec/changes/publish-client-fixture-v1-target-map docs/protocol-research`.

## Verification Results

- `target_map.json` parsed with 46 target rows and
  `accepted_protocol_mapping=false`.
- Required V1 markers were present in the target map:
  `PF_FORM_MAIN`, edit fields, checkboxes, choice, buttons, command bar,
  table, rows, label, groups and pages.
- `protocol-corpus-runner.md` now links the V1 target map as a corpus planning
  input while keeping historical fixture rows non-accepted.
- `evidence-index.md` now indexes the target-map evidence directory.
- Read-only TestClient/Vanessa form analysis is deferred because the fixture
  source was not applied to the infobase in this change. The target-map rows
  remain semantic/source targets with `availability=partial`.

## Verification Matrix

| Surface | Affected scope | Planning output | Required evidence | Artifact path | Status | Provider owner | N/A reason | Residual risk |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Managed form layout | V1 fixture form element targets | Target map with marker, family, target path and expected state | Read-only form tree or form-analysis marker coverage | `.artifacts/openspec/publish-client-fixture-v1-target-map/<run-id>/ui-analysis/`; `docs/protocol-research/evidence/fixture-target-maps/<run-id>/target_map_summary.md` | required | `/opt/vanessa-mcp-stack`, `/opt/edt-lab`, `project:qa-mcp` | N/A | Medium: provider tree may omit hidden or disabled variants |
| Metadata object | Fixture processor/form source metadata | Source-qualified semantic labels for target rows | EDT/meta source summary or provider-gap note | `docs/protocol-research/evidence/fixture-target-maps/<run-id>/target_map_summary.md` | required | `/opt/edt-lab`, `/opt/finshtab-1c` | N/A | Medium: source metadata is support only and cannot prove wire behavior |
| Delivery or runtime apply | Protocol capture and accepted mappings | N/A for target-map publication | N/A | N/A | N/A | `project:qa-mcp` | This change prepares capture inputs only; live capture/replay acceptance is a later change | Low: corpus acceptance remains deferred |
| BSL-only module edit | 1C source code | N/A | N/A | N/A | N/A | `project:qa-mcp` | Target-map publication should not change BSL behavior | Low: drift is mitigated by linking form-analysis evidence |
