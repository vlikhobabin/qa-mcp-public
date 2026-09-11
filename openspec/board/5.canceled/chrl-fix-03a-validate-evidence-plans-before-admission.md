# Require a persistent evidence plan before admitting a new card

## Status

5.canceled

## Owner
qa-mcp

## Series
chrl-fix-03a

## Order Index
406.221

## OpenSpec Stage
operator-refined implementation candidate; not admitted

## Priority
P1

## Source

Historical planning snapshot: the baseline observations below and the retained
Scope, Design, Budget, Verify, Next and ordered Changes describe the original
proposal. Current offline implementation and evidence are recorded in Result;
preserving the proposal does not grant admission or publication authority.

- Operator authorized refining the first independently useful boundary of `openspec/board/5.canceled/chrl-fix-03-persist-and-enforce-card-evidence-contract.md` into a bounded implementation plan.
- The parent separates plan completeness from observed evidence authenticity. This card owns only the former; a valid plan is not a passing implementation, GO or publication authority.
- Existing reusable seams: `section_body`, `acceptance_criteria`, `admission_report` and `doctor` in `scripts/changerail/local_delivery.py`; `_require_stage_sections`, `_tasks_admission`, `_has_complete_plan` and `_accept_card` in `scripts/changerail/local_ff.py`.
- `bin/board-ff`, including its dry-run mode, already calls the common `chrl admission` entrypoint. `doctor(recovery=True)` already skips fresh right-size admission and separately requires exact retained recovery. These facts avoid another wrapper or a new legacy registry.
- FF tasks admission currently caches by card workspace only. A retained READY predating the new rules must not bypass current plan validation. The final acceptance boundary must check current proof-plan validity before any card transition.

## Summary

New cards must declare a small, versioned mapping from all acceptance conditions
to intended verification before they are admitted. Use one read-only validator
from ordinary FF, complete-plan admission and existing shell/direct adapters.
Persist the authoring and role rules in project-owned files so a fresh session
does not depend on chat history or private working notes.

This is independently useful planning validation. It does not implement retained
check receipts, enforce observed proof at handoff/GO, repair the offline finalizer
or migrate the currently stopped pilot.

## Acceptance

### Requirement: Give each mandatory condition a verifiable plan

#### Scenario: A simple or risk-bearing card declares verification

- [C1] WHEN a candidate uses the new template, THEN every top-level Acceptance bullet, including each structured WHEN/THEN/AND bullet, has a unique local condition ID and exactly one verification row with an implementation seam, precondition, action, expected observation, method and owning stage; all six defined risk categories are assessed, with reasoned non-applicability and a mechanism decision plus condition references for applicable risks.
- [C2] AND the read-only validator rejects missing/unknown versions, malformed or duplicate JSON keys, duplicate/missing/foreign condition references, empty required values, unknown fields, invalid method/stage values and incomplete/overlapping risk assessments; it neither reads nor executes a declared check target, and an otherwise valid future test target may not exist yet.

### Requirement: Apply the same gate on every new-admission path

#### Scenario: Normal FF, cached FF and a complete plan request acceptance

- [C3] WHEN ordinary FF tasks, the deterministic complete-plan path, direct chrl admission, board-ff or fresh-start doctor evaluates a new candidate, THEN the same current plan validation is required; an invalid plan cannot reach the todo transition, and already cached READY metadata cannot substitute for revalidation after the contract policy changes.
- [C4] AND planning remains phase-aware: specs require identified Acceptance conditions, design requires Design and risk decisions, and tasks/final admission require the complete verification mapping. Earlier stages and admission never require completed tests, observed success, implementation handoff or a model invocation to evaluate the static contract.

### Requirement: Persist the rule without claiming semantic proof

#### Scenario: A new or resumed session consumes the project instructions

- [C5] WHEN the repository instructions and template are read in a new session, THEN AGENTS/OpenSpec/board/FF-delivery-review guidance consistently points to the same plan format and distinguishes structural plan validation, implementation checks and runner-owned acceptance; resumed FF includes the same card-bound plan and stage requirements, and tests check template/routing consistency.
- [C6] AND instructions require meaningful before/action/after observations where risks demand them and identify what is mocked versus actually exercised; a populated row, call-order stub or N/A statement is not semantic proof. The reviewer still judges coverage of all clauses and adequacy of the chosen methods; no automatic classifier, new coverage threshold or extra uncounted review cycle is introduced.

### Requirement: Preserve old exact recovery and authority boundaries

#### Scenario: Legacy cards coexist with new planning validation

- [C7] WHEN new admission or a fresh start encounters a versionless/unsupported plan, THEN it gives a concrete plan-migration refusal without editing the card. Existing eligible exact recovery continues through its unchanged recovery branch; an amended tree, renamed card or claimed legacy flag gains no new recovery permission. No old card, source manifest, verdict, counter or history entry is rewritten.
- [C8] AND implementation of this gate leaves evidence execution, handoff, review verdict validation, publisher, budgets and model routes unchanged. It does not enable FIX-02, admit the parent aggregate, make either plan a retroactive done prerequisite for FIX-01, authorize live/model calls in tests or turn a planning/offline request into commit/push authority.

## Scope

Production implementation: three files only.

- `scripts/changerail/local_delivery.py`: pure plan extraction/validation adjacent to existing card helpers; require a valid plan in fresh `admission_report`. Do not change the recovery branch or execution/evidence/review/publication functions.
- `scripts/changerail/local_ff.py`: stage-specific plan checks, current-policy validation around cached admission and final acceptance; retain existing stage routing and FF schema.
- `tools/changerail/schemas/card-evidence.schema.json` (new): closed plan-only `qa-mcp.card-evidence.v1` schema. No result, verdict or execution schema is added here.

Instructional/canonical payload, reviewed and included in the estimate:

- `AGENTS.md`: a short evidence-plan obligation and links, preserving ordinary offline completion and authority rules.
- `openspec/config.yaml`: condition IDs in specs, seam/risk decisions in design, verification mapping in tasks; preserve board-only lifecycle.
- `openspec/board/README.md`: authoring format and distinction between new admission and exact legacy recovery.
- `openspec/board/card-template.md`: add Design, Affected Capabilities and per-Change Ordered Tasks; provide the contract pattern inside Verify so a completed template also fits the existing complete-plan detector.
- `docs/development/local-changerail-delivery.md`: explain the new-admission gate, migration refusals and the still-unimplemented runtime proof gate.
- `tools/changerail/skills/chrl-ff/SKILL.md`: phase-specific authoring and validation responsibilities.
- `tools/changerail/skills/chrl-deliver/SKILL.md`, `tools/changerail/skills/chrl-review/SKILL.md`: consume the matrix and assess required conditions; do not claim deterministic observed-proof enforcement before the later card implements it. Edit these canonical skill sources, not their symlinked copies.
- `openspec/specs/changerail-consumer-wiring/spec.md`: plan-gate behavior and its refusal/compatibility scenarios, explicitly separate from eventual execution-proof guarantees.

Tests: new `tests/test_local_changerail_evidence_plan.py`, plus scoped fixtures
and assertions in `tests/test_local_changerail_delivery.py`,
`tests/test_local_changerail_ff.py` and `tests/test_board_helpers.py`.
This card's Result/Log may be updated during implementation. Its parent is not
part of the future implementation payload.

## Non-Goals

- A new helper module, general Markdown parser, YAML dependency, lifecycle framework, arbitrary command executor, schema registry or per-card waiver list.
- Runtime proof receipts, before/after execution fingerprints, duplicate full-suite suppression, structured actual-result references, additional-plan GO validation or changes to `review-verdict.schema.json`. These remain the parent's second boundary.
- Implementing any CHRL-FIX-02 finalization mechanism, changing publisher crash recovery, classifying historical activity again or altering retained recovery budgets.
- Rewriting legacy/accepted/done/canceled/frozen cards en masse, forcing accepted cards through FF again, silently downgrading new admission, changing profile limits or reducing safety conditions to fit an estimate.
- Live 1C/Windows/provider operations, real model calls in tests, real project card transitions, commit/push or new `openspec/changes/` artifacts during offline verification.

## Depends On

- none

The parent is a planning source, not a done dependency. Implementing the first
boundary does not require the future execution-proof gate or finalizer to publish
itself. The current occupied/dirty checkout is not a clean-start exception.

## Affected Capabilities

- `changerail-consumer-wiring`

## Change Set

- `chrl-fix-03a-define-and-validate-static-evidence-plan`
- `chrl-fix-03a-integrate-new-admission-and-session-guidance`

## Design

The unchanged-recovery premise below belongs to the original plan-gate scope.
Later offline checks exposed defects in that baseline; the separately authorized
exact-proof and duplicate-key corrections are attributed in Result, not added
retroactively to this card's original scope or acceptance authority.

### Restricted card format

Use the existing top-level Acceptance and Verify sections, not a second tracked
plan artifact. Each top-level Acceptance bullet begins `- [C<number>] `, with
positive integers and unique IDs across the card. Wrapped continuation lines
belong to that bullet; structured Requirement/Scenario headings remain unchanged.
Compact and structured acceptance both work. Do not count IDs as new admission
groups or change existing semantic scenario grouping.

Require one Design section and exactly one fenced `json` block inside Verify.
Reject ambiguous duplicate Acceptance/Verify/Design sections, missing IDs on a
top-level Acceptance bullet, duplicate JSON object keys and multiple/unclosed
contract blocks. Parse the bounded format using existing section extraction and
JSON/schema tooling; do not reconstruct arbitrary Markdown. A condition can
contain several related assertions; checking the meaning/completeness of those
assertions remains a planning/review obligation, not a natural-language parser.

The plan schema permits exactly these fields:

- Root: `schema`, `conditions`, `risks`; schema is exactly `qa-mcp.card-evidence.v1`.
- Condition row: `condition`, `seam`, `precondition`, `action`, `expected`, `method`, `stage`. There is exactly one row per Acceptance ID. All descriptive strings are nonempty.
- Method: `kind` (`test`, `inspection`, `runtime`) and `target`, a repository-relative file locator with an optional literal `::selector`. Targets are metadata only: no absolute/escaping path, URL, shell command or file existence/execution requirement. They may describe a file to be created by implementation.
- Stage: `implementation`, `review` or `final`, identifying who will eventually supply the proof; admission verifies declarations only.
- Risk group: `kinds`, `applies`, `decision`, `conditions`. Known kinds are `mutation`, `concurrency`, `restart`, `publication`, `input_safety`, `external_effects`. Every kind occurs exactly once across groups. Related N/A kinds may share a concrete reason. `applies` is a strict boolean; applicable groups name existing condition IDs and a mechanism decision, while N/A groups use an empty condition list and a reason.

Closed schema validation owns types/enums/nonempty fields. A small Python check
owns exact ID/risk set equality and reference consistency. A declaration cannot
contain observed results or self-approved success. The Verify block below is a
concrete design example for this card. At proposal time the format was not yet
supported; structural validation is now implemented as recorded in Result.
Observed execution-proof enforcement remains separate, unimplemented work.

### Reuse and call boundaries

Keep the pure helper in `local_delivery.py`, taking card text plus the schema and
returning plan findings/parsed data without writes or invoking a model. Read the
candidate once for that validation; do not dereference check locators.
`admission_report` requires a valid plan before the existing size checks.
Its existing direct CLI and shell caller inherit the same rule without editing
`bin/board-ff` or adding another entrypoint.

An incomplete/invalid declaration is an actionable `DeliveryError` (CLI exit 2),
not a sizing verdict or an instruction to split the card. Existing budget
overruns retain their SPLIT_REQUIRED report/exit 3. Fix a missing plan field in
the same planning scope; do not create rescue cards for a structural error.

The FF specs validator checks Acceptance IDs without requiring a JSON block.
Design requires Design plus the closed declaration with all risk groups; its
`conditions` array may still be empty, and risk references resolve against
Acceptance IDs. The full row-to-ID equality check is mandatory at tasks/final
admission. These stage checks use the same extraction conventions and schema,
not a second acceptance parser; the schema can permit an empty conditions array
while the tasks/admission equality check rejects missing rows.
The template adds the sections already expected by `_has_complete_plan`; that
detector must not reroute an otherwise complete but invalid evidence plan into
new model planning just to avoid a deterministic refusal.

`_tasks_admission` must validate the current contract before returning cached
READY. Cache reuse must account for the current schema/policy, not just the card
hash; missing old policy metadata requires revalidation. `_accept_card` also
requires current plan validity before any writes. Preserve existing card/workspace
identity checks; this card does not claim a new cross-process atomic transition
or introduce mutable-lease recovery. Test a retained old READY and a card edited
before final acceptance, not only fresh direct calls.

`doctor(recovery=True)` already skips fresh admission and proves exact retained
scope separately: leave that branch and its manifest/counter behavior unchanged.
There is no new legacy flag, registry or date-based exception. An old accepted
but not yet running card receives a migration diagnostic at a fresh start if it
lacks the contract; its plan must be explicitly updated, not silently changed
or sent through FF again. An amended old run still fails existing exact recovery.

### Persistent instructions and their limits

The board README describes the format; the template provides it; canonical specs
describe observable gates. AGENTS and OpenSpec carry concise requirements/links.
FF owns declaring the plan, implementation checks its planned assertions, review
judges test adequacy. All refer to the same names and stage distinctions.
Clarify existing instructions instead of repeating a checklist in every file.

A successful static check means only that a plan is structurally complete.
Relevant tests must exercise real policy/state seams rather than only call-order
stubs. The machine cannot prove that a well-formed N/A reason or expected result
is truthful; normal planning/review retains that responsibility. No new observed
evidence enforcement, model session or extra review cycle is implied here.

## Implementation Plan

1. Add the minimal closed plan schema and pure validation beside current card helpers. Use malformed/positive template fixtures before connecting any gate.
2. Connect fresh admission and FF phase/cache/acceptance seams; exercise actual common validators through normal, complete-plan and shell routes using fake models in isolated repositories.
3. Synchronize template, board/canonical rules and the short AGENTS/OpenSpec/role guidance; update ordinary test-card factories to the new format while retaining dedicated legacy recovery fixtures unchanged.
4. Finalize this card's Result/Log, retain focused evidence and hand off only in an authorized measured delivery. The outer runner owns fresh review and one final floor. An ordinary offline implementation instead reports its checks without inventing a handoff.

## Delivery Budget

- primary_invariant: Every new-admission route rejects a card lacking a complete static evidence plan without demanding observed implementation results or changing exact legacy recovery.
- expected_wall_minutes: 30
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 3
- estimated_production_loc: 280

## Budget Notes

Provisional bounded estimate, not measured READY or a correctness guarantee:
approximately 145 lines for extraction/reference checks in the existing owner,
100 schema lines and 35 FF/admission integration lines. Instruction changes and
test fixtures are additional reviewed payload included in the time estimate.
Do not minify code/schema or omit negative cases to obtain these numbers.

The reduction from the parent's first-boundary estimate uses concrete reuse:
no new Python module, no legacy registry/migration engine, unchanged exact
recovery, existing shell-to-admission routing, and no execution/result/verdict
schema. Both ordered Changes remain necessary to this one planning invariant.
After Change 1, compare actual scope and remaining integration work to this
estimate. If it is no longer credible under existing limits, record the concrete
design gap before broadening; do not report an unexplained planning variance as
completed acceptance. No profile/budget increase is authorized by this card.

## Canonical Specs

- `openspec/specs/changerail-consumer-wiring/spec.md`

## Verify

This is the retained proposal's plan declaration, now supported by the static
validator. Its original targets remain planned locators, not execution results
or a claim that those exact test names exist. Result maps the actual proof and
its checkpoints; structural validation does not establish observed success.

```json
{
  "schema": "qa-mcp.card-evidence.v1",
  "conditions": [
    {"condition": "C1", "seam": "card template and plan parser", "precondition": "compact and structured cards with simple and risk-bearing changes", "action": "extract condition IDs and validate the plan", "expected": "one complete row per ID and exact risk coverage", "method": {"kind": "test", "target": "tests/test_local_changerail_evidence_plan.py::test_complete_plan_shapes"}, "stage": "implementation"},
    {"condition": "C2", "seam": "read-only schema/reference validation", "precondition": "one invalid field/reference per fixture plus a future test path", "action": "validate without touching targets or running commands", "expected": "malformed plans fail; a valid future locator passes with zero side effects", "method": {"kind": "test", "target": "tests/test_local_changerail_evidence_plan.py::test_plan_validation_boundaries"}, "stage": "implementation"},
    {"condition": "C3", "seam": "admission_report and FF/shell callers", "precondition": "normal, complete-plan and cached-ready candidates", "action": "request admission and attempt the actual fixture acceptance boundary", "expected": "all routes use current validation and invalid candidates remain unmodified in backlog", "method": {"kind": "test", "target": "tests/test_local_changerail_evidence_plan.py::test_all_new_admission_routes"}, "stage": "implementation"},
    {"condition": "C4", "seam": "FF stage-specific validation", "precondition": "specs/design declarations without implementation or completed checks", "action": "validate stages and final planned-only admission", "expected": "only phase-appropriate fields are required; full mapping is required at tasks/admission", "method": {"kind": "test", "target": "tests/test_local_changerail_evidence_plan.py::test_phase_appropriate_plan_checks"}, "stage": "implementation"},
    {"condition": "C5", "seam": "template and project-owned instruction routing", "precondition": "new template and resumed FF context", "action": "render a card and inspect declared authority/context references", "expected": "same format and ownership names are available without chat history or duplicated skill copies", "method": {"kind": "test", "target": "tests/test_local_changerail_evidence_plan.py::test_template_and_instruction_contract"}, "stage": "implementation"},
    {"condition": "C6", "seam": "FF/delivery/review instructions and actual validator tests", "precondition": "a valid-looking plan and a call-order-only stub", "action": "review the planned assertions against the required behavior", "expected": "review distinguishes structural validity from semantic adequacy and does not certify the stub as invariant proof", "method": {"kind": "inspection", "target": "tools/changerail/skills/chrl-review/SKILL.md"}, "stage": "review"},
    {"condition": "C7", "seam": "fresh admission versus unchanged exact recovery", "precondition": "versionless fresh card, eligible legacy run and amended/renamed legacy payload", "action": "run real admission and existing recovery checks in fixtures", "expected": "fresh missing version and inexact recovery fail; eligible exact recovery and source hashes/counters are preserved", "method": {"kind": "test", "target": "tests/test_local_changerail_evidence_plan.py::test_legacy_recovery_is_not_new_admission"}, "stage": "implementation"},
    {"condition": "C8", "seam": "scope and unchanged execution/authority boundaries", "precondition": "final scoped diff and ordinary harness fixtures", "action": "inspect scope and run focused ordinary regressions", "expected": "no execution-proof/finalizer/publisher/budget changes or real model/live/publication calls", "method": {"kind": "inspection", "target": "scripts/changerail/local_delivery.py"}, "stage": "review"}
  ],
  "risks": [
    {"kinds": ["input_safety"], "applies": true, "decision": "Closed schema plus exact IDs; check locators remain inert metadata and are never read or executed.", "conditions": ["C1", "C2"]},
    {"kinds": ["mutation", "restart"], "applies": true, "decision": "Validate at existing admission/acceptance boundaries, reject stale policy caches, and leave exact retained recovery untouched.", "conditions": ["C3", "C7"]},
    {"kinds": ["concurrency", "publication", "external_effects"], "applies": false, "decision": "This gate adds no worker, shared execution lock, publisher or external operation; existing lifecycle ownership remains unchanged and no new atomicity guarantee is claimed.", "conditions": []}
  ]
}
```

Required negative cases: missing contract/ID/row/expected observation; unknown
schema/field/kind/stage; duplicated JSON key, section, ID, risk kind or row;
foreign condition/risk; empty N/A decision; string instead of boolean; absolute,
escaping or command-like method target; malformed/unclosed/multiple JSON blocks;
stale cached READY and a changed candidate before acceptance. Test both syntax
and exact coverage; do not merely count rows.

- Change 1 proposed focus: `uv run pytest -q tests/test_local_changerail_evidence_plan.py -k 'complete_plan_shapes or plan_validation_boundaries'`.
- Change 2 proposed focus: `uv run pytest -q tests/test_local_changerail_evidence_plan.py`.
- Existing regression harness: `uv run pytest -q tests/test_local_changerail_delivery.py tests/test_local_changerail_ff.py tests/test_board_helpers.py`.
- `git diff --check`.
- `uv run python -m compileall -q src tests scripts/changerail`.
- `./bin/openspec validate --specs --strict --no-interactive`.
- `./bin/verify-project`.
- Runner-owned final floor for an authorized measured delivery: `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60`.
- Keep the common validator, FF state transition and shell adapter real in isolated fixtures; fake only model/external boundaries. Assert refusal leaves fixture card bytes/column unchanged, old records and counters unchanged, and actual project/model/live/commit/push call counts at zero. No new positive tests or actual implementation results are claimed by this plan.

## Related

- `openspec/board/5.canceled/chrl-fix-03-persist-and-enforce-card-evidence-contract.md`
- `openspec/board/5.canceled/chrl-fix-02-finalize-authorized-offline-repair.md`
- `openspec/board/4.done/oss-fix-01-freeze-physical-target-configuration.md`
- `openspec/board/README.md`
- `docs/development/local-changerail-delivery.md`

## Result

### Current offline state and evidence checkpoints

The static plan gate and the C3/C5 integration proofs are implemented offline.
Exact recovery was repaired separately, including recursive refusal of duplicate
JSON object keys. The original proposal and Next section remain historical
planning/authority boundaries, not a claim that implementation is still absent.

Retained local evidence under ignored `.runtime/changerail/` distinguishes:

- Initial implementation: 242 focused tests and 1879 non-live tests, 74.69%
  coverage. These are historical counts, not the latest verification.
- Completed C3/C5 checkpoint: 280 focused tests and 1917 non-live tests, 74.69%
  coverage, plus 70 strict canonical specs, compilation and wiring. The final
  logs are `offline-chrl-fix-03a-c3c5-9rTejO/logs/14-final-four-file-harness.log`
  and `offline-chrl-fix-03a-c3c5-9rTejO/logs/19-final-nonlive-coverage.log`.
  This full floor predates the duplicate-key correction; it is not a full-floor
  result for the repaired payload.
- C7 duplicate-key correction: 6 focused raw-JSON cases and 286 delivery/FF/
  board-helper/evidence-plan tests passed, with scoped whitespace/compilation.
  See `offline-c7-duplicate-jDsNe0/orchestrator-result.md` and its indexed logs.
  Real isolated Git, manifest production, hashing, recovery and doctor are
  exercised; model launch is forbidden in those fixtures.

The prior independent assessment at
`offline-chrl-fix-03a-acceptance-nfke6j/assessment.json` recorded C1-C6/C8 pass,
C7 fail (F1: duplicate proof keys) and minor F2 (historical/current wording).
The C7 repair and this F2 clarification do not rewrite that assessment or
constitute a new independent verdict. Subsequent delta acceptance is a separate
fingerprint-bound report; no full-floor rerun, handoff, GO, admission, done
transition, finalizer, pilot or publication is implied by this documentation.

### Historical implementation sequence

Authorized offline implementation added the static `qa-mcp.card-evidence.v1`
validator, fresh-admission/FF checks, schema, template and project guidance.
At that initial checkpoint, checks passed: 242 focused tests, 1879 non-live tests, 74.69% coverage,
strict canonical specs, compilation, wiring and skill validation. This is not
complete acceptance, a measured delivery, handoff, GO or publication.

Orchestrator acceptance found a pre-existing C7 blocker: `recovery_source`
compared retained path sets but did not compare retained file fingerprints.
That baseline premise was separately repaired under explicit offline authority:
recovery now reads only a safe run-local source and refuses unless current whole
tree paths, baseline, card/run identity, aggregate fingerprint and exact
per-path hashes agree. The regression covers same-path byte drift without
rewriting the retained manifest or counter. At that checkpoint the C3/C5 route
and compatibility integration gaps were still open; their later completion is
recorded below. The card remains in backlog, and implementation wording alone
does not establish complete C1-C8 acceptance.

The separately authorized offline C3/C5 proof completion now covers the four
remaining integration boundaries in isolated Git fixtures: invalid complete
plans refuse through `run_ff` before model/transition work; an ordinary tasks
verdict with a current fingerprint but an incomplete condition map refuses;
current sizing refreshes a cached READY and blocks `_accept_card`; and a real
failed/resumed FF run preserves inherited history while enforcing its generated
context and remaining design/tasks declaration gates. The evidence map uses
`tests/test_local_changerail_ff.py` for these route proofs even where the
proposed Verify locators named the evidence-plan test module. This is bounded
offline test evidence, not a measured handoff, GO, done transition,
publication, or independent full-card review.

The retained C3 cache proof records the identical card workspace in its genuine
READY cache before policy change and in its refreshed SPLIT_REQUIRED cache
afterwards. The C5 proof records actual context schema/stage/run identity and
the complete inherited-plus-resumed verdict path sequence; its negative cases
retain the current post-model card/verdict and original failed-run history on
refusal.

## Next

No further work in qa-mcp. Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

## Change 1: `chrl-fix-03a-define-and-validate-static-evidence-plan`

### Why

A concrete, bounded representation is needed before placing a new rule on every
admission route; a future test must remain a plan rather than fabricated evidence.

### Goal

Parse the restricted card format and validate condition/risk completeness without
filesystem writes, target dereferences, command execution or observed results.

### Scope

- Pure helpers in the existing owner module, the plan-only schema and focused positive/negative fixtures.

### Acceptance

- C1 and C2 pass through the actual schema and parser; declaration-only checks require no completed implementation.

### Depends On

- none

### Ordered Tasks

1. Add schema and the smallest pure extraction/reference helpers, preserving existing scenario/requirement grouping.
2. Implement positive compact/structured examples and one-variable negative fixtures, including duplicate keys/sections and inert future targets.
3. Run the Change 1 focus and compare actual production size plus remaining integration scope with the stated estimate before proceeding.

## Change 2: `chrl-fix-03a-integrate-new-admission-and-session-guidance`

### Why

A checker that only some routes call does not protect newly created cards or
resumed sessions from omissions.

### Goal

Require the same plan at every new-admission boundary and persist its role-aware
instructions without changing retained recovery or claiming runtime proof.

### Scope

- Existing admission/FF seams, scoped instructional/canonical changes and integration/compatibility fixtures.

### Acceptance

- C3 through C8 are supported by real route/compatibility tests and explicit semantic instruction review; no evidence execution or publication boundary is broadened.

### Depends On

- Change 1

### Ordered Tasks

1. Integrate fresh admission, phase-specific FF checks and current-policy cache/acceptance validation; use the existing shell adapter unchanged.
2. Synchronize template and concise project/role guidance; keep old exact-recovery fixtures separate from newly formatted candidate factories.
3. Exercise real normal/complete-plan/shell routes, old cached READY, fresh-start migration refusal and exact legacy recovery with no real model/live/pilot calls.
4. Finalize Result/Log and retain focused checks; hand off only in a real measured implementation context, otherwise report the authorized offline implementation honestly.

## Log

- 2026-09-06T07:54:24Z Created the operator-authorized first successor plan from CHRL-FIX-03 after checking admission, shell routing, FF cache/acceptance and the exact-recovery branch. Narrowed to three production files and a concrete plan-only format; provisional budget 30 minutes/280 production-schema LOC. This is a backlog candidate, not accepted delivery or permission to implement/publish in the occupied checkout.
- 2026-09-06T08:01:35Z Read-only admission exited 0/READY with no reasons under current structural/sizing rules. Planning checks confirmed all 16 template sections, four acceptance groups, eight exact condition mappings, six risk categories, two ordered Changes, complete-plan detection, 18 existing references and two explicitly proposed paths. Diff checks reported no whitespace diagnostics. No new validator/test, full floor, FF transition, implementation, pilot or publication was run.
- 2026-09-06T08:44:59Z Authorized offline implementation added the static declaration schema/parser and fresh admission/FF integration. Corrected focused parser and scoped regression logs are retained under the offline task directory; no runner lifecycle, model/live call, recovery mutation, handoff, GO, commit or publication occurred.
- 2026-09-06T09:00:47Z Orchestrator recorded 242 focused and 1879 non-live passing tests (74.69% coverage), but did not accept completion: an isolated retained-manifest probe reproduced C7's pre-existing same-path changed-bytes recovery gap. Recovery and protected pilot/FIX-02 payloads remain unchanged. The offline report records the blocker and remaining test gaps; no card transition, handoff, GO, commit or push was performed.
- 2026-09-06T09:33:17Z Separately authorized offline repair corrected only C7's exact-recovery baseline premise. The read-only admission boundary now requires a safe run-local manifest with matching current whole-tree paths, baseline, card/run identity, aggregate and per-path fingerprints; malformed, stale, pointer-only and symlinked sources refuse before run/model work. Focused legacy recovery fixtures and negative drift/safety cases passed. This does not claim C3/C5 integration completion, card movement, handoff, GO, finalization, commit or publication.
- 2026-09-06T10:20:52Z Authorized offline C3/C5 integration proofs added only to `tests/test_local_changerail_ff.py`: complete-plan declaration refusal (unsupported version and missing condition row), current-fingerprint ordinary tasks-map refusal with unchanged prior verdicts, current sizing versus cached READY/acceptance refusal, and resumed context/history plus design-risk/tasks-row negatives. Isolated Git fixtures kept model/external boundaries fake and all policy, validators, admission, transitions and contexts real. No production behavior changed; no card movement, lifecycle runner, handoff, GO, finalization, commit, push, pilot or publication occurred.
- 2026-09-06T10:24:27Z Strengthened the same offline C3/C5 proofs before the final floor: cache workspace equality now spans genuine READY, isolated policy change and refreshed SPLIT_REQUIRED; resumed snapshots assert actual context schema/stage/run and every prior verdict identity; resumed negative refusals retain current post-model card/verdict bytes and original failed-run history. No production change or lifecycle action occurred.
- 2026-09-06T12:34:18Z Authorized F2 documentation clarification labels the original proposal/recovery premise and distinguishes the initial 242/1879 counts, completed C3/C5 280/1917 checkpoint and separately verified C7 duplicate-key correction (6 new cases; 286 adjacent harness tests). The earlier independent not-accepted assessment is preserved, not replaced by an implementation claim. Acceptance, declaration JSON, status, budgets, Next, ordered Changes and existing Log entries remain unchanged. No code, lifecycle, full-floor, pilot or publication action is part of this card edit.

## Cancellation

2026-09-09T18:38:55.554861+00:00 — Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.
