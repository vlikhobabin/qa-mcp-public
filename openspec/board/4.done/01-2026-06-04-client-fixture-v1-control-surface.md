# 01. Client Fixture Processor V1: Control Surface

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Order Index
01

## Source
- 2026-06-04 planning session
- `docs/protocol-research/client-fixture-processor-roadmap.md`
- `docs/protocol-research/api-corpus-roadmap-2026-06-03.md`

## Summary
Create the first version of the client fixture processor in `vanessa_client`.
V1 should provide a broad, stable read-only/control surface for protocol
capture: many control families, unique `PF_*` markers and deterministic local
state, without accepting action or mutation protocol semantics yet.

## Expected Scope
- Add a dedicated client fixture processor/form in the `client` EDT target.
- Add form-level markers: `PF_FORM_MAIN`, `PF_FIXTURE_VERSION`,
  `protocol-fixture.v1`.
- Add `EditField` variants for string, number, date, read-only and disabled
  states.
- Add `CheckBox` variants for checked, unchecked, read-only and disabled
  states.
- Add a radio/choice-style control with stable values.
- Add enabled, disabled, default and inert button variants.
- Add a command bar with an enabled command, disabled command and popup/group.
- Add a local table with 2-3 stable `PF_ROW_*` rows and typed columns.
- Add label/decoration, group and pages/tab controls with unique markers.
- Add local state fields such as `PF_LAST_ACTION`, `PF_ACTION_COUNTER` and
  `PF_SELECTED_ROW_MARKER`.
- Add a reset command hook for later versions, without requiring V1 corpus
  acceptance for the reset action.
- Produce or update a target path map for every `PF_*` fixture element.

## Out Of Scope
- Text input acceptance.
- Button click acceptance.
- Page-switch action acceptance.
- Business object writes.
- TCP parsing or protocol decoding inside 1C.

## Acceptance
- Source authoring is completed in the `vanessa_client` EDT project.
- No retrieve, DB update or hot deploy is performed unless
  `validate_project_infobase_binding(target_id="client")` returns cleanly in a
  bounded follow-up run.
- TestClient form-open and read-only form analysis are deferred until the
  fixture source is applied to the infobase.
- The fixture source has a reviewed target path map.
- No business-data mutation is required to initialize or inspect V1.

## Change Set
- `openspec/changes/archive/2026-06-04-add-client-fixture-v1-processor-shell/`
- `openspec/changes/archive/2026-06-04-add-client-fixture-v1-readonly-controls/`
- `openspec/changes/archive/2026-06-04-publish-client-fixture-v1-target-map/`

## Verify
- `openspec validate add-client-fixture-v1-processor-shell --strict`
- `openspec validate add-client-fixture-v1-readonly-controls --strict`
- `openspec validate publish-client-fixture-v1-target-map --strict`
- `openspec validate qa-mcp-protocol-lab --strict`
- `openspec validate --all`
- `git diff --check` for OpenSpec and reviewed docs/evidence paths
- XML parse checks for the authored fixture form and related metadata
- target-map JSON parse check

## Archive
- `openspec/changes/archive/2026-06-04-add-client-fixture-v1-processor-shell/`
- `openspec/changes/archive/2026-06-04-add-client-fixture-v1-readonly-controls/`
- `openspec/changes/archive/2026-06-04-publish-client-fixture-v1-target-map/`

## Related
- `docs/protocol-research/client-fixture-processor-roadmap.md`
- `docs/protocol-research/evidence/fixture-sources/20260604-client-fixture-v1-shell/source_summary.md`
- `docs/protocol-research/evidence/fixture-sources/20260604-client-fixture-v1-controls/control_surface_summary.md`
- `docs/protocol-research/evidence/fixture-target-maps/20260604-client-fixture-v1-target-map/target_map_summary.md`
- `docs/protocol-research/evidence/fixture-target-maps/20260604-client-fixture-v1-target-map/target_map.json`
- `openspec/changes/archive/2026-06-04-add-client-fixture-v1-processor-shell/`
- `openspec/changes/archive/2026-06-04-add-client-fixture-v1-readonly-controls/`
- `openspec/changes/archive/2026-06-04-publish-client-fixture-v1-target-map/`

## Result
V1 client fixture source was authored in the external `vanessa_client` EDT
project with a dedicated processor/form, broad read-only control families,
deterministic `PF_*` local state and a reviewed 46-row target map.

The result is source-ready and corpus-planning-ready, not runtime-applied and
not protocol-accepted. `validate_project_infobase_binding(target_id="client")`
timed out during this OPSX run, so retrieve, DB update, hot deploy, live
TestClient form-open and Vanessa form-tree proof remain deferred.

## Next
- resolve the bounded EDT binding validation timeout before runtime apply,
  TestClient form-open proof or V2 fixture action work

## Publish
- Docs updated:
  `docs/protocol-research/protocol-corpus-runner.md`,
  `docs/protocol-research/evidence-index.md`.
- Delivery manifest:
  `.runtime/opsx/delivery-manifests/01-2026-06-04-client-fixture-v1-control-surface.json`.
- Commit: publish commits on `origin/main`.
- Push: pushed to `origin/main`.

## Change Plan Notes
## Change 1: `add-client-fixture-v1-processor-shell`

### Why
The V1 fixture needs a target-bound processor/form shell before broad control
families are added.

### Goal
Create the dedicated client fixture processor shell with top-level markers,
local state attributes and a reset command hook.

### Scope
- Data processor metadata and default managed form in the `client` EDT target.
- Markers `PF_FORM_MAIN`, `PF_FIXTURE_VERSION` and `protocol-fixture.v1`.
- Local state fields `PF_LAST_ACTION`, `PF_ACTION_COUNTER` and
  `PF_SELECTED_ROW_MARKER`.
- Form-open and EDT validation planning evidence.

### Acceptance
- Fixture shell opens in TestClient.
- Top-level markers are visible through read-only inspection.
- No business data mutation is required.

### Depends On
- none

### Related
- `openspec/changes/add-client-fixture-v1-processor-shell/`

### Notes For `$openspec-ff-change`
- Preserve read-only acceptance boundaries; reset is a future hook, not an
  accepted action in this change.

## Change 2: `add-client-fixture-v1-readonly-controls`

### Why
The fixture must expose the main form element families up front so protocol
research is not blocked by missing controls in every later corpus run.

### Goal
Populate the V1 fixture form with deterministic `PF_*` read-only control
families and local values.

### Scope
- Edit fields, checkboxes, choice/radio-style control, buttons, command bar,
  table, label, group and pages.
- Enabled, disabled and read-only variants where safe.
- Local table rows and deterministic initialization.
- Read-only marker coverage evidence.

### Acceptance
- Read-only form analysis sees the expected `PF_*` control families.
- Fixture values do not depend on business data.
- Control existence is not treated as action/mutation protocol acceptance.

### Depends On
- `add-client-fixture-v1-processor-shell`

### Related
- `openspec/changes/add-client-fixture-v1-readonly-controls/`

### Notes For `$openspec-ff-change`
- Keep clicks, input and page-switching out of V1 acceptance.

## Change 3: `publish-client-fixture-v1-target-map`

### Why
Protocol captures need a compact target map that links fixture elements to
case ids and expected markers before corpus runs can classify frame ranges.

### Goal
Publish the reviewed V1 target map and corpus readiness evidence for fixture
controls.

### Scope
- Machine-readable target map JSON and Markdown summary.
- Element family, target path, expected state, response markers and planned
  case ids for each supported `PF_*` target.
- Explicit gap rows for missing or provider-dependent targets.
- Corpus manifest/readiness updates without accepted mapping promotion.

### Acceptance
- Target map links implemented `PF_*` elements to read-only corpus intent.
- Semantic sources are marked as support, not wire proof.
- No corpus row is accepted without frame range, normalized hash and
  replay/probe evidence.

### Depends On
- `add-client-fixture-v1-processor-shell`
- `add-client-fixture-v1-readonly-controls`

### Related
- `openspec/changes/publish-client-fixture-v1-target-map/`

### Notes For `$openspec-ff-change`
- Store raw UI/runtime output under ignored `.artifacts/` or `runtime/`; keep
  only compact reviewed target-map evidence in git.

## Log
- 2026-06-04T12:04:00Z card created
- 2026-06-04T12:12:29Z decomposed into three OpenSpec changes and moved to `2.todo`
- 2026-06-04T13:20:00Z archived `add-client-fixture-v1-processor-shell`
- 2026-06-04T13:45:00Z archived `add-client-fixture-v1-readonly-controls`
- 2026-06-04T14:05:00Z archived `publish-client-fixture-v1-target-map`
- 2026-06-04T14:10:00Z moved card to `4.done`
- 2026-06-04T14:20:00Z publish docs reviewed and final scoped verification started
- 2026-06-04T14:25:00Z publish commit created
- 2026-06-04T14:30:00Z pushed publish commits to `origin/main`
