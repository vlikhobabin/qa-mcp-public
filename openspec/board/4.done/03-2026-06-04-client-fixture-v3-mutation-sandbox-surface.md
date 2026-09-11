# 03A. Client Fixture Processor V3: Mutation Sandbox Surface

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Order Index
70

## Source
- 2026-06-04 planning session
- `docs/protocol-research/client-fixture-processor-roadmap.md`
- V1/V2 client fixture processor cards
- V2 safe-action readiness and manifest contract updates
- 2026-06-08 card split from the broader V3 mutation sandbox plan

## Summary
Build the fixture-local V3 mutation sandbox surface without making protocol
acceptance claims. This card prepares deterministic local state, editable
targets, checkbox toggles, inert button handlers and reset markers so later
evidence work can study mutation frames without touching business data or
weakening the V2 allowlist.

## Expected Scope
- Add editable string, number and date mutation targets with stable initial
  values and expected mutated values.
- Add checkbox toggle scenarios with explicit before/after markers.
- Add inert button commands that only update `PF_LAST_ACTION` and counters.
- Add command handlers that change local fixture attributes only, with no
  business-data writes or external side effects.
- Strengthen `PF_RESET_STATE` so every mutation scenario can be rolled back to
  the V1 baseline and replayed deterministically.
- Add fixture-visible result markers for every local mutation target, including
  baseline and reset markers needed by later evidence work.
- Record the target marker names and expected local state transitions needed by
  the follow-up evidence/promotion card.

## Change Set
- `openspec/changes/archive/2026-06-09-mutation-state-model/`
- `openspec/changes/archive/2026-06-09-mutation-form-handlers/`

## Out Of Scope
- Creating, editing or posting documents.
- Writing catalogs, registers, settings storage or external files.
- Network, COM, HTTP, mail, crypto or filesystem side effects.
- Reusing the V2 safe-action allowlist as a shortcut for mutation scenarios.
- Capturing, publishing or promoting mutation protocol frame mappings.
- Final mutation manifest publication and corpus evidence promotion.

## Acceptance
- Every mutation modifies only local fixture state.
- Every fixture-local mutation target has deterministic pre-state, post-state
  and reset markers.
- Re-running the same local mutation case after reset produces the same
  observable markers.
- No V3 scenario depends on current demo business data.
- The card can reference reviewed V2 safe-action evidence without assuming V3
  mutation acceptance from it.
- The follow-up evidence card has enough marker names and expected state
  transitions to define fail-closed mutation rows.

## Delivery Gate
- This card may run before mutation protocol acceptance because it is scoped to
  fixture-local state and handlers only.
- Stop before capture publication, protocol mapping acceptance or corpus
  promotion. Those belong to the follow-up evidence/promotion card.

## Verify
- `bin\openspec.cmd validate mutation-state-model --strict` passed
- `bin\openspec.cmd validate mutation-form-handlers --strict` passed
- `bin\openspec.cmd validate --all` passed
- `git diff --check -- openspec/changes/mutation-state-model openspec/changes/mutation-form-handlers openspec/board docs\protocol-research\client-fixture-processor-roadmap.md` passed with CRLF warnings only
- external EDT `Form.form` XML parse passed
- scoped BSL parse/problem evidence retained for the fixture module; full EDT
  document-issues phase timed out
- EDT direct `deploy_infobase` applied the external V3 fixture source to the
  live `vanessa_client` infobase after the probe/classify routes hit provider
  gaps
- Windows-native live open/reset proof retained under
  `.artifacts/openspec/mutation-state-model/20260608-v3-surface/runtime-reset-proof/`
  and
  `runtime/protocol-research/captures/20260608-v3-surface-open-fixture-after-deploy/`
- Vanessa handler proof retained for committed text input, both checkbox
  toggles and the inert button under
  `.artifacts/openspec/mutation-form-handlers/20260608-v3-surface/runtime-handler-proof/`
- initial number/date handler proof found a fixture metadata cause: in the
  operator-saved
  `C:\1C_BASES\vanessa_client\ФикстураПротоколаTestClient.epf`, the original
  `PF_EDIT_NUMBER` and `PF_EDIT_DATE` input fields have `TextEdit=false`, while
  manually-created editable siblings `PF_EDIT_NUMBER_2` and `PF_EDIT_DATE_2`
  do not; in EDT source this maps to the missing `<textEdit>true</textEdit>`
  flag under the number/date `InputFieldExtInfo`
- after fixing the EDT form source and applying the live fixture through a
  Designer `LoadConfigFromFiles` partial load, the normal Vanessa/TestClient
  route `И в поле с именем ... я ввожу текст ...` works for number/date:
  `PF_EDIT_NUMBER=240,75`, `PF_LAST_ACTION=PF_EDIT_NUMBER`,
  `PF_MUTATION_STATE=PF_MUTATION_CHANGED`,
  `PF_MUTATION_TARGET=PF_EDIT_NUMBER`,
  `PF_MUTATION_POST_STATE=PF_EDIT_NUMBER_POST`; and
  `PF_EDIT_DATE=20.02.2026 11:45:00`, `PF_LAST_ACTION=PF_EDIT_DATE`,
  `PF_MUTATION_TARGET=PF_EDIT_DATE`,
  `PF_MUTATION_POST_STATE=PF_EDIT_DATE_POST`
- direct number/date evidence retained under
  `.artifacts/openspec/mutation-form-handlers/20260608-v3-surface/runtime-handler-proof/direct-text-input-after-textedit-fix-run/`
- the VanessaExt route is retained as negative workaround evidence: with
  `useaddin=true` and `emulatekeyboardinputwithVanessaExt=true`, the VA steps
  returned success but form analysis stayed at baseline
- ad-hoc clipboard/keyboard probes are rejected for normal delivery: they can
  interfere with operator work and are not the same route as VA's own
  VanessaExt text-emulation branch

## Archive
- `mutation-state-model` archived to
  `openspec/changes/archive/2026-06-09-mutation-state-model/`
- `mutation-form-handlers` archived to
  `openspec/changes/archive/2026-06-09-mutation-form-handlers/`
- Main `qa-mcp-protocol-lab` spec was synced with the V3 fixture-local
  mutation state and handler requirements before archive.

## Related
- `docs/protocol-research/client-fixture-processor-roadmap.md`
- `openspec/board/4.done/01-2026-06-04-client-fixture-v1-control-surface.md`
- `openspec/board/4.done/02-2026-06-04-client-fixture-v2-safe-actions.md`
- `openspec/board/4.done/10-2026-06-07-v2-readiness-docs-and-safety-contract.md`
- `openspec/board/4.done/40-2026-06-07-v2-safe-action-tooling-pipeline.md`
- `openspec/board/4.done/50-2026-06-07-v2-first-focused-safe-action-proof.md`
- `openspec/board/1.backlog/70-2026-06-08-client-fixture-v3-mutation-evidence-promotion.md`
- `openspec/changes/archive/2026-06-09-mutation-state-model/`
- `openspec/changes/archive/2026-06-09-mutation-form-handlers/`
- `docs/protocol-research/safe-ui-action-scope.md`
- `docs/protocol-research/corpus-evidence-contract.md`

## Result
Fixture-local V3 source surface was implemented in the external
`vanessa_client` EDT source tree. The form now exposes V3 mutation markers, and
text, number, date, checkbox and inert-button handlers route through the shared
local mutation helper.

This surface card is archived but not protocol-accepted. The current `qa-mcp`
git repository does not own the external EDT source files. Live open/reset
proof and text/number/date/checkbox/inert handler proof are retained.
Number/date became available through the normal Vanessa/TestClient text-input
route after the fixture field metadata was fixed (`TextEdit=false` removed in
the live platform XML / `<textEdit>true</textEdit>` in EDT source) and the live
`vanessa_client` infobase was updated. The VA-owned VanessaExt text-emulation
path remains negative workaround evidence because it reported successful input
steps while the form stayed at baseline. Ad-hoc clipboard fallback is
intentionally not accepted as a route.

## Next
- continue with the follow-up evidence/promotion card only after publishing
  this surface card:
  `openspec/board/1.backlog/70-2026-06-08-client-fixture-v3-mutation-evidence-promotion.md`

## Change Plan Notes
Change order:
1. `mutation-state-model`
2. `mutation-form-handlers`

## Change 1: `mutation-state-model`

### Why
V3 needs a deterministic local state model before handlers or evidence can be
trusted.

### Goal
Expose fixture-local baseline, editable, checkbox, inert-action and reset
markers without introducing business persistence.

### Scope
- Add the local mutation state record.
- Add baseline and expected mutated values.
- Add shared marker update and reset helpers.

### Acceptance
- Opening and resetting the fixture returns the same observable marker set.
- State remains transient and fixture-local.

### Depends On
- V1 control surface and V2 safe-action boundary.

### Related
- `openspec/changes/mutation-state-model/`

## Change 2: `mutation-form-handlers`

### Why
The state model needs controlled local handlers to generate observable sandbox
mutations.

### Goal
Route text, number, date, checkbox and inert-button interactions through the
shared fixture-local state helper.

### Scope
- Add local editable-value handlers.
- Add checkbox toggle handling.
- Add inert button marker/counter handling.
- Fail closed for unsupported targets and business-command paths.

### Acceptance
- Every supported handler updates only local markers.
- Reset after each handler returns the fixture to baseline.

### Depends On
- `mutation-state-model`

### Related
- `openspec/changes/mutation-form-handlers/`

## Log
- 2026-06-04T12:04:00Z card created
- 2026-06-07T00:00:00Z order index updated to 70 after the V2 safe-action proof and demo pilot cards
- 2026-06-07T00:00:00Z refreshed after V2 readiness and safe-action contract updates
- 2026-06-07T00:00:00Z fast-forwarded into four OpenSpec changes and moved to `2.todo`
- 2026-06-07T00:00:00Z reviewed artifacts and added explicit V2 tooling/proof delivery gate
- 2026-06-08T00:00:00Z split fixture-local surface delivery from mutation evidence/promotion
- 2026-06-08T05:55:00Z partial implementation completed in external EDT source; stopped before archive because runtime evidence tasks remain open
- 2026-06-08T08:10:00Z runtime open/reset and text/checkbox/inert handler proof retained; stopped before archive on the number/date handler action-route gap
- 2026-06-08T08:20:00Z confirmed `УвеличитьЗначение` also fails for number/date controls and retained final reset evidence
- 2026-06-08T11:35:00Z rejected clipboard/keyboard probing as a normal
  number/date route because it depends on the real OS foreground window and can
  interfere with operator work
- 2026-06-08T11:50:00Z found the VA-owned VanessaExt text-emulation candidate
  route (`useaddin=true` plus `emulatekeyboardinputwithVanessaExt=true`);
  runtime proof was deferred until an operator-approved clean desktop session
- 2026-06-08T12:20:00Z tested the VA-owned VanessaExt text-emulation route in
  a coordinated clean desktop session with explicit WinAPI focus on the
  TestClient OS window; VA steps reported success, but number/date fields and
  mutation markers stayed at baseline, so the route was retained as negative
  evidence rather than accepted as working proof
- 2026-06-08T16:35:00Z dumped the operator-saved EPF and found
  `TextEdit=false` on the original `PF_EDIT_NUMBER` and `PF_EDIT_DATE` input
  fields while manually-created editable `PF_EDIT_NUMBER_2` and
  `PF_EDIT_DATE_2` siblings do not carry that setting; next proof should fix
  the EDT `textEdit` flag and retest number/date before blaming the route
- 2026-06-08T19:30:00Z fixed EDT `textEdit` for `PF_EDIT_NUMBER` and
  `PF_EDIT_DATE`, applied the live fixture through a Designer partial
  `LoadConfigFromFiles` update after `edt-mcp` stayed unavailable, and
  confirmed the normal Vanessa/TestClient text-input route for number/date
  with reset evidence
- 2026-06-09T00:00:00Z synced the V3 fixture-local mutation state and handler
  requirements into the main `qa-mcp-protocol-lab` spec, archived
  `mutation-state-model` and `mutation-form-handlers`, and moved the surface
  card to `4.done`
