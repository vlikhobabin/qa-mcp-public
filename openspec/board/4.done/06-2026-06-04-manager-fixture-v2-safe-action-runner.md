# 06. TestManager Fixture Processor V2: Safe Action Runner

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Order Index
30

## Source
- 2026-06-04 planning session
- `docs/protocol-research/research-plan.md`
- TestManager fixture processor V1 card
- Client fixture processor V2 card
- V1 read-only manager fixture accepted/pending gap closed on 2026-06-06

## Summary
Extend the manager-side fixture processor/harness with an allowlisted safe
action runner. V2 should execute strictly documented non-business UI actions
against the client fixture, capture pre/post/recovery evidence and produce
clean candidate frame ranges for later protocol acceptance.
This card consumes the client fixture V2 target map and prepares action events
for the V2 tooling pipeline.

## Expected Scope
- Consume the client fixture V2 safe-action target map or manifest.
- Add an allowlisted safe action catalog with explicit `action_id`,
  `target_id`, target `PF_*` marker, expected pre-state, expected post-state
  and recovery contract.
- Implement manager commands for non-business UI actions only:
  activate existing window/form, set focus or activate a control, switch
  fixture pages, select a local table row, expand command group or popup/menu,
  and inspect resulting transient UI state.
- Wrap every action in a fixed sequence:
  pre-read, action-start, action-end, post-read, recovery/reset when needed,
  recovery-read.
- Record action event boundaries in `case_events.jsonl` so proxy frames can be
  grouped by `action_id`.
- Record `mutates_business_data=false` and a safety class for every action.
- Fail closed when an action target is missing, disabled unexpectedly, changes
  business data or cannot be reset.
- Keep recovery local to the fixture and label cleanup traffic separately from
  the candidate action frame range.
- Update capture/probe evidence so safe-action rows remain candidates until
  replay or direct Python-manager proof validates the normalized request and
  response shape.

## Out Of Scope
- Text input and value mutation.
- Button clicks that execute business commands.
- Object writes, posting, saving, data exchange or settings mutation.
- Dialog/error/retry recovery scenarios; those belong to a later manager V3/V4
  layer.
- Accepting action protocol mappings from one capture without repeatability or
  replay evidence.

## Acceptance
- Each safe action has before, action, after and recovery events in the manager
  log.
- The capture runner can isolate candidate frame ranges for every safe action
  from bootstrap, background refresh and cleanup traffic.
- The client fixture returns to a known baseline after each action case.
- No scenario writes business data or depends on external business state.
- Reviewed evidence marks rows as candidate or accepted according to the
  existing protocol evidence contract.

## Change Set
- `openspec/changes/archive/2026-06-07-define-manager-fixture-v2-safe-action-catalog/`
- `openspec/changes/archive/2026-06-07-implement-manager-fixture-v2-safe-action-runner/`
- `openspec/changes/archive/2026-06-07-record-manager-fixture-v2-safe-action-boundaries/`
- `openspec/changes/archive/2026-06-07-verify-manager-fixture-v2-safe-action-recovery/`
- `openspec/changes/archive/2026-06-07-publish-manager-fixture-v2-safe-action-candidate-evidence/`

## Verify
- `bin\openspec.cmd validate define-manager-fixture-v2-safe-action-catalog --strict`
- `bin\openspec.cmd validate implement-manager-fixture-v2-safe-action-runner --strict`
- `bin\openspec.cmd validate record-manager-fixture-v2-safe-action-boundaries --strict`
- `bin\openspec.cmd validate verify-manager-fixture-v2-safe-action-recovery --strict`
- `bin\openspec.cmd validate publish-manager-fixture-v2-safe-action-candidate-evidence --strict`
- `bin\openspec.cmd validate --all`
- `git diff --check -- openspec/changes/define-manager-fixture-v2-safe-action-catalog openspec/changes/implement-manager-fixture-v2-safe-action-runner openspec/changes/record-manager-fixture-v2-safe-action-boundaries openspec/changes/verify-manager-fixture-v2-safe-action-recovery openspec/changes/publish-manager-fixture-v2-safe-action-candidate-evidence openspec/board`

## Archive
- `openspec/changes/archive/2026-06-07-define-manager-fixture-v2-safe-action-catalog/`
- `openspec/changes/archive/2026-06-07-implement-manager-fixture-v2-safe-action-runner/`
- `openspec/changes/archive/2026-06-07-record-manager-fixture-v2-safe-action-boundaries/`
- `openspec/changes/archive/2026-06-07-verify-manager-fixture-v2-safe-action-recovery/`
- `openspec/changes/archive/2026-06-07-publish-manager-fixture-v2-safe-action-candidate-evidence/`

## Related
- `openspec/board/4.done/05-2026-06-04-manager-fixture-v1-readonly-runner.md`
- `openspec/board/4.done/02-2026-06-04-client-fixture-v2-safe-actions.md`
- `openspec/board/4.done/10-2026-06-07-v2-readiness-docs-and-safety-contract.md`
- `openspec/board/4.done/40-2026-06-07-v2-safe-action-tooling-pipeline.md`
- `openspec/board/4.done/50-2026-06-07-v2-first-focused-safe-action-proof.md`
- `openspec/changes/archive/2026-06-07-define-manager-fixture-v2-safe-action-catalog/`
- `openspec/changes/archive/2026-06-07-implement-manager-fixture-v2-safe-action-runner/`
- `openspec/changes/archive/2026-06-07-record-manager-fixture-v2-safe-action-boundaries/`
- `openspec/changes/archive/2026-06-07-verify-manager-fixture-v2-safe-action-recovery/`
- `openspec/changes/archive/2026-06-07-publish-manager-fixture-v2-safe-action-candidate-evidence/`
- `docs/protocol-research/safe-ui-action-scope.md`
- `docs/protocol-research/corpus-evidence-contract.md`
- `docs/protocol-research/protocol-corpus-runner.md`
- `docs/protocol-research/research-plan.md`

## Result
manager V2 safe-action catalog, fail-closed dry-run dispatcher, boundary
events, recovery contract evidence and compact candidate publication delivered
and archived; live action execution remains gated until a reviewed
manager/Vanessa proof is explicitly enabled

## Next
- use `openspec/board/4.done/50-2026-06-07-v2-first-focused-safe-action-proof.md`
  for the first accepted/candidate proof decision

## Change Plan Notes
Change order:
1. `define-manager-fixture-v2-safe-action-catalog`
2. `implement-manager-fixture-v2-safe-action-runner`
3. `record-manager-fixture-v2-safe-action-boundaries`
4. `verify-manager-fixture-v2-safe-action-recovery`
5. `publish-manager-fixture-v2-safe-action-candidate-evidence`

## Change 1: `define-manager-fixture-v2-safe-action-catalog`

### Why
The manager V2 runner needs a reviewed allowlist before it can execute any UI
action.

### Goal
Define a fail-closed manager-side safe-action catalog that consumes client V2
target markers and records pre-state, post-state and recovery expectations.

### Scope
- Define required catalog row fields.
- Link rows to client fixture target ids and `PF_*` markers.
- Reject incomplete, unsupported, mutating or non-allowlisted rows.

### Acceptance
- Executable rows include all V2 safety fields.
- Unsafe rows fail closed before manager execution.
- Unsupported rows remain visible with reason, owner and residual risk.

### Depends On
- none

### Related
- `openspec/changes/define-manager-fixture-v2-safe-action-catalog/`

### Notes For `$openspec-ff-change`
- Catalog validation permits candidate execution only; it does not accept a
  protocol mapping.

## Change 2: `implement-manager-fixture-v2-safe-action-runner`

### Why
The tooling can validate/report safe actions, but live proof remains gated
until the manager fixture can execute reviewed non-mutating actions.

### Goal
Implement manager-side runner commands for the V2 allowlisted action families.

### Scope
- Add a dispatcher behind catalog validation.
- Implement supported focus, activate, page switch, local row selection and
  safe expand/collapse action paths.
- Emit typed success/rejected/blocked/partial/timeout runner results.

### Acceptance
- Runner executes only validated non-mutating rows.
- Unsafe or unavailable targets fail closed.
- V1 read-only runner behavior remains stable.

### Depends On
- `define-manager-fixture-v2-safe-action-catalog`

### Related
- `openspec/changes/implement-manager-fixture-v2-safe-action-runner/`

### Notes For `$openspec-ff-change`
- Do not include text input, value toggles, business command clicks or V4
  dialog/error scenarios.

## Change 3: `record-manager-fixture-v2-safe-action-boundaries`

### Why
Safe-action proof needs action frame candidates separated from bootstrap,
background refresh and recovery traffic.

### Goal
Record phase-aware manager side-channel events for every V2 action attempt.

### Scope
- Emit `pre_read`, `action_start`, `action_end`, `post_read`, `recovery` and
  background events.
- Preserve action/background/recovery frame correlation fields.
- Keep ambiguous rows visible as candidate, partial, timeout, rejected or
  blocked.

### Acceptance
- `case_events.jsonl` identifies action id, target id, action family and result
  markers.
- Candidate action ranges are isolated from background/cleanup ranges.
- Boundary ambiguity is not promoted.

### Depends On
- `implement-manager-fixture-v2-safe-action-runner`

### Related
- `openspec/changes/record-manager-fixture-v2-safe-action-boundaries/`

### Notes For `$openspec-ff-change`
- Do not inject markers into TCP traffic; use side-channel event correlation.

## Change 4: `verify-manager-fixture-v2-safe-action-recovery`

### Why
Every V2 safe action must return the client fixture to a known baseline or a
documented known state.

### Goal
Verify recovery/reset behavior and rerun determinism for executable safe
actions.

### Scope
- Define recovery expectations per executable row.
- Retain recovery markers and recovery frame ranges separately.
- Mark rows non-accepted when recovery cannot be proved.

### Acceptance
- Post-recovery reads show baseline or known-state markers.
- The first supported subset can rerun after recovery.
- Cleanup traffic stays separate from candidate action evidence.

### Depends On
- `record-manager-fixture-v2-safe-action-boundaries`

### Related
- `openspec/changes/verify-manager-fixture-v2-safe-action-recovery/`

### Notes For `$openspec-ff-change`
- Recovery is fixture-local only; no business rollback or reposting.

## Change 5: `publish-manager-fixture-v2-safe-action-candidate-evidence`

### Why
The first focused V2 proof needs compact manager-runner evidence without raw
captures in reviewed git.

### Goal
Publish candidate safe-action evidence with explicit accepted/non-accepted
status and proof links.

### Scope
- Publish compact rows with action, background and recovery ranges separated.
- Record normalized hash fields, result markers and replay/probe or typed
  contract status where available.
- Update durable docs/evidence links for the focused proof handoff.

### Acceptance
- Candidate rows are not confused with accepted protocol knowledge.
- Accepted output excludes rows lacking replay/probe or typed contract proof.
- Raw captures and generated replay payloads stay under ignored runtime paths.

### Depends On
- `verify-manager-fixture-v2-safe-action-recovery`

### Related
- `openspec/changes/publish-manager-fixture-v2-safe-action-candidate-evidence/`

### Notes For `$openspec-ff-change`
- This card hands evidence to the first focused V2 safe-action proof; broad
  demo button pilots remain out of scope.

## Log
- 2026-06-04T16:47:33Z card created
- 2026-06-07T00:00:00Z order index updated to 30 and scope refreshed after V1 read-only gap closure
- 2026-06-07T00:00:00Z fast-forwarded into five OpenSpec changes and moved to
  `2.todo`
- 2026-06-07T17:36:33Z delivered and archived five OpenSpec changes; compact
  candidate evidence published with `accepted_count=0`
- 2026-06-07T17:44:45Z publish verification prepared for scoped commit and
  push; raw runtime and `.artifacts` evidence remain excluded
