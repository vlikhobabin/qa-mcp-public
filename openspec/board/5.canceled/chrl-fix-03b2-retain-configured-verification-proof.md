# Retain configured verification proof through reuse and final logs

## Status

5.canceled

## Owner

qa-mcp

## Series

chrl-fix-03b2

## Order Index

406.2222

## OpenSpec Stage

SPLIT_REQUIRED; superseded aggregate retained for C1-C6 traceability; use 03B2-P then 03B2-F, not this card for delivery

## Priority

P1

## Source

- `openspec/board/5.canceled/chrl-fix-03b-retain-verifiable-check-results.md`: successor B, covering the configured portions of preserved C1-C6.
- `openspec/board/5.canceled/chrl-fix-03b1-retain-focused-check-proof.md`: owns the sole shared receipt contract/validator and complete focused boundary; this card must consume its actually delivered interface.
- `.runtime/changerail/offline-fix03b-retry-IKbVci/orchestrator-assessment.md`: actual missing-log reuse and malformed/unsafe-reader failures; historical diagnosis, not passing evidence.

## Summary

Superseded aggregate, not a runner input or done dependency. The operator
approved complete pre_review and final lane successors; the original intent,
Acceptance/Verify, budget and Change below remain historical obligations.
Current routing and clause coverage are recorded in Successor Coverage/Next.

Extend 03B1's usable focused proof to existing configured pre-review/final
verification, complete ordered command-set reuse and validated final-log
summary. Preserve the existing aggregate before/after payload comparison and
intentional changed-payload import repair. No new validator or executor.

## Acceptance

### Requirement: Record actual configured execution in the shared contract

#### Scenario: An existing pre-review or final floor executes

- [C1] WHEN a configured verification command runs, THEN its actual run/card/invocation identity, explicit pre_review/final lane, exact configured shell text AND shell invocation, before-payload and UTC start are bound before launch. Terminal records use 03B1's sole `qa-mcp.check-result.v1` validator and preserve actual process exit/signal or spawn/interruption/unknown outcome, UTC finish, duration and after-payload separately from wrapper verdict. Zero-exit drift/incomplete retention fails to the verification caller; missing owner refuses before launch, and the existing aggregate start/end payload check remains enforced.
- [C2] AND configured attempts use exclusive new paths, complete regular size/SHA-256-bound logs and terminal-after-log atomic publication. Malformed/unknown/duplicate-key records, invalid terminal types/dates/durations, running-only, missing/tampered/truncated logs and failed storage cannot establish success; a stable silent zero-byte log can. Storage failure preserves the actual observed process outcome in writable failure evidence or diagnostics without forging success.

### Requirement: Validate complete configured sets before reuse or final parsing

#### Scenario: Floor reuse, final summary or metrics consumes evidence

- [C3] WHEN preverification guards, _successful_verification_matches, preverify/verify or final-log readers consume a configured set, THEN they use the shared safe validator for each record/log and require the exact complete ordered command set, one owning run/card/lane and frozen payload with valid invocation references. Missing/extra/reordered/duplicated/foreign/stale/failed proof refuses reuse; equal command lists do not merge lanes. Aggregate booleans/exit lists alone are not proof. All index/record/log paths are validated component-wise before any content read; final pytest summary parses precisely the same safely validated log bytes, not a reopened path.
- [C4] AND an unchanged valid complete set retains existing reuse semantics without a second child; invalid proof is not a cache hit and only existing authorized callers may execute new attempts. Old records/logs remain byte-identical. Configured metrics keep compatible command/exit/duration/time projections without independently authenticating proof. Real producer -> schema -> wrapper -> aggregate -> reuse -> final-log summary/metrics compose with stable, drift and missing-log controls.

### Requirement: Preserve repair, history and workflow authority

#### Scenario: Legacy verification or deliberate deterministic repair is used

- [C5] WHEN legacy or carried configured evidence is read, THEN it remains historical/unconfirmed without upgrade/cross-run adoption or changes to exact manifests, counters, recovery eligibility, old contexts, verdicts or retained runs. A deliberately authorized import repair may correctly exit zero with changed payload: retain that real outcome and existing repair success, never relabel it unchanged verification proof or impose the verification drift gate on the general shell helper.
- [C6] AND focused proof remains compatible; no duplicate schema/validator, loaded-command execution, condition-proof mapping, single-flight, command/model/budget/role or final-floor ownership change, FIX-02/finalizer enablement, pilot or publication is introduced. Offline completion remains checks/report. Proof asserts endpoint payload/log identity and observed execution only, not semantic test adequacy, no transient edit/revert, hostile-writer resistance or environment reproducibility.

## Scope

- `scripts/changerail/local_delivery.py`: configured wrappers around `run_shell_verification`, `_run_full_floor`, `_successful_verification_matches`, preverification guard, `preverify`/`verify`, `pytest_summary_from_verification` and configured `deterministic_commands` projections. Preserve `run_safe_handoff_repair` semantics, changing it only if a narrow compatibility adapter is necessary and tested.
- `tests/test_local_changerail_delivery.py`: real configured producers/aggregates/logs and repair regression; replace fabricated success only at proof-requiring fixture boundaries.
- `openspec/specs/changerail-consumer-wiring/spec.md`, `docs/development/local-changerail-delivery.md` and this card's implementation Result/Log.
- Reuse 03B1's existing `tools/changerail/schemas/check-result.schema.json` and sole validator without a second schema or structural-validation path. If its delivered interface cannot support this plan, stop and replan explicitly.

## Non-Goals

- Reimplementing focused receipts, global JSON/recovery decoders, another executor, daemon, framework, dependency or configurable verification command source.
- Serialization/orphan policy (03C), condition-proof enforcement (03D), FIX-02 authority or a finalizer repair.
- Live/provider/admin/Windows work, automatic cleanup/migration/adoption, executing receipt/plan text, environment/secret hashing or Git publication.

## Affected Capabilities

- `changerail-consumer-wiring`

## Depends On

- `openspec/board/5.canceled/chrl-fix-03b1-retain-focused-check-proof.md`

Use the actually delivered 03B1 interface; a draft, structural size report or
offline report is not the runner's literal done dependency/clean-start gate.

## Change Set

- `chrl-fix-03b2-deliver-configured-proof-and-reuse`

## Design

Pass lane explicitly from the authorized pre-review/final caller, never from
equal command lists or path substrings. Extend existing configured producers
with 03B1's receipt creation/validation interface. Bind exact shell text plus
actual shell invocation, not a display-only command or an arbitrary command
loaded from historical JSON. The caller's configured command list is authority.

Keep aggregate shapes as readable indexes of ordered attempt references; their
`ok`/exit summaries cannot authorize reuse. The shared validator authenticates
every current terminal receipt and exact log, then the aggregate checks complete
ordered command coverage, lane, owning identity and one frozen payload. Do not
remove existing `_run_full_floor` before/after comparison. A valid success in
one lane is not success in another even when their configured commands match.

Use the shared component-wise safe reader on indexes, records and logs BEFORE
content access, rejecting absolute/traversal/symlink/nonregular paths. Retain
the validated log bytes for `pytest_summary_from_verification`; no check-then-
reopen path race or unchecked fallback. Empty complete output is valid receipt
content; absence of a pytest summary does not fabricate one. Metrics/display
fields remain compatible observations, not alternate proof. Historical exit-
only indexes stay readable/unconfirmed without rewriting the original data.

The general `run_shell_verification` also executes deterministic import repair.
Separate observed process outcome from a verification-specific unchanged-payload
verdict at its caller; do not globally reject an intended repair change. Keep
actual exit/before/after display fields, never present that repair as unchanged
proof. Preserve focused compatibility and all existing authority gates.

Tests exercise real Git, subprocess, safe I/O, schema and digest checks.
`_verification_fixture` currently mocks the shell producer and
`_write_matching_preverification` fabricates exit-only proof: adapt acceptance
fixtures to genuine owner metadata and actual retained attempts, not a fake
success object with a new schema tag. Keep unrelated mocked guard tests useful,
but do not count them as the composed proof regression.

## Delivery Budget

- primary_invariant: Configured floor reuse and final summaries require intact complete current-lane terminal proof without breaking intentional repair.
- expected_wall_minutes: 25
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 1
- estimated_production_loc: 125

## Budget Notes

Incremental estimate 90-125 added production lines using delivered 03B1:
65-85 configured wrappers/explicit lane/aggregate reuse, 25-40 final-log/metrics
adapters. 20-25 minutes includes approximately 6 integration, 7 real fixture/
reuse/final-log/repair matrix, 2 contract docs and 5-10 review/checks/floor.
Tests/docs are elapsed/review work, not excluded effort. No schema duplication,
minification or net-deletion accounting to fit. At the first checkpoint compare
the actual 03B1 interface and remaining effort: if >125 lines/25 minutes is
needed, report the revised estimate and replan before extending this slice;
never raise the configured 300-line/30-minute ceiling or silently borrow 03B1's
unused allowance. A structural READY report is not measured feasibility.

## Canonical Specs

- `openspec/specs/changerail-consumer-wiring/spec.md`

## Verify

Future test locators, not existing or passing proof. Keep real Git payload
hashes, controlled children, schema/digest validation and result/log I/O. Fake
model/network/publication boundaries only. Narrow injected retention faults
and outside-read sentinels may test refusal without replacing real validators.

```json
{
  "schema": "qa-mcp.card-evidence.v1",
  "conditions": [
    {"condition":"C1","seam":"configured wrappers and preserved aggregate drift gate","precondition":"real run/card fixtures in both lanes with stable/silent, zero-exit mutation, nonzero/signal, missing-owner, spawn and interruption cases","action":"execute actual configured wrappers and aggregate with real subprocesses and before/after hashes","expected":"stable control passes its own schema; drift/incomplete execution fails to the caller with actual outcome retained; missing owner prevents spawn and aggregate drift check remains active","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_configured_check_terminal_outcomes"},"stage":"implementation"},
    {"condition":"C2","seam":"configured attempts and shared retention validation","precondition":"actual terminal records plus malformed recursive keys/types/dates/durations, running-only, silent-empty and damaged logs/storage faults","action":"produce attempts and validate fault variants through the unchanged shared validator","expected":"only intact complete terminal proof is usable; exclusive attempts preserve history and retention failure never changes an observed exit into success","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_configured_check_contract_and_retention"},"stage":"implementation"},
    {"condition":"C3","seam":"preverification/reuse guards and safe final pytest summary","precondition":"real complete ordered set plus missing/extra/reordered/duplicated/foreign/stale/failed references, equal lists in different lanes and unsafe index/record/log paths","action":"exercise actual preverify/verify guards, reuse matcher and summary with outside-read/reopen sentinels","expected":"only exact current-lane complete proof reuses; unsafe content is never read and summary uses the exact validated bytes without reopening","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_configured_check_set_and_safe_summary"},"stage":"implementation"},
    {"condition":"C4","seam":"composed configured reuse and metrics","precondition":"counted real configured children with intact proof, drift and missing-log variants; saved original bytes","action":"exercise producer to schema to wrapper to aggregate to reuse to final summary and configured metrics","expected":"valid complete reuse launches no child; invalid proof is no cache hit, metrics remain compatible and original logs/records are unchanged","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_configured_check_composed_reuse"},"stage":"implementation"},
    {"condition":"C5","seam":"historical configured evidence and intentional import repair","precondition":"exact legacy fixture, copied index and real tracked fixture needing the existing deterministic import repair","action":"read historical evidence and execute the real authorized repair path with its actual subprocess and before/after hashes","expected":"legacy remains historical/unconfirmed with original history/accounting intact; intended changed-payload exit zero remains repair success but is not unchanged verification proof","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_configured_check_legacy_and_deliberate_repair"},"stage":"implementation"},
    {"condition":"C6","seam":"shared focused contract and role/publication boundaries","precondition":"final scoped diff, final Result/Log and relevant existing focused/authority guard results","action":"inspect sole validator/schema use and unchanged commands/models/budgets/roles/finalizer guards","expected":"focused contract composes unchanged; no second validator, loaded-command execution, condition mapping, serialization or added authority; limitations are explicit","method":{"kind":"inspection","target":"scripts/changerail/local_delivery.py"},"stage":"review"}
  ],
  "risks": [
    {"kinds":["input_safety"],"applies":true,"decision":"Reuse shared closed validation; safe component-wise index/record/log access precedes all content reads, and final parsing reuses validated bytes.","conditions":["C2","C3"]},
    {"kinds":["mutation","restart"],"applies":true,"decision":"Per-command and aggregate endpoint hashes, explicit terminal outcomes and immutable attempts reject incomplete/stale proof; deliberate repair and historical eligibility stay separate.","conditions":["C1","C2","C4","C5"]},
    {"kinds":["concurrency"],"applies":true,"decision":"Exclusive attempts cannot overwrite history; complete-set validation is not a single-flight or orphan-recovery guarantee, which remains 03C.","conditions":["C2","C3","C6"]},
    {"kinds":["publication"],"applies":true,"decision":"Strengthen existing final evidence consumption without modifying who reviews, runs the floor or publishes; FIX-02 remains disabled.","conditions":["C3","C6"]},
    {"kinds":["external_effects"],"applies":true,"decision":"Configured caller commands remain sole execution authority; fixtures use owned offline subprocesses and never execute recorded plan/proof text.","conditions":["C1","C5","C6"]}
  ]
}
```

Both lanes need stable/silent controls and the applicable shared malformed/
unknown-field/version/recursive-duplicate-key (including escaped spelling)/
boolean-exit/invalid-UTC/negative-duration matrix; spawn/interruption and
log-write/completion-write faults after known exits; running/missing/tampered/
truncated log variants; wrong run/card/invocation/lane/exact-shell/payload;
absolute/traversal/symlink-ancestor/leaf/nonregular index/record/log paths.
Keep validation real and prove refusal before outside content reads.

- Behavioral RED first: a real completed configured set with its log then missing must be refused by the actual reuse reader; also exercise zero-exit drift at the caller before new-field/schema assertions. Retain observed false-success controls, not a schema-name failure.
- Focused final command: `uv run pytest -q tests/test_local_changerail_delivery.py -k 'configured_check or focused_check'`. Collect all planned tests and delivered 03B1 compatibility tests; empty selection is failure.
- Exercise the actual intentional import-repair path plus existing handoff/finalizer/role guards; pin their exact selectors from the dependency interface inventory before edits, not after a green broad count.
- `git diff --check` and `./bin/openspec validate --specs --strict --no-interactive`.
- Retain focused evidence after final Result/Log edits. In measured delivery the outer runner owns fast pre-review checks, independent review and one frozen-payload post-GO floor: `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60`, `uv run python -m compileall -q src tests`, strict specs. Ordinary authorized offline fixes finish with relevant checks/report, not invented handoff or duplicate unchanged floors.

## Related

- `openspec/board/5.canceled/chrl-fix-03b-retain-verifiable-check-results.md`
- `openspec/board/5.canceled/chrl-fix-03c-serialize-verification-attempts.md`
- `openspec/board/5.canceled/chrl-fix-03d-bind-acceptance-to-observed-proof.md`
- `docs/development/local-changerail-delivery.md`

## Result

Board-only successor plan created. The pre-implementation checkpoint now uses
03B1's independently accepted offline interface, rather than its earlier draft:
`.runtime/changerail/offline-rereview-fix03b1-4x0gJ2/assessment.json` records
F1-F3 fixed and C1-C6 pass. Its local source is usable, but this does not satisfy
the runner's literal done dependency or clean-start gate.

Checkpoint outcome: **NO-GO / replan required for the existing 125-line/25-minute
envelope**, before any 03B2 product integration. This is an engineering estimate,
not a deterministic admission error; no runner/FF command was invoked.
The shared schema/validator supports exact shell identity and both lanes, but
the allocator always uses focused-evidence. Reuse needs explicit run/lane/index
context, and its caller inventory includes publish's existing evidence-read
boundary in addition to preverify/verify. Those adaptations and real fixtures
were not sufficiently represented in the old estimate.

Real isolated checkpoint probes retained 4 RED failures and 4 passing controls:
in both lanes a deleted log still reuses, and per-command drift hidden by a
later restoring command still passes the aggregate. Ordinary aggregate drift
is already refused; genuine shared shell/silent records validate successfully.
No product tests or implementation success is claimed by these baseline probes.

Revised working estimate: 140-200 added production lines / 35-45 total minutes
with the full negative/compatibility matrix and review/checks; this is not a
measured bound or permission to raise limits. Preserve the original budget
and configured 300-line/30-minute ceiling. Proposed replan for separate approval:
one complete pre_review proof/reuse/repair-compatible boundary, followed by one
complete final proof/reuse/safe-summary boundary including the publisher's
read-only evidence adapter. Do not ship a shared-core-only slice, create these
siblings automatically, or drop any original C1-C6 obligation.

Inventory, actual command/results, proposed boundaries and preservation audit:
`.runtime/changerail/offline-checkpoint-fix03b2-knAAuZ/checkpoint-report.md`.
Only this Result/Log changed; product/schema/tests/specs, prior reports and the
stopped pilot are preserved. No measured verdict, dependency satisfaction,
admission, card movement, 03B2 implementation, pilot or publication is claimed.

Approved successor-planning outcome: actual backlog cards 03B2-P and 03B2-F
now contain standalone C1-C6, complete Verify/risk matrices, ordered Change
checkpoints and provisional budgets. The old monolithic Change/Verify/budget
above is retained history, not an executable plan or current READY verdict.
This note supersedes the preceding proposed-only/no-siblings instruction after
explicit operator approval, without rewriting the checkpoint or its evidence.
03C/03D now depend on the final successor, transitively requiring pre_review
and 03B1; they no longer wait for this aggregate to become done.

The split is not a smaller-total-effort claim: pre_review's candidate is up to
150 added lines/30 minutes; final's incremental candidate is up to 80/24,
including its own review/floor. Separate lane qualification adds overhead to
the earlier 35-45-minute monolithic estimate. All estimates remain provisional;
the configured 300-line/30-minute per-card ceiling is unchanged. Earlier
implementation/review/checkpoint work stays recorded, not reset or relabeled.

## Successor Coverage

- P: `openspec/board/5.canceled/chrl-fix-03b2p-retain-pre-review-verification-proof.md` — complete pre_review producer, all prerequisite/reuse consumers, metrics and real deliberate repair; depends on actual 03B1.
- F: `openspec/board/5.canceled/chrl-fix-03b2f-retain-final-verification-proof.md` — complete final producer/reuse, existing publish evidence gate, safe-byte summary/receipt and metrics; depends on actual P.

| Preserved parent obligation | Pre-review owner | Final owner |
|---|---|---|
| C1: actual owner/invocation/lane/shell, before launch, real terminal outcome, per-command and aggregate drift, missing owner | P C1 for pre_review, including stop-before-restoring-command | F C1 for final, retaining GO/manifest/preverification prerequisites |
| C2: exclusive attempts, closed sole schema, complete log before terminal, silent/invalid/storage matrix and actual failure outcome | P C2, shared adapter delivered only with usable lane | F C2, same delivered schema/adapter and final-lane matrix |
| C3: exact ordered unique proof, all safe preliminary/repeated owner/index/record/log reads, lane isolation and inert text | P C3 for every preverification guard/reuse/metrics entry | F C3 for final verify/reuse/publish-read and exact validated-byte summary/receipt/metrics; no reopen |
| C4: real producer-to-consumer composition, no repeat child, invalid no-cache, history and compatible metrics | P C4 through actual pre_review guards/metrics; no focused leakage | F C4 through final summary/metrics plus valid/invalid publish evidence gate and unchanged pre-action card/index state |
| C5: historical/carried unconfirmed, no adoption/accounting/eligibility/context rewrite, intentional changed-payload repair | P C5 owns actual real import-repair implementation compatibility and excluded-file preservation | F C5 retains final history and regression-checks delivered P/focused/real-repair behavior |
| C6: focused compatibility, one validator/executor, unchanged authority/commands/budgets/roles/floor, non-goals and endpoint limits | P C6; final remains explicitly untouched legacy during interim | F C6; only publisher evidence consumption changes, never its Git/finalization authority |

Every original clause remains required. A schema/adapter-only checkpoint is
not an independently delivered successor. After P but before F, final behavior
and its known configured-proof gaps remain explicitly legacy, not repaired or
certified by P; P does not enable final publication. Both successors need real
accepted evidence before the parent's configured boundary is complete. 03C,
03D and FIX-02 remain separate; no acceptance-to-proof enforcement is added here.

## Next

No further work in qa-mcp. Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

## Change 1: `chrl-fix-03b2-deliver-configured-proof-and-reuse`

### Why

Focused receipts alone do not fix configured cache hits with missing logs or
unsafe final-log parsing; general repair must remain able to change payload.

### Goal

Deliver complete configured proof/reuse/final consumption using the sole shared
contract while retaining intentional repair and all existing authority gates.

### Scope

This card's configured producers, all dependent readers, fixtures and contracts.

### Ordered Tasks

1. Inspect the actually delivered 03B1 interface and inventory configured producer/index/guard/summary/metrics/repair consumers, plus exact existing test selectors. Retain behavioral missing-log reuse and zero-exit drift RED through actual wrappers before new schema assertions. CHECKPOINT before integration: confirm all remaining work fits 125 incremental lines/25 minutes with tests/docs/review/floor; incompatible interface or overrun means stop/replan, not duplicate a validator.
2. Pass explicit lane/owning identity to shared receipt production; integrate configured wrappers, aggregate complete-set validation, preverification guards and reuse together. Preserve per-command actual outcomes and the existing aggregate start/end comparison. Leave the general repair outcome outside the verification-specific drift gate.
3. Adapt final pytest summary to the exact safely validated bytes and configured metrics to compatible projections. Replace fabricated success at proof-requiring fixture seams with genuinely produced complete records/logs. Prove C1-C4 through the real composed chain, equal-lane-list controls and malformed/path/storage/reuse matrices.
4. Prove real intentional changed-payload import repair, historical byte preservation and focused compatibility for C5/C6; inspect authority/role guards. CHECKPOINT: retain actual total delta/time and full verification allowance, without shifting work to 03C/03D or claiming the parent's proof prematurely.
5. Update configured canonical contract/runbook and this Result/Log; retain focused evidence against final bytes and use only the separately authorized completion boundary. No pilot, finalizer enablement or publication as an offline side effect.

### Acceptance

- C1-C6 are supported by concrete observations; complete configured proof composes with 03B1 without changing the intentional repair contract or execution/publication authority.

### Depends On

- none

## Log

- 2026-09-06T14:18:25Z Created the operator-authorized board-only successor B with actual 03B1 dependency, complete configured/reuse/final-log scope, real repair regression, ordered Tasks/Verify and an incremental 25-minute/125-line candidate envelope. No implementation/admission or publication ran.
- 2026-09-06T16:32:11Z Authorized next-step offline checkpoint: compared the accepted 03B1 interface and inventoried all configured consumers, including publish's evidence-read caller. Isolated real Git/process/schema/log probes: 4 intended RED failures (missing-log reuse and per-command drift across restoration, both lanes), 4 controls passed. Existing 125-line/25-minute plan is not credible for the full surface; engineering estimate 140-200 lines/35-45 minutes triggers NO-GO/replan before integration. Recorded two candidate end-to-end lane boundaries for separate board-only approval; no siblings, product edits, runner/FF admission, model review, pilot or publication.
- 2026-09-06T16:45:59Z Operator approved and created the actual 03B2-P pre_review and dependent 03B2-F final plans. SPLIT_REQUIRED aggregate retained, with original C1-C6/Verify/budget/Change history unchanged and explicit clause-level successor coverage. Provisional P150/30 and F80/24 budgets include separate qualification overhead, not a reset or current READY. Updated 03C/03D dependencies to the actual final successor. Board-only planning; no product/test/spec/schema edits, admission, implementation, model review, pilot or publication.

## Cancellation

2026-09-09T18:38:55.554861+00:00 — Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.
