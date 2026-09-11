# 02. Client Fixture Processor V2: Safe Actions

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Order Index
20

## Source
- 2026-06-04 planning session
- `docs/protocol-research/client-fixture-processor-roadmap.md`
- V1 client fixture processor card
- V1 read-only manager fixture accepted/pending gap closed on 2026-06-06

## Summary
Extend the fixture processor with safe non-mutating UI action surfaces. V2
should make focus, activation, page switching, popup expansion and table-row
selection observable and resettable, while keeping business data untouched.
This card follows the V2 readiness/safety contract card and provides the
client-side surface consumed by the manager V2 safe-action runner.

## Expected Scope
- Preserve the V1 read-only markers and baseline behavior.
- Add handlers and state markers for focus or activation of selected fixture
  controls.
- Add page-switch markers for `PF_PAGE_A` and `PF_PAGE_B`.
- Add popup/menu expansion surfaces that do not execute business commands.
- Add local table selection markers, including selected row marker and action
  counter updates.
- Add pre-state and post-state fields for safe action corpus rows.
- Add local observable state markers such as `PF_LAST_ACTION`,
  `PF_ACTION_COUNTER`, `PF_SELECTED_PAGE`, `PF_SELECTED_ROW` and
  `PF_FOCUSED_ELEMENT` where the final design needs them.
- Keep `PF_RESET_STATE` able to return the form to the V1 baseline.
- Document which controls are safe-action targets and which remain read-only
  only.

## Out Of Scope
- Business command execution.
- Text input or value mutation acceptance.
- Writes to catalogs, documents, registers or settings storage.
- Treating safe-action capture as accepted protocol knowledge without replay
  or direct Python-manager proof.

## Acceptance
- Safe actions affect only local fixture state.
- Each safe action has unique before/after `PF_*` markers.
- The form can be reset after every safe action.
- TestClient capture can isolate action candidate ranges from background
  refresh traffic.
- No V2 scenario requires business-data mutation or manual cleanup.

## Change Set
- `openspec/changes/archive/2026-06-07-add-client-fixture-v2-safe-action-state-model/`
- `openspec/changes/archive/2026-06-07-add-client-fixture-v2-safe-action-form-handlers/`
- `openspec/changes/archive/2026-06-07-publish-client-fixture-v2-safe-action-manifest-updates/`
- `openspec/changes/archive/2026-06-07-verify-client-fixture-v2-safe-action-recovery/`

## Verify
- `bin\openspec.cmd validate add-client-fixture-v2-safe-action-state-model --strict`
- `bin\openspec.cmd validate add-client-fixture-v2-safe-action-form-handlers --strict`
- `bin\openspec.cmd validate publish-client-fixture-v2-safe-action-manifest-updates --strict`
- `bin\openspec.cmd validate verify-client-fixture-v2-safe-action-recovery --strict`
- `bin\openspec.cmd validate --all`
- `git diff --check -- openspec/changes openspec/board`

## Archive
- `openspec/changes/archive/2026-06-07-add-client-fixture-v2-safe-action-state-model/`
- `openspec/changes/archive/2026-06-07-add-client-fixture-v2-safe-action-form-handlers/`
- `openspec/changes/archive/2026-06-07-publish-client-fixture-v2-safe-action-manifest-updates/`
- `openspec/changes/archive/2026-06-07-verify-client-fixture-v2-safe-action-recovery/`

## Related
- `docs/protocol-research/client-fixture-processor-roadmap.md`
- `openspec/board/4.done/01-2026-06-04-client-fixture-v1-control-surface.md`
- `openspec/board/1.backlog/10-2026-06-07-v2-readiness-docs-and-safety-contract.md`
- `openspec/board/1.backlog/06-2026-06-04-manager-fixture-v2-safe-action-runner.md`

## Result
published and committed

## Next
- none

## Change Plan Notes
When this card moved to `2.todo/`, the change order was:
1. state model
2. form handlers
3. capture manifest updates
4. recovery verification

## Related
- `origin/main`

## Log
- 2026-06-04T12:04:00Z card created
- 2026-06-07T00:00:00Z order index updated to 20 and scope refreshed after V1 read-only gap closure
- 2026-06-07T00:00:00Z decomposed into four OpenSpec changes and moved to `2.todo`
- 2026-06-07T10:05:44Z archived four OpenSpec changes and moved to `4.done`
- 2026-06-07T10:30:00Z published and committed
