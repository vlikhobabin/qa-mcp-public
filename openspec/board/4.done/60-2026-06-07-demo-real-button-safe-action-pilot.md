# 60. Demo Real Button Safe-Action Pilot

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Order Index
60

## Source
- 2026-06-07 V2 planning discussion
- V2 first focused safe-action proof card
- Demo configuration runtime goal

## Summary
After fixture V2 safe-action evidence exists, classify and attempt one real
third-party-configuration button only if it is safe under the V2 contract. The pilot
should either publish a safe-action candidate/accepted proof or explicitly
route the button to V3 mutation work.

## Expected Scope
- Choose one concrete button in a demo configuration form.
- Classify the button as safe UI action, inert local action or business
  mutation before any click is attempted.
- Record target path, visible caption or marker, pre-state, expected post-state
  and recovery expectation.
- Run only if `mutates_business_data=false` can be justified.
- Publish compact candidate or accepted evidence if the action is safe.
- Route the case to V3 if it writes data, executes a business command or needs
  rollback.

## Out Of Scope
- Clicking unknown business buttons.
- Save, post, fill, import, export, exchange, delete or other business
  commands.
- Treating visual success as accepted protocol evidence without frame and
  replay/probe or typed contract support.
- Generalizing one demo button to all button actions.

## Acceptance
- The selected button has a recorded safety classification.
- Unsafe or mutating behavior is rejected before execution and routed to V3.
- Safe behavior, if attempted, has compact evidence with pre/action/post and
  recovery status.
- The result states whether the pilot produced accepted evidence, candidate
  evidence or a V3 blocker.

## Change Set
- `openspec/changes/archive/2026-06-10-select-demo-safe-button-target/`
- `openspec/changes/archive/2026-06-10-classify-demo-button-safety-contract/`
- `openspec/changes/archive/2026-06-10-capture-demo-button-safe-action-pilot/`
- `openspec/changes/archive/2026-06-10-publish-demo-button-safe-action-decision/`

## Verify
- `bin\openspec.cmd validate select-demo-safe-button-target --strict`
- `bin\openspec.cmd validate classify-demo-button-safety-contract --strict`
- `bin\openspec.cmd validate capture-demo-button-safe-action-pilot --strict`
- `bin\openspec.cmd validate publish-demo-button-safe-action-decision --strict`
- `bin\openspec.cmd validate qa-mcp-protocol-lab --strict`
- `bin\openspec.cmd validate --all`
- `git diff --check -- openspec/changes/publish-demo-button-safe-action-decision docs/protocol-research openspec/board`
- `git diff --check`

## Archive
- `openspec/changes/archive/2026-06-10-select-demo-safe-button-target/`
- `openspec/changes/archive/2026-06-10-classify-demo-button-safety-contract/`
- `openspec/changes/archive/2026-06-10-capture-demo-button-safe-action-pilot/`
- `openspec/changes/archive/2026-06-10-publish-demo-button-safe-action-decision/`

## Related
- `openspec/board/4.done/50-2026-06-07-v2-first-focused-safe-action-proof.md`
- `openspec/board/4.done/03-2026-06-04-client-fixture-v3-mutation-sandbox-surface.md`
- `openspec/board/4.done/70-2026-06-08-client-fixture-v3-mutation-evidence-promotion.md`
- `docs/protocol-research/safe-ui-action-scope.md`
- `docs/protocol-research/evidence/demo-button-safe-action/20260610-demo-button-blocked-publication/`
- `docs/protocol-research/evidence/accepted-mappings/demo-button-safe-action-20260610/`
- `docs/protocol-research/evidence-index.md`

## Result
completed: the pilot selected target
`demo10413-operation-goods-toggle-activity` from the demo10413 source, then
classified it as `business_mutation` before execution. The guarded capture was
blocked before any click, no raw capture was created, accepted mappings remain
empty, and the final publication status is `routed_to_v3`.

Provider note: `vanessa-mcp` had no connected TestClient during the run, so the
runtime UI path was recorded as a provider gap and no live UI action was
performed.

## Next
- none

## Change Plan Notes
Change order:
1. `select-demo-safe-button-target`
2. `classify-demo-button-safety-contract`
3. `capture-demo-button-safe-action-pilot`
4. `publish-demo-button-safe-action-decision`

## Change 1: `select-demo-safe-button-target`

### Why
The pilot needs one concrete demo target before safety classification can be
meaningful.

### Goal
Select one visible demo configuration button-like target using read-only
evidence and record enough target context for classification.

### Outcome
Selected `demo10413-operation-goods-toggle-activity` from source-only evidence.
The selection step did not click the target.

### Related
- `openspec/changes/archive/2026-06-10-select-demo-safe-button-target/`

## Change 2: `classify-demo-button-safety-contract`

### Why
A real demo button must be proven non-mutating before any click is attempted.

### Goal
Classify the selected target as safe UI action, inert local action, business
mutation, unsupported or blocked and produce either a complete manifest row or
a fail-closed routing decision.

### Outcome
Classified the selected target as `business_mutation`, marked it not capture
eligible for V2 and routed it to V3 or later mutation/recovery work.

### Related
- `openspec/changes/archive/2026-06-10-classify-demo-button-safety-contract/`

## Change 3: `capture-demo-button-safe-action-pilot`

### Why
Only a reviewed safe row may be attempted live, and the pilot must preserve
phase evidence or a blocked result.

### Goal
Run zero or one guarded demo-button action, retaining pre/action/post/recovery
evidence when safe and a blocked summary when not safe.

### Outcome
Recorded a blocked no-click capture result because classification found a
business mutation. Runtime click attempted: `false`. Raw capture created:
`false`.

### Related
- `openspec/changes/archive/2026-06-10-capture-demo-button-safe-action-pilot/`

## Change 4: `publish-demo-button-safe-action-decision`

### Why
The pilot must publish whether it produced accepted evidence, candidate
evidence, a rejection, a blocked result or a V3 mutation route.

### Goal
Publish compact final evidence and update docs/indexes without overclaiming
accepted protocol knowledge.

### Outcome
Published compact evidence, updated the evidence index, emitted an empty
accepted-mapping output for this run and recorded final status `routed_to_v3`.

### Related
- `openspec/changes/archive/2026-06-10-publish-demo-button-safe-action-decision/`

## Log
- 2026-06-07T00:00:00Z card created
- 2026-06-10T04:46:25Z fast-forwarded into four OpenSpec changes and moved to
  `2.todo`
- 2026-06-10T06:16:11Z archived all four OpenSpec changes and moved card to
  `4.done`
- 2026-06-10T06:56:45Z prepared final publish scope for commit and push
