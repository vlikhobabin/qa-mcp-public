# Persist and enforce the card evidence contract across planning and delivery

## Status

5.canceled

## Owner
qa-mcp

## Series
chrl-fix-03

## Order Index
406.22

## OpenSpec Stage
non-executable aggregate; 03A/03B successors and 03C accepted offline; 03D operator-refined, implementation authorization pending

## Priority
P1

## Source

The initial baseline observations, aggregate Acceptance/Design estimates and
ordered Changes below are retained planning history. Later operator-authorized
successor refinement is recorded in Result/Next and Log; it does not rewrite
the original acceptance or authorize execution of this aggregate.

- Operator requested a persistent project-wide response to the six acceptance gaps found in the CHRL-FIX-02 offline implementation, then authorized recording the common contract and estimating its implementation scope.
- `openspec/board/5.canceled/chrl-fix-02-finalize-authorized-offline-repair.md` records the incomplete finalizer. Its CLI remains disabled; this card neither repairs nor enables it.
- Inspected mechanisms: `admission_report`, `implementation_handoff`, `run_evidence`, `build_review_context`, `validate_verdict` and `run_shell_verification` in `scripts/changerail/local_delivery.py`; `_require_stage_sections` and `_has_complete_plan` in `scripts/changerail/local_ff.py`.
- Existing delivery/review skills already require acceptance-to-code-to-test mapping and meaningful before/after assertions. The board template supplies only a general command list; FF validates mostly section presence and declared size; verdict evidence accepts arbitrary nonempty strings. These gaps permit structurally valid but substantively incomplete proof.
- The CI coverage target is `qa_mcp`, not `scripts/changerail`. Product coverage and process exit zero are not proof that a changed runner contract is satisfied. No new percentage gate is proposed here.
- Local ignored incident reports are operator context, not clean-clone prerequisites. The reproduction and required behavior are restated below.

## Summary

Make required proof survive a new session, a new card, a resumed run and the
operator-refined planning fast path. Establish one versioned, risk-proportionate
card contract connecting acceptance conditions, chosen implementation seams,
planned verification and retained results. Check structural completeness and
artifact identity deterministically; keep test adequacy and semantic correctness
with the existing independent reviewer.

This is the common prevention plan, not a second implementation attempt for
CHRL-FIX-02. Original numerical admission failures below are retained history;
the 2026-09-06 operator policy makes those limits informational. This remains a
planning source, not an executable runner input or implementation permission.

## Acceptance

### Requirement: Preserve one risk-proportionate proof contract

#### Scenario: A new session prepares or implements a new card

- WHEN a new card is created from the project template or refined through FF, THEN its versioned contract identifies each mandatory acceptance condition, the corresponding implementation boundary, a verification method and the expected retained proof; a resumed session receives the same fingerprint-bound contract rather than reconstructing it from chat.
- AND Design identifies reused functions and the contract they actually provide, material assumptions and applicable risks: state mutation, concurrency, interruption/repeat execution, publication, path/input safety and external effects. Non-applicability has a short reason; simple cards do not acquire unrelated live, concurrency or publication tests.
- AND the board rules own the authoring format, canonical specs own observable guarantees, the template supplies the fields, and AGENTS/OpenSpec/role skills route to that contract without duplicating a large checklist or reviving legacy lifecycle artifacts.
- AND an acceptance scenario remains the semantic review unit, but every required condition within it has traceable proof. Grouping many AND clauses under four headings does not prove or reduce their content; existing admission group limits are not reinterpreted.

### Requirement: Admit a verifiable plan without requiring completed implementation

#### Scenario: Both FF and an operator-refined card reach admission

- WHEN normal FF tasks or the complete-plan fast path requests admission, THEN one shared validator rejects missing/unknown contract versions, missing or duplicate condition IDs, unmapped acceptance conditions, unreasoned non-applicability and missing expected observations or verification methods before transition to todo.
- AND a planned test may not exist yet; admission validates its declared target and expected proof, not a fabricated passing run. A new card cannot opt out by declaring itself legacy or omitting its contract.
- AND security, concurrency, atomicity and recovery boundaries that apply to the change have an explicit design decision and evidence plan before product implementation; the bounded implementation discovery confirms the proposed reuse and estimate instead of assuming a named helper satisfies a new guarantee.
- AND machine validation establishes structure and consistency only. FF/review must still assess whether the declared risks, mechanisms and tests are sufficient; neither keyword matching nor a populated table constitutes semantic proof.

### Requirement: Accept only complete evidence for the current payload

#### Scenario: Implementation hands off and the runner reviews and verifies

- WHEN a versioned card is handed off, THEN every required implementation-stage proof resolves to the declared check or inspection artifact, a terminal result and the current payload; planned-only, absent, failed, truncated-as-completion or stale evidence blocks that handoff. Runner-owned review/final-floor evidence is not demanded prematurely from the implementation role.
- AND verification records identify the invocation, command/check identity, start and finish, exit status, log identity and before/after payload fingerprints. A changed payload during a check cannot be certified by stamping only its final fingerprint. Interrupted and missing results remain unconfirmed, not zero/pass.
- AND review context, template and validator derive the same namespaced expected criteria/proof references, including any additional plan explicitly admitted by an authorized caller. Missing, duplicate, foreign or stale references reject GO. No arbitrary note such as "tests passed" replaces required structured proof.
- AND the reviewer examines the real mechanism for each critical invariant: isolated tests may fake model/network behavior, but stubbing the validator, lock, state transition or publisher under examination proves only call ordering. Required preservation/replacement/retry evidence includes the relevant before-state, action and after-state.
- AND the outer runner retains one final-floor result for the frozen payload before publication and prevents concurrent duplicate execution of that same check. Successful unchanged evidence is reused; a missing log or completion cannot be replaced by coverage percentage, process exit zero, disabled functionality or an implementation report.

### Requirement: Roll out without rewriting history or expanding authority

#### Scenario: New cards coexist with retained old delivery work

- WHEN the new contract is activated for admission, THEN new cards and both planning routes require it; an existing eligible exact retained run keeps its recorded contract and accounting, while migration of an old active or amended card is explicit and invalidates affected proof. Missing version on a new admission is never a legacy bypass.
- AND completed, canceled and frozen history and original manifests/verdicts remain byte-identical. Legacy compatibility depends on exact retained runner records, not a user-supplied waiver, refreshed manifest, renamed request or omitted field.
- AND ordinary offline fixes can retain the same quality/proof inventory in an offline report without creating a fake delivery context or handoff. Reporting implemented code does not claim fresh GO or authorize publication; the command's process outcome and the feature's acceptance outcome remain distinct.
- AND changes to these shared rules do not automatically adopt other dirty work, migrate FIX-01, admit this aggregate, enable FIX-02, grant live/model execution or initiate commit/push. Changes to configured routes, budgets, full-floor policy and recovery allowances are outside scope.

## Scope

Only this card is authored during the current planning step. The proposed
implementation surface, to be allocated and re-estimated in bounded follow-up
plans, is:

- `AGENTS.md`: short startup obligation and links; preserve role/authority boundaries.
- `openspec/config.yaml`: observable conditions, seam/risk decisions and proof mapping in existing specs/design/tasks instructions; retain board-only routing.
- `openspec/board/README.md`: authoring, stage readiness and migration rules.
- `openspec/board/card-template.md`: explicit Design and a versioned proof declaration inside Verify.
- `docs/development/local-changerail-delivery.md`: proof ownership, retained results and rollout procedure; no competing normative checklist.
- `tools/changerail/skills/chrl-ff/SKILL.md`, `tools/changerail/skills/chrl-deliver/SKILL.md`, `tools/changerail/skills/chrl-review/SKILL.md`: role-specific consumption and completion rules; edit these sources, not another copy of their `.codex/skills` links.
- `openspec/specs/changerail-consumer-wiring/spec.md`: canonical observable guarantees and refusal scenarios.
- `scripts/changerail/evidence_contract.py` (proposed new small module): shared extraction, structural validation and proof-reference matching only.
- `scripts/changerail/local_ff.py`: stage validation and complete-plan detection; both admission paths use the same contract rules.
- `scripts/changerail/local_delivery.py`: admission, measured context/handoff/review integration and retained verification results, reusing existing role/payload gates.
- `tools/changerail/schemas/card-evidence.schema.json` (proposed new schema): allowlisted plan/result definitions.
- `tools/changerail/schemas/review-verdict.schema.json`: versioned structured proof references with explicit retained-version compatibility.
- `tests/test_local_changerail_evidence_contract.py` (proposed new tests), `tests/test_local_changerail_delivery.py`, `tests/test_local_changerail_ff.py`, `tests/test_board_helpers.py`: risk-matched offline regression fixtures.

## Non-Goals

- Implementing the six finalizer corrections: active-board classification, finalization lineage, source adoption, finalization lock, bootstrap authorization or exact Git publication recovery remain CHRL-FIX-02 work. This plan defines the common proof requirements those changes must satisfy.
- A new workflow engine, general Markdown parser, test framework, background service, dependency, arbitrary shell executor or automatic semantic proof system.
- Requiring all risk categories to have tests on every card; treating coverage or LOC as correctness; changing the current coverage threshold, models, budgets or review cycle caps.
- Capturing credentials, raw session streams, full source bodies or customer/runtime data as proof metadata. Logs remain ignored and use public-safe fixture inputs.
- Editing all existing cards, rewriting historical logs, enabling a legacy opt-out for new work, silently converting an offline fix to full delivery, or fabricating FF/GO/handoff records.
- New `openspec/changes/` artifacts, new active cards, real finalizer/model/live/commit/push execution during offline tests, or automatic creation of implementation siblings in this planning step.

## Depends On

- none

This prevention plan does not depend on CHRL-FIX-02 publishing itself and is not
a newly imposed done prerequisite for the stopped FIX-01 pilot. Actual execution
still needs an eligible checkout and the authority appropriate to its scope.

## Change Set

- `chrl-fix-03-define-proof-contract-and-planning-gate`
- `chrl-fix-03-retain-and-validate-delivery-proof`

## Design

### One representation with phase-aware validation

Propose `qa-mcp.card-evidence.v1` as the first explicit proof-contract version,
not as an existing supported schema. Keep one small fenced JSON declaration in
the card's Verify section; use existing JSON/schema tooling and derive runtime
indexes from it. Do not maintain another tracked manifest of the same plan.

Acceptance conditions receive stable local IDs. A proof row references its ID
and scenario rather than copying the requirement into several editable fields.
The row names the implementation seam, precondition/action/expected observation,
proof kind (test, code inspection or authorized runtime evidence), declared check
locator and required stage. Tests have an expected failure/preservation case
where the risk demands it. Runtime proof does not grant runtime authority.
An actual result later references the same row and the exact run artifact; the
planning declaration must not prefill observed success. Unsupported fields,
duplicate IDs and unresolved cross-references fail closed.

Use source path plus condition/scenario identity to disambiguate an explicitly
included plan. Bind the whole declaration and source documents to fingerprints.
Do not add implicit extra-plan adoption: a caller such as the future finalizer
must first establish that authority under its own contract.

The risk assessment lists applicable categories and briefly explains omitted
categories. A small code/documentation change may use a compact assessment.
Review checks whether that assessment matches the actual diff; the engine cannot
infer all semantic risks from filenames or trust an N/A field as proof.

### Stage ownership and integration seams

| Boundary | Required input/proof | Refusal or limitation |
| --- | --- | --- |
| FF specs/design/tasks | Condition IDs, risk/seam decisions, planned checks and expected observations | Missing plan coverage; completed tests are not required yet. |
| Direct admission of a complete card | The same shared plan validation | No fast-path omission or legacy flag bypass. |
| Implementation Change completion/handoff | Actual implementation-stage results for current bytes | Missing/stale proof; do not demand the runner's future review or full floor. |
| Fresh review | Complete condition inventory, declared and observed proof, current diff | Missing/foreign proof blocks GO; test adequacy remains a reviewer decision. |
| Final floor/publication | Terminal retained configured checks for frozen bytes | Unknown result, drift or missing required artifacts blocks publication. |
| Ordinary offline fix | Declared scope, focused results and honest acceptance/limitation report | No fabricated measured handoff, GO, automatic publication or extra model cycle. |

Retain invocation identity and in-progress/terminal state in the ignored run
directory. Reuse the existing evidence and verification execution seams; do not
build a parallel launcher. Preserve start/end fingerprints and reject drift.
Serialize a duplicate request for the same run/check/payload and reconcile a
retained result after interruption; never infer completion from a surviving
coverage file or an asynchronous launch response. Metadata/log validation must
reject unsafe paths and must not execute commands read from evidence documents.

Existing handoff, verdict schema, final verification and publisher guards remain
authoritative for their roles. A new proof result augments those guards rather
than granting execution authority itself. This is not publisher crash-recovery
implementation and does not make the disabled finalizer eligible.

### Versioning and migration

New admission requires the explicit proof version once the new gate is deployed.
All checks for that version apply to both FF and the operator-refined fast path.
An eligible exact retained legacy run is handled under its original contract;
new work cannot choose legacy mode. Bind compatibility to the retained run/card
identity and fingerprints, preserve counters and original bytes, and test both
paths. Unknown versions fail closed. Migration changes the current declared
contract and requires new affected proof; it never refreshes old records.

This plan does not authorize changing the occupied primary checkout to activate
those rules now. No prerequisite commit, arbitrary manifest adoption or cleanup
of FIX-01/FIX-02 is permitted to obtain a clean start.

### Sizing and independently useful boundaries

SPLIT_REQUIRED is an operator planning assessment, not a measured FF verdict.
The common intent touches two independently useful contracts:

1. **Plan completeness:** versioned card format, persistent role instructions,
   shared parser/schema, normal/direct admission and explicit legacy handling.
   This improves newly authored plans without pretending to enforce observed
   delivery results. Working estimate: 35 minutes and about 300 production/schema
   lines before full execution proof; not yet within admission or READY.
2. **Evidence authenticity and acceptance:** terminal fingerprint-bound check
   records, duplicate-run prevention and real proof-reference validation at
   handoff/review/floor. This improves the existing ordinary delivery path even
   without the finalizer. Working estimate: 55 minutes and about 350 additional
   production/schema lines, reusing the first contract where applicable; not READY.

These boundaries are candidates for operator-approved bounded plans, not newly
created siblings or a permission to bypass aggregate limits. Within either
boundary, function-level work remains ordered Changes. Narrow/refactor the
mechanisms and re-estimate before proposing executable cards; do not lower
numbers on paper, remove safety cases or increase profile caps to obtain READY.

The first boundary has now been refined in
`openspec/board/5.canceled/chrl-fix-03a-validate-evidence-plans-before-admission.md`:
30 expected minutes/280 production-schema LOC, using two existing Python owners
and one plan-only schema. It adds no helper module or legacy registry and leaves
execution proof outside its scope. That candidate is not an accepted transition.
The second boundary's original estimate is retained in the aggregate budget
below, not claimed to fit one delivery. The later operator-authorized refinement
separates result integrity (03B), run-local execution serialization (03C) and
condition-level proof binding (03D); the last remains SPLIT_REQUIRED. This is
not another parser or finalizer implementation. See Result and the linked cards.

## Implementation Plan

1. Refine the two independently useful boundaries above against actual seams and limits. Record concrete scope/estimates before creating executable successor plans. This aggregate must not enter chrl-run.
2. For the plan contract, implement a minimal shared representation and tests before connecting normal/direct admission; then synchronize canonical specs, board template/rules and existing role instructions.
3. For retained evidence, first reproduce missing completion, changed-during-check payload and duplicate invocation in isolated fixtures; then implement result retention/reference validation and connect stage-specific guards.
4. Exercise migration, old exact recovery and unchanged ordinary delivery through real validators. Retain code/fixture inspection of mocked boundaries so call-order tests are not mislabeled as invariant proof.
5. Run the applicable focused tests, then the configured runner-owned review/final floor for the frozen authorized delivery. Do not use this planning step or its checks as implementation, GO or publication authority.

## Delivery Budget

- primary_invariant: A new or resumed card cannot claim a satisfied required condition without phase-appropriate proof bound to its declared contract and payload.
- expected_wall_minutes: 90
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 5
- estimated_production_loc: 650

## Budget Notes

The estimate is provisional design sizing, not measured execution or a promise.
It counts three Python modules and two executable schemas; instructions, board
artifacts and tests remain additional reviewed payload, not hidden work. The
90-minute aggregate includes their coordination and risk-matched verification.
It exceeds the current 30-minute/300-production-LOC admission limits; those
limits remain unchanged. A further bounded design pass must validate or revise
the proposed independent boundaries before implementation is requested.

## Canonical Specs

- `openspec/specs/changerail-consumer-wiring/spec.md`

## Verify

The proposed tests below do not exist yet and are not reported as passed.
Their selectors are planning targets for the eventual implementation plans.

| Proof target | Preconditions and observation | Planned check family |
| --- | --- | --- |
| Persistent plan contract | Render a simple card and a risky card from the template; required fields and role references agree, with reasoned N/A and no unrelated live gate. | `card_evidence and template` |
| Normal and fast-path admission | Same otherwise-valid card through both routes; missing/duplicate condition or expected result is rejected before movement; a declared future test is allowed. | `card_evidence and admission` |
| Current implementation proof | Planned-only, absent, nonterminal, failed or stale result blocks handoff; a matching completed focused result passes without requiring a premature final floor. | `card_evidence and handoff` |
| Complete semantic inventory | Real template/context/validator with a fake model; omitted main/additional criterion, duplicate/foreign reference and stale source contract reject GO. | `card_evidence and verdict` |
| Retained check result | Payload changes while a controlled check runs, a log is missing, process is interrupted, or a second process requests the same check; no false success or concurrent duplicate. | `card_evidence and receipt` |
| Evidence adequacy | Intentionally broken fixture behavior makes the corresponding invariant test fail; a call-order stub alone does not exercise that test. Review records this distinction; protocol fixtures validate proof references, not an automatic semantic judgment. | `card_evidence and adequacy` |
| Safe rollout | New versionless card fails; eligible exact legacy recovery preserves records/counters; an amended/renamed/claimed-legacy card cannot use that compatibility. | `card_evidence and migration` |

- Proposed focused file: `uv run pytest -q tests/test_local_changerail_evidence_contract.py`.
- Existing integration harness: `uv run pytest -q tests/test_local_changerail_delivery.py tests/test_local_changerail_ff.py tests/test_board_helpers.py`.
- `git diff --check`.
- `uv run python -m compileall -q src tests scripts/changerail`.
- `./bin/openspec validate --specs --strict --no-interactive`.
- `./bin/verify-project`.
- Final authorized measured delivery floor, owned by the outer runner: `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60`.
- Use temporary Git/board/run fixtures and fake model/external services only. Preserve real policy validators and relevant process/file transitions. Do not invoke the real pilot/finalizer, create a review model session, stage, commit or push the project to test this contract.

## Related

- `openspec/board/5.canceled/chrl-fix-03a-validate-evidence-plans-before-admission.md`
- `openspec/board/5.canceled/chrl-fix-03b-retain-verifiable-check-results.md`
- `openspec/board/5.canceled/chrl-fix-03c-serialize-verification-attempts.md`
- `openspec/board/5.canceled/chrl-fix-03d-bind-acceptance-to-observed-proof.md`
- `openspec/board/5.canceled/chrl-fix-02-finalize-authorized-offline-repair.md`
- `openspec/board/4.done/oss-fix-01-freeze-physical-target-configuration.md`
- `docs/development/local-changerail-delivery.md`
- `openspec/board/README.md`
- `openspec/board/card-template.md`

## Result

### Original aggregate planning checkpoint

Planning only. The common contract, file ownership, phase-specific proof rules,
regression matrix, rollout constraints and aggregate sizing are recorded here.
SPLIT_REQUIRED: the declared total is too large for one current measured delivery.
The first successor planning card, CHRL-FIX-03A, is now recorded; canonical
contracts, instructions, schemas and implementation remain unchanged.
Read-only aggregate admission returned SPLIT_REQUIRED for the two declared budget
overruns; no accepted admission, measured FF stage verdict, handoff, GO, pilot,
commit or push exists for this aggregate. FIX-01 and the incomplete FIX-02 draft
remain untouched.

### Historical successor planning checkpoint — 2026-09-06T13:03:40Z

03A now has implemented offline plan validation and a successful independent
offline delta assessment for C1-C8. That is not a board admission, done card or
publication, and its retained verdict is bound to its reviewed payload.

The operator-authorized second-boundary plan now has three linked successors:

- 03B: terminal execution identity and intact logs, integrated into existing
  writers/reuse consumers; provisional 30 minutes/280 production-schema lines.
- 03C: one run-local check admission/ownership boundary through completion,
  with real two-process/orphan refusal proof; provisional 30 minutes/190 lines,
  dependent on 03B and requiring adapter confirmation after it.
- 03D: namespaced stage-appropriate observations and review/final reference
  enforcement, including activation/legacy compatibility; 45 minutes/350 lines,
  explicitly SPLIT_REQUIRED with implementation-handoff and review/final
  successor boundaries still to be sized before execution.

The split follows independent guarantees, not individual helper functions.
03B includes producer AND consumer validation; 03C does not claim receipt
authenticity again; 03D does not replace those mechanisms or implement FIX-02
adoption. Earlier requirements remain mapped; no single-flight or semantic
acceptance guarantee is implied by merely implementing 03B. No canonical spec,
runtime code, test, old pilot record, model route or budget was changed in this
planning pass. All successors remain backlog plans with unsatisfied literal
done dependencies; this aggregate remains non-executable SPLIT_REQUIRED.

### Current successor state — 2026-09-07

- 03A is independently accepted offline, C1-C8 pass:
  `.runtime/changerail/offline-fix03a-delta-x54SHO/assessment.json`.
- 03B's complete execution-proof boundary was split into
  [03B1 focused](chrl-fix-03b1-retain-focused-check-proof.md),
  [03B2-P pre_review](chrl-fix-03b2p-retain-pre-review-verification-proof.md) and
  [03B2-F final](chrl-fix-03b2f-retain-final-verification-proof.md).
  All three have accepted independent offline C1-C6 assessments. 03B1's is
  `.runtime/changerail/offline-rereview-fix03b1-4x0gJ2/assessment.json`; P/F
  assessments and repairs are indexed in
  `.runtime/changerail/offline-continue-fix03b2-WkKmHK/completion-report.md`.
  Neither 03B nor 03B2 is a new execution candidate or synthetic done card.
- 03C is implemented and independently accepted offline, C1-C4 pass, no open
  findings. It owns the real check-execution lock, publication boundary,
  validated direct-floor reuse and unresolved-orphan refusal. Do not repeat it.
  Exact evidence: `.runtime/changerail/offline-fix03c-UhUyjW/completion-report.md`
  and `check-04/review/assessment.json` under that root.
- [03D](chrl-fix-03d-bind-acceptance-to-observed-proof.md) remains unimplemented,
  but its operator refinement is complete: one invariant/two ordered Changes
  cover all C1-C4 with the actual plan/receipt/lock/handoff/review/final interfaces.
  The common inventory, typed observations, stage ownership and version activation
  stay together; the historical two-successor proposal remains recorded without
  creating new cards. Estimate 180 minutes/800 production-schema lines is
  informational. Separate implementation authorization is next, not measured
  READY or a runner start in the occupied checkout.
- The latest unchanged-product verification combines 2247 full-run non-live
  passes (74.69% coverage) with the sole failed Xvfb test passing separately.
  The original failed full-run outcome is retained; this is not one exit-zero
  floor or proof of missing 03D behavior. These board
  edits change the fingerprint; prior assessments/logs remain unmodified evidence
  for their reviewed bytes, not a new GO for this documentation delta.
- All offline successors remain unpublished/backlog; their card Result/Log
  records preserve implementation chronology and their original Next text is
  not an instruction to repeat accepted work. The latest sequencing entry point
  is this section and the OSS-00 roadmap. No runner done/admission is inferred.

## Next

No further work in qa-mcp. Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

## Change 1: `chrl-fix-03-define-proof-contract-and-planning-gate`

### Why

Required proof currently depends on instructions and working notes rather than
the same validated declaration across new sessions and planning routes.

### Goal

Define and validate a proportionate plan contract without requiring code or
test results that do not exist at planning time.

### Scope

- Contract extraction/schema, authoring instructions/template and normal/direct admission, with explicit rollout and their isolated tests. This remains a planning boundary until separately sized.

### Acceptance

- The first two requirements and their planning/migration proof targets are satisfied; complete-plan fast paths cannot omit the gate, and no execution result is fabricated to make a plan ready.

### Depends On

- none

## Change 2: `chrl-fix-03-retain-and-validate-delivery-proof`

### Why

A valid verification plan is not observed evidence; current nonempty strings
and after-only fingerprints do not prove a completed check of unchanged bytes.

### Goal

Retain trustworthy verification results and bind the complete declared proof to
the proper implementation/review/floor boundary without introducing new authority.

### Scope

- Check-result retention and identity, duplicate-run prevention, shared review inventory and stage-specific proof validation, plus ordinary/offline/migration fixtures. This remains a planning boundary until separately sized.

### Acceptance

- The third and fourth requirements pass with the real validation and relevant process/file seams; incomplete or changed proof is unconfirmed, semantic adequacy remains reviewed, and source history and ordinary role/budget behavior are preserved.

### Depends On

- Change 1

## Log
- 2026-09-07T07:41:01Z Linked the completed operator-only 03D refinement: all
  C1-C4 stay in one coherent plan with two Changes, typed observed proof and
  pinned stage/version ownership. Separate implementation authorization is next.
  Original aggregate Acceptance/Design/Budget/Changes and prior Log remain
  historical; this aggregate stays non-executable. No implementation or publish.
- 2026-09-07T07:16:05Z Recorded independently accepted offline 03C, C1-C4 pass,
  and composed unchanged-product verification; advanced the current queue to
  03D planning. Preserved original Acceptance/Design/Verify, historical budget
  records and all prior logs. No implementation, adoption, card move or publish.

- 2026-09-07T03:13:08Z Updated current successor state at operator request: independently accepted offline 03A/03B1/P/F are not repeated or marked done; 03C is next, 03D still needs semantic refinement, finalizer stays disabled. Preserved original Acceptance/Design/budget/checkpoints and all prior Log history, while labeling old numeric failures historical under the explicit budget waiver. Board-only reconciliation; no implementation, new verdict, pilot, status move or publication.
- 2026-09-06T07:26:18Z Recorded the operator-authorized common prevention plan after inspecting the template, board/OpenSpec instructions and actual FF/admission/evidence/verdict seams. Only this new backlog aggregate is authored. Working estimate 90 minutes/650 production-schema LOC exceeds current limits: SPLIT_REQUIRED planning assessment, not a measured verdict or implementation authority. No source pilot records or pre-existing changes were altered.
- 2026-09-06T07:31:37Z Planning checks passed: all 16 template sections are present and nonempty, four acceptance groups, two ordered Changes, 16 existing local paths and three explicitly proposed paths checked; whitespace checks passed. Read-only chrl admission exited 3/SPLIT_REQUIRED solely for 90 > 30 expected minutes and 650 > 300 estimated production LOC. No FF/delivery transition or implementation test was run; canonical specs remain unchanged.
- 2026-09-06T07:54:24Z Refined the operator-requested first boundary into CHRL-FIX-03A using existing admission/shell/exact-recovery seams. Recorded its plan-only 30-minute/280-LOC scope and preserved the unrefined execution-proof boundary. Only these planning cards changed; no active-pilot or implementation work occurred.
- 2026-09-06T08:01:35Z CHRL-FIX-03A passed read-only structural/sizing admission (READY, no transition) and explicit plan-mapping checks. The aggregate remains SPLIT_REQUIRED; runtime-proof work is not claimed by its first successor. Instructions, implementation and prior pilot work remain unchanged.
- 2026-09-06T13:03:40Z Operator-authorized second-boundary refinement created backlog plans 03B (terminal result/log integrity, 30 minutes/280 lines), 03C (single-run execution serialization, 30 minutes/190 lines) and 03D (condition-proof binding, SPLIT_REQUIRED at 45 minutes/350 lines). Recorded actual after-only focused versus already start/end-checked floor behavior; kept producer/consumer integrity separate from single-flight and semantic coverage. 03A's offline acceptance, original aggregate Acceptance/Budget/Changes and prior Log entries are preserved. Only these planning cards changed; no implementation, canonical-spec edit, product tests, pilot, model session, FF transition, commit or push ran.

## Cancellation

2026-09-09T18:38:55.554861+00:00 — Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.
