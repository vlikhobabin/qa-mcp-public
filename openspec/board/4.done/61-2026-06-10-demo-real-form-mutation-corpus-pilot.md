# 61. Demo Real Form Mutation Corpus Pilot

## Status
4.done

## Owner
unassigned

## OpenSpec Stage
archived

## Order Index
61

## Source
- 2026-06-10 discussion after card 60
- `openspec/board/4.done/60-2026-06-07-demo-real-button-safe-action-pilot.md`
- Demo10413 runtime goal: test real configuration forms, documents,
  processors and catalogs

## Summary
Start a controlled mutation/recovery corpus on existing demo10413 forms. Unlike
V2 safe-action work, this card explicitly permits business-data mutations in
the disposable test demo configuration, provided every operation is reviewed,
manifest-driven, observable and recoverable.

The goal is to move from fixture-local mutation proof to real configuration UI
workflows while preserving protocol evidence quality: target selection,
pre-state, action, post-state, cleanup/recovery, frame isolation and explicit
candidate/accepted/rejected status.

## Expected Scope
- Select a small first row set from real demo10413 forms, preferably one
  document form action from card 60 and one or two low-blast-radius catalog or
  processing form actions.
- Treat `mutates_business_data=true` as allowed for this card when the row has
  an explicit recovery or cleanup plan.
- Require a machine-readable manifest row for every attempted action with
  `target_id`, object/form path, element path, operation family, pre-state,
  action, expected post-state, recovery expectation and residual risk.
- Use unique test markers or object naming such as `QA_MCP_*` where new data is
  created.
- Capture live runtime evidence through the reviewed Windows-native path when
  the provider/runtime is ready.
- Pass `scripts\preflight-live-runtime.ps1` (capture or attach mode) before
  any guarded execution; a failed preflight is the recorded `runtime_gap`
  blocker before any 1C interaction, not a mid-card discovery.
- Publish compact evidence for each row with action/background/recovery ranges
  where available.
- Classify each row as `accepted`, `candidate`, `rejected`, `blocked`,
  `partial` or `timeout` according to available replay, direct probe or typed
  contract proof.
- Keep raw captures, full UI dumps, platform logs and generated replay payloads
  under ignored runtime or artifact paths.

## Out Of Scope
- Treating the demo configuration as production-safe or portable to customer
  bases.
- Unbounded clicking across arbitrary forms without manifest review.
- Save/post/delete/fill/import/export actions without pre-approved recovery or
  cleanup.
- External side effects such as filesystem, network, mail, exchange, print,
  clipboard, COM automation outside the 1C test runtime or OS dialogs.
- Promoting protocol mappings from visual success alone.
- Replacing V2 safe-action acceptance gates; this is a separate mutation layer.

## Acceptance
- A real-demo mutation manifest is defined for the selected first row set.
- At least one reviewed row is either executed with retained pre/action/post
  and recovery evidence, or blocked with a precise no-execution reason.
- Any created or changed demo data is cleaned up, reset, or documented as an
  acceptable test residue with owner and residual risk.
- Action frames are separated from bootstrap, background refresh and recovery
  traffic before any row is considered for accepted status.
- Accepted output remains empty unless same-action replay, direct Python-manager
  probe or accepted typed contract proof supports the row.
- The final publication states whether the pilot produced accepted mappings,
  candidate evidence, rejected rows or blockers.
- A live runtime preflight result is retained for every execution attempt, or
  its failure is the recorded blocker.
- The final publication refreshes
  `docs/protocol-research/api-inventory/case-api-map.json` and
  `docs/protocol-research/coverage-report.md` when row statuses changed, and
  states whether the mutation scheme is proven well enough to plan the 30-50
  row batch corpus card per `docs/protocol-research/methodology.md`.

## Change Set
- `openspec/changes/archive/2026-06-10-select-demo-real-mutation-targets/`
- `openspec/changes/archive/2026-06-10-define-demo-mutation-manifest-contract/`
- `openspec/changes/archive/2026-06-10-execute-demo-mutation-guarded-pilot/`
- `openspec/changes/archive/2026-06-10-isolate-demo-mutation-action-frames/`
- `openspec/changes/archive/2026-06-10-publish-demo-mutation-corpus-decision/`

## Verify
- `bin\openspec.cmd validate select-demo-real-mutation-targets --strict`
- `bin\openspec.cmd validate define-demo-mutation-manifest-contract --strict`
- `bin\openspec.cmd validate execute-demo-mutation-guarded-pilot --strict`
- `bin\openspec.cmd validate isolate-demo-mutation-action-frames --strict`
- `bin\openspec.cmd validate publish-demo-mutation-corpus-decision --strict`
- `scripts\preflight-live-runtime.ps1 -Mode capture -OutputPath .artifacts\openspec\execute-demo-mutation-guarded-pilot\20260610-demo-real-mutation-pilot\runtime-pilot\preflight_result.json`
- `python tools\protocol-research\coverage_report.py`
- `python -m pytest tests\test_coverage_report.py`
- `bin\openspec.cmd validate qa-mcp-protocol-lab --strict`
- `bin\openspec.cmd validate --all`
- `git diff --check`

## Archive
- `openspec/changes/archive/2026-06-10-select-demo-real-mutation-targets/`
- `openspec/changes/archive/2026-06-10-define-demo-mutation-manifest-contract/`
- `openspec/changes/archive/2026-06-10-execute-demo-mutation-guarded-pilot/`
- `openspec/changes/archive/2026-06-10-isolate-demo-mutation-action-frames/`
- `openspec/changes/archive/2026-06-10-publish-demo-mutation-corpus-decision/`

## Related
- `openspec/board/4.done/60-2026-06-07-demo-real-button-safe-action-pilot.md`
- `openspec/board/4.done/70-2026-06-08-client-fixture-v3-mutation-evidence-promotion.md`
- `openspec/board/4.done/04-2026-06-04-client-fixture-v4-dialog-recovery.md`
- `openspec/changes/archive/2026-06-10-select-demo-real-mutation-targets/`
- `openspec/changes/archive/2026-06-10-define-demo-mutation-manifest-contract/`
- `openspec/changes/archive/2026-06-10-execute-demo-mutation-guarded-pilot/`
- `openspec/changes/archive/2026-06-10-isolate-demo-mutation-action-frames/`
- `openspec/changes/archive/2026-06-10-publish-demo-mutation-corpus-decision/`
- `docs/protocol-research/evidence/demo-button-safe-action/20260610-demo-button-blocked-publication/`
- `docs/protocol-research/evidence/demo-real-mutation-corpus/20260610-blocked-pilot/`
- `docs/protocol-research/evidence/accepted-mappings/demo-real-mutation-corpus-20260610/`
- `docs/protocol-research/evidence/client-fixture-v3-mutation/20260609-recovery-proof/`
- `docs/protocol-research/corpus-evidence-contract.md`
- `docs/protocol-research/safe-ui-action-scope.md`
- `scripts/preflight-live-runtime.ps1`
- `docs/protocol-research/api-inventory/case-api-map.json`
- `docs/protocol-research/coverage-report.md`

## Result
completed: the pilot selected one real-demo document-form mutation row,
`demo10413-operation-goods-toggle-activity`, and defined the reviewed
manifest/status contract for `mutates_business_data=true` rows in the
disposable demo10413 lab.

The capture-mode live runtime preflight passed, but the guarded pilot stopped
before UI attach or click because the row lacks live active-form/target-marker
pre-state, a selected register-record state and a reviewed recovery wrapper.
No 1C action executed, no demo data changed, no raw capture was created and
accepted mutation mappings remain empty.

The final publication status is `blocked`; the mutation scheme is not yet
proven enough to plan the 30-50 row batch corpus card.

Provider note: AI1C trace capture was skipped because
`/opt/ai-tools-1c/bin/ai1c-trace.cmd` and
`/opt/ai-tools-1c/bin/ai1c-trace` were not present in this Windows workspace.
The active `vanessa-mcp` provider remains an expected unproxied profile gap.

## Next
- none

## Change 1: `select-demo-real-mutation-targets`

### Why
The pilot needs a deliberately small real-demo row set before any mutating UI
operation can be reviewed or executed.

### Goal
Select one primary document-form mutation candidate and one or two low-blast-
radius catalog or processing candidates, or publish a blocked target-selection
summary when no candidate can be reviewed safely.

### Scope
- Read-only runtime, Vanessa, metadata or existing card-60 evidence review.
- Target records with form/object path, element path, operation family,
  expected business-data mutation, recovery feasibility and residual risk.
- Rejected or deferred target notes.
- No click, write, save, post, delete or capture execution.

### Acceptance
- The selected first row set is small, explicit and reviewable.
- Each candidate has an owner, evidence route and recovery feasibility note.
- Rejected or blocked candidates remain visible with reason and residual risk.

### Depends On
- none

### Related
- `openspec/changes/archive/2026-06-10-select-demo-real-mutation-targets/`

### Outcome
Selected one document-form row from the card-60 real demo button evidence and
deferred additional catalog/processing rows because no compact reviewed marker
and recovery plan were available. No click or write was attempted.

### Notes For `$openspec-ff-change`
- Preserve the no-execution boundary in proposal, design, spec and tasks.
- Include 1C verification rows for managed-form target evidence and command
  classification.

## Change 2: `define-demo-mutation-manifest-contract`

### Why
Real-demo mutations are allowed only when every attempted action is manifest-
driven, reviewed, observable and recoverable.

### Goal
Define the machine-readable manifest row shape, allowed statuses and fail-
closed validation rules for real demo mutation candidates where
`mutates_business_data=true` is explicit and permitted only with recovery.

### Scope
- Manifest fields for `target_id`, object/form path, element path, operation
  family, pre-state, action, expected post-state, recovery expectation,
  residual risk, target marker and proof route.
- Status taxonomy: `accepted`, `candidate`, `rejected`, `blocked`, `partial`
  and `timeout`.
- Explicit separation from V2 safe-action rows.
- Compact evidence and accepted-output gates.

### Acceptance
- Every executable row must be complete before guarded execution.
- Incomplete, unsupported or unrecoverable rows fail closed with reason.
- Accepted output remains proof-gated by same-action replay, direct
  Python-manager probe or accepted typed contract proof.

### Depends On
- `select-demo-real-mutation-targets`

### Related
- `openspec/changes/archive/2026-06-10-define-demo-mutation-manifest-contract/`

### Outcome
Defined the real-demo manifest/status contract, including fail-closed handling
for `mutates_business_data=true` rows without live pre-state and reviewed
recovery proof.

### Notes For `$openspec-ff-change`
- Treat this as a docs/tooling contract change; no live mutation occurs here.
- Include evidence paths for compact manifest review bundles.

## Change 3: `execute-demo-mutation-guarded-pilot`

### Why
The pilot needs one controlled execution path that can either run a reviewed
recoverable row or stop before mutation with a precise blocker.

### Goal
Execute at most the reviewed first row set against the disposable demo10413
runtime through the Windows-native path, retaining pre/action/post/recovery
evidence or a no-execution blocker.

### Scope
- Live runtime preflight (`scripts\preflight-live-runtime.ps1`, capture or
  attach mode) before any 1C process start or attach; failed preflight is a
  recorded `runtime_gap` blocker before execution.
- Manifest load and pre-state recheck.
- Guarded action execution only for reviewed, recoverable rows.
- Unique `QA_MCP_*` markers when new demo data is created.
- Recovery or cleanup proof, owned-process cleanup and raw-output separation.

### Acceptance
- At least one reviewed row executes with retained recovery evidence, or the
  pilot records a precise blocked reason before execution.
- Any changed demo data is cleaned, reset or documented as acceptable residue.
- Raw captures, logs and generated replay payloads stay outside reviewed git.

### Depends On
- `select-demo-real-mutation-targets`
- `define-demo-mutation-manifest-contract`

### Related
- `openspec/changes/archive/2026-06-10-execute-demo-mutation-guarded-pilot/`

### Outcome
Ran capture-mode live preflight successfully and retained the result, then
blocked before any UI action because the selected row was not
execution-eligible. Runtime action attempted: `false`.

### Notes For `$openspec-ff-change`
- Include fail-closed execution gates and owned-process safety.
- Add 1C verification matrix rows for form command, managed form UI proof and
  runtime cleanup evidence.

## Change 4: `isolate-demo-mutation-action-frames`

### Why
Real-demo mutation evidence cannot be promoted until action frames are separated
from bootstrap, background refresh and recovery traffic.

### Goal
Analyze the guarded pilot output to label action, background and recovery
ranges and classify each row's frame-isolation quality.

### Scope
- Phase event review and candidate frame-range extraction.
- Background/refresh range notes.
- Dynamic-field, normalized-hash and response-marker review when available.
- Non-accepted status when ranges are ambiguous or proof is missing.

### Acceptance
- Each attempted row has action, background and recovery ranges where
  available, or a precise unresolved reason.
- Accepted status is impossible without same-action replay, direct probe or
  accepted typed contract proof.
- Frame-isolation notes are retained in compact evidence.

### Depends On
- `execute-demo-mutation-guarded-pilot`

### Related
- `openspec/changes/archive/2026-06-10-isolate-demo-mutation-action-frames/`

### Outcome
Recorded `blocked_no_action_frames`: no action/background/recovery frame ranges
exist because the guarded pilot stopped before action.

### Notes For `$openspec-ff-change`
- Keep this change evidence-focused; do not add new mutations.
- Route analyzer/provider gaps to the owning provider rather than hiding them
  as manual checks.

## Change 5: `publish-demo-mutation-corpus-decision`

### Why
The pilot must publish a clear final decision so candidate, rejected, blocked
or accepted rows are not confused with each other.

### Goal
Publish compact corpus evidence for the real-demo mutation pilot and state
whether it produced accepted mappings, candidate evidence, rejected rows or
blockers.

### Scope
- Compact evidence bundle or docs publication.
- Evidence-index and accepted-output updates.
- Final row status, proof route, recovery status and residual risk.
- Case-api-map and coverage-report refresh when row statuses changed.
- Explicit batch-readiness decision: whether the mutation scheme is proven
  well enough to plan the 30-50 row batch corpus card.
- Raw runtime output exclusion.

### Acceptance
- Final publication lists every attempted or selected row with status and
  evidence links.
- Accepted output remains empty unless accepted proof exists for the same
  action.
- Residual demo data, if any, has owner and risk note.

### Depends On
- `select-demo-real-mutation-targets`
- `define-demo-mutation-manifest-contract`
- `execute-demo-mutation-guarded-pilot`
- `isolate-demo-mutation-action-frames`

### Related
- `openspec/changes/archive/2026-06-10-publish-demo-mutation-corpus-decision/`

### Outcome
Published compact blocked-pilot evidence, updated the evidence index, emitted
empty accepted-mapping output and regenerated the API coverage report.

### Notes For `$openspec-ff-change`
- Publication may be candidate-only or blocked; either outcome is valid when
  evidence and blocker details are precise.
- Include OpenSpec, evidence-index and diff-check verification tasks.

## Log
- 2026-06-10T07:16:02Z card created after deciding to use existing demo10413
  real forms as a controlled mutation/recovery corpus.
- 2026-06-10T07:24:23Z `$opsx-ff` moved card to `2.todo`, decomposed five
  OpenSpec changes and began artifact preparation.
- 2026-06-10T07:31:50Z `$opsx-ff` completed artifacts, validation and delivery
  manifest sync.
- 2026-06-10T11:45:00Z card and change artifacts aligned with the lab-hardening
  pass: live runtime preflight gate before guarded execution, proof-class
  risk-tier minimums from `corpus-evidence-contract.md`, coverage-report and
  case-api-map refresh in publication, and the batch-readiness decision per
  `methodology.md`.
- 2026-06-10T12:40:00Z `$opsx-do` completed all five changes, published a
  blocked real-demo mutation pilot, archived changes and moved card to
  `4.done`.
- 2026-06-10T12:55:00Z `$opsx-pub` verified final OpenSpec state, refreshed
  durable protocol docs, prepared the scoped publish commit and left local
  runtime artifacts excluded.
