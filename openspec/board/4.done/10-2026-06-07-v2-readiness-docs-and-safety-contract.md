# 10. V2 Readiness: Docs And Safety Contract

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Order Index
10

## Source
- 2026-06-07 V2 planning discussion
- `docs/protocol-research/status-report-2026-06-06.md`
- `docs/protocol-research/safe-ui-action-scope.md`
- Manager fixture V1 follow-up contract proofs

## Summary
Refresh the project documentation and agent instructions before V2 work starts.
The card makes the V2 safety boundary explicit: V2 may study only
non-mutating UI actions, while text input, command execution and business-data
mutation remain out of scope for later V3/V4 cards.

## Expected Scope
- Update stale top-level project status after V1 read-only pending rows were
  accepted by contract-backed evidence.
- Refresh `safe-ui-action-scope.md` after the V1 gap closure.
- Define the V2 safe-action manifest fields: `action_id`, `target_id`,
  `target_marker`, `pre_state`, `action`, `post_state`,
  `recovery_expectation`, `mutates_business_data=false`,
  `allowed_action_family` and `expected_action_result_markers`.
- Record allowed first action families: focus/activate existing element,
  activate existing window/form, switch fixture page, select local table row
  and expand/collapse menu or group without executing a command.
- Record excluded families: text input, checkbox/value toggle, business
  command click, object write, save, post, delete, fill, import, export or
  external side effect.
- Update local protocol research skills/instructions if they still imply that
  V2 can click or mutate real business state.

## Out Of Scope
- Editing the client fixture or manager harness.
- Running live 1C captures.
- Accepting any V2 safe-action protocol mapping.
- Designing V3 mutation rollback semantics.

## Acceptance
- Project docs state that V1 read-only no longer blocks V2.
- V2 safety boundary is explicit and fail-closed.
- The safe-action manifest contract is documented before implementation.
- Agent-facing instructions route clicks, input and writes outside V2 unless
  they are explicitly inert fixture-only actions.

## Change Set
- `openspec/changes/archive/2026-06-07-refresh-v2-readiness-docs/`
- `openspec/changes/archive/2026-06-07-define-v2-safe-action-manifest-contract/`
- `openspec/changes/archive/2026-06-07-align-agent-v2-safety-instructions/`

## Verify
- `bin\openspec.cmd validate refresh-v2-readiness-docs --strict`
- `bin\openspec.cmd validate define-v2-safe-action-manifest-contract --strict`
- `bin\openspec.cmd validate align-agent-v2-safety-instructions --strict`
- `bin\openspec.cmd validate qa-mcp-protocol-lab --strict`
- `bin\openspec.cmd validate --all`
- `git diff --check`
- `scripts\check.ps1 -SkipPytest`

## Archive
- `openspec/changes/archive/2026-06-07-refresh-v2-readiness-docs/`
- `openspec/changes/archive/2026-06-07-define-v2-safe-action-manifest-contract/`
- `openspec/changes/archive/2026-06-07-align-agent-v2-safety-instructions/`

## Related
- `docs/protocol-research/status-report-2026-06-06.md`
- `docs/protocol-research/safe-ui-action-scope.md`
- `docs/protocol-research/corpus-evidence-contract.md`
- `openspec/board/1.backlog/02-2026-06-04-client-fixture-v2-safe-actions.md`
- `openspec/board/1.backlog/06-2026-06-04-manager-fixture-v2-safe-action-runner.md`
- `openspec/changes/archive/2026-06-07-refresh-v2-readiness-docs/`
- `openspec/changes/archive/2026-06-07-define-v2-safe-action-manifest-contract/`
- `openspec/changes/archive/2026-06-07-align-agent-v2-safety-instructions/`

## Result
V2 readiness documentation now states that manager fixture V1 read-only no
longer blocks V2 planning, while preserving the caveat that typed manager
side-channel rows are not direct wire marker claims.

The safe-action scope and corpus evidence contract now define the V2
manifest-gated action boundary: every row needs target, pre/post state,
recovery, `mutates_business_data=false`, an allowlisted action family and
expected action result markers before capture or manager-runner execution.

`AGENTS.md` and the local protocol research skill now route broad clicks, text
input, value toggles, business commands, writes and external side effects out
of V2 and into later mutation/recovery cards.

## Next
- continue with downstream V2 fixture and manager safe-action cards after
  publish

## Publish
- Docs updated:
  `docs/protocol-research/status-report-2026-06-06.md`,
  `docs/protocol-research/safe-ui-action-scope.md`,
  `docs/protocol-research/corpus-evidence-contract.md`,
  `AGENTS.md`,
  `.codex/skills/1c-testclient-protocol-research/SKILL.md`,
  `openspec/specs/qa-mcp-protocol-lab/spec.md`.
- Delivery manifest:
  `.runtime/opsx/delivery-manifests/10-2026-06-07-v2-readiness-docs-and-safety-contract.json`.
- Commit and push: handled by `$opsx-pub` on `main`.

## Change 1: `refresh-v2-readiness-docs`

### Why
The 2026-06-06 status report still carried the older baseline pending-row
story in parts of its narrative, while later contract-backed proofs accepted
all former pending rows. V2 planning needed a single current readiness
statement before safe-action cards move.

### Goal
Make the project status and safe-action scope docs state that manager fixture
V1 read-only no longer blocks V2, while preserving the caveat that three rows
were accepted by typed manager side-channel contracts rather than direct wire
markers.

### Scope
- Refresh `docs/protocol-research/status-report-2026-06-06.md`.
- Refresh V1 prerequisite language in
  `docs/protocol-research/safe-ui-action-scope.md`.
- Keep compact evidence paths and raw-runtime boundaries intact.

### Acceptance
- V1 pending-row closure is stated as `unblocked_by_v1_readonly`.
- Side-channel accepted rows are not described as direct wire marker claims.
- Downstream V2 cards can cite the updated readiness state.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-06-07-refresh-v2-readiness-docs/`

### Notes For `$openspec-ff-change`
- This is documentation-only and should not start 1C runtime processes.

## Change 2: `define-v2-safe-action-manifest-contract`

### Why
The existing safe-action scope defined broad candidate rows, but V2 needed a
fail-closed manifest contract before fixture or manager runner work can consume
action rows.

### Goal
Define the V2 manifest fields, allowed first action families and excluded
mutation families in reviewed docs and OpenSpec requirements.

### Scope
- Extend `docs/protocol-research/safe-ui-action-scope.md`.
- Update `docs/protocol-research/corpus-evidence-contract.md` only where the
  safe-action row contract needs the new manifest fields.
- Require `mutates_business_data=false` and expected result markers for every
  V2 action row.

### Acceptance
- Required manifest fields are documented.
- Allowed first action families are explicitly allowlisted.
- Text input, checkbox/value toggles, business command clicks and external
  side effects fail closed and route to later V3/V4 work.

### Depends On
- `refresh-v2-readiness-docs`

### Related
- `openspec/changes/archive/2026-06-07-define-v2-safe-action-manifest-contract/`

### Notes For `$openspec-ff-change`
- Do not accept protocol mappings in this change; it defines the contract only.

## Change 3: `align-agent-v2-safety-instructions`

### Why
Agent-facing instructions said to prefer read-only operations until
write/action semantics are understood. V2 needed a sharper rule: safe actions
are allowed only when the documented manifest classifies them as inert,
fixture-local and non-mutating.

### Goal
Align AGENTS and local protocol research skills so clicks, text input, writes
and business commands are routed outside V2 unless they are explicitly covered
by the V2 safe-action manifest contract.

### Scope
- Update `AGENTS.md` safety language if needed.
- Update `.codex/skills/1c-testclient-protocol-research/SKILL.md`.
- Check other local routing skills only for statements that could broaden V2
  into mutating actions.

### Acceptance
- Agent instructions name the V2 allowlist and excluded families.
- UI action requests fail closed when they are not covered by the manifest.
- Mutating work is routed to later mutation/recovery cards, not V2.

### Depends On
- `define-v2-safe-action-manifest-contract`

### Related
- `openspec/changes/archive/2026-06-07-align-agent-v2-safety-instructions/`

### Notes For `$openspec-ff-change`
- Keep this scoped to local instructions in this repository.

## Log
- 2026-06-07T00:00:00Z card created
- 2026-06-07T07:31:22Z decomposed into three OpenSpec changes and moved to `2.todo`
- 2026-06-07T08:00:00Z archived `refresh-v2-readiness-docs`
- 2026-06-07T08:10:00Z archived `define-v2-safe-action-manifest-contract`
- 2026-06-07T08:20:00Z archived `align-agent-v2-safety-instructions`
- 2026-06-07T08:25:00Z moved card to `4.done`
- 2026-06-07T08:15:14Z publish notes added for scoped commit on `main`
