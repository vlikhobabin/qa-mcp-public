# Retain usable focused-check proof across all existing consumers

## Status

5.canceled

## Owner

qa-mcp

## Series

chrl-fix-03b1

## Order Index

406.2221

## OpenSpec Stage

operator-planned successor; Tasks/Verify drafted; not admitted or implemented

## Priority

P1

## Source

- `openspec/board/5.canceled/chrl-fix-03b-retain-verifiable-check-results.md`: successor A of the preserved C1-C6 split, not the obsolete producer-only Change 1.
- `.runtime/changerail/offline-fix03b-retry-IKbVci/orchestrator-assessment.md`: rejected schema composition, zero-exit drift wrapper success, metrics `KeyError('command')`, malformed terminal validation, unsafe summary read and non-behavioral RED. Retained reports are historical, not this card's passing evidence.

## Summary

Make focused-check success usable only when its owning runner observed terminal
completion against unchanged payload bytes and retained the complete log.
Deliver the shared record contract, focused producer and every affected focused
consumer together. Configured pre-review/final proof remains unchanged until
03B2; this card does not complete the parent's configured obligations.

## Acceptance

### Requirement: Retain actual focused execution and intact terminal proof

#### Scenario: A real focused child completes or fails

- [C1] WHEN an authorized focused check runs, THEN before launch its unique attempt records actual run/card/invocation identity, explicit focused lane, exact argv, UTC start and payload; its terminal record preserves actual exit/signal or explicit spawn/interruption/unknown outcome, UTC finish, nonnegative finite duration and after-payload separately from wrapper verdict. Stable exit zero succeeds; exit zero with drift, incomplete retention or interruption returns nonzero/unconfirmed without falsifying the observed process outcome. Missing owning metadata refuses before launch.
- [C2] AND attempts are exclusively allocated without overwriting history; a complete regular log with byte size/SHA-256 precedes atomic terminal publication. One closed `qa-mcp.check-result.v1` schema and one schema-backed validator accept genuinely produced running/terminal variants and valid silent zero-byte success, while rejecting incomplete success, unknown versions/fields, malformed or duplicate decoded keys at every depth, non-JSON numbers, boolean exits, invalid/non-UTC dates, negative duration and absent/changed/truncated logs. Failed log/record writes cannot certify success; retain the real observed exit in a writable failure record or caller diagnostic.

### Requirement: Switch all focused consumers as one compatible boundary

#### Scenario: Existing readers encounter new, damaged or repeated proof

- [C3] WHEN focused repeat detection, current summaries, metrics or recovery/review projections read a result, THEN the same validator enforces actual owning run/card/invocation/lane/command, current payload and safe record/log identity before assigning current proof. Component-wise no-follow regular-file access precedes reading any record/index/log content, including symlink ancestors; missing/foreign/stale/unsafe proof is unconfirmed. Metrics retain compatible command/exit/duration/time projections without exceptions or independent proof authority; no loaded command or prose is executed.
- [C4] AND intact unchanged focused proof causes the existing repeat refusal with its retained reference and no second child; invalid proof is never a valid-repeat/cache claim. Only existing authorized entrypoints may allocate a new attempt. Original records/logs remain byte-identical. Real producer -> schema -> wrapper -> repeat -> summaries -> metrics -> carried/recovery consumers compose for both stable and drift cases, not merely schema-only or mocked unit controls.

### Requirement: Keep history, remaining lanes and authority unchanged

#### Scenario: Legacy or carried evidence is inspected

- [C5] WHEN old or copied focused evidence is encountered, THEN it remains readable as historical/unconfirmed, never automatically upgraded or adopted as current cross-run proof. Exact manifests, recovery eligibility, counters, verdicts, prior contexts and old run files stay unchanged; an authorized new check writes only to its current run. Configured floor/reuse/final-log behavior and the general intentional-repair API keep their existing contract until 03B2.
- [C6] AND this slice neither binds acceptance conditions to receipts, runs plan locators, adds single-flight, changes command lists/models/budgets/role or final-floor ownership, nor enables FIX-02, finalization, a pilot or publication. Offline implementation ends with relevant checks/report, without fabricated runner context/handoff. Endpoint equality is not a no-transient-edit, malicious-writer, semantic-test-adequacy or all-environment guarantee.

## Scope

- Future owner `scripts/changerail/local_delivery.py`: bounded shared receipt I/O/validation, `run_evidence`, `focused_evidence_summaries`, `deterministic_commands` focused projection, `build_recovery_context` and `build_review_context` focused/carried projection only.
- New `tools/changerail/schemas/check-result.schema.json`; use existing `jsonschema`, no dependency or general executor/module.
- `tests/test_local_changerail_delivery.py`: real fixture producers/consumers and focused regressions below.
- `openspec/specs/changerail-consumer-wiring/spec.md`, `docs/development/local-changerail-delivery.md`: focused contract and explicit configured-lane limitation.
- This card's Result/Log in a separately authorized implementation. Planning here changes no product/test/spec/runbook files.

## Non-Goals

- Configured producers, aggregate floor/cache proof or final pytest summary: 03B2.
- Single-flight, orphan cleanup/retry and exactly-once effects: 03C. Condition-proof binding: 03D.
- Global JSON decoder/recovery-source changes, a manual parallel structural validator, framework refactor, automatic migrations, cross-run adoption, signing, environment/secret hashing or runtime/provider/Windows operations.
- A schema-only or producer-only delivered switch; the shared core is an internal checkpoint, not an independently shippable successor.

## Affected Capabilities

- `changerail-consumer-wiring`

## Depends On

- `openspec/board/5.canceled/chrl-fix-03a-validate-evidence-plans-before-admission.md`

03A's offline acceptance is not a literal done dependency. This live path must
follow its real board transition; no invented done path or clean-start waiver.

## Change Set

- `chrl-fix-03b1-deliver-complete-focused-proof`

## Design

Keep one closed object in the new schema: declare all properties together and
use state conditionals only to require/constrain them. Do not extend a closed
base with `allOf`. Close nested objects; use existing jsonschema validation with
an active FormatChecker and explicit UTC constraint. A bounded decoder rejects
recursive duplicate decoded keys (including escaped spellings) and non-JSON
numeric constants. No second hand-maintained structural validator. Semantic
checks outside the schema cover identity/current payload, safe paths and log
digest/size only. Design the command variant for exact argv and configured
shell identity now; 03B2 must reuse this sole contract/validator.

Require real owning metadata and explicit caller lane; no fallback/null
self-certification, directory-substring inference or arbitrary foreign binding.
Use an opaque invocation/attempt ID and exclusive run-local allocation. Record
running identity before launching the existing subprocess entrypoint. Preserve
actual process exit independently of wrapper failure and never stamp unknown
exit as zero. Retain complete stdout/stderr in the existing concatenation order
(not a claim of temporal interleaving), close the log, then atomically publish
terminal metadata using the existing writer. Retention failure is a failure
even after actual exit zero; diagnostics disclose when durable storage failed.

Safe reads reject traversal/absolute locators, symlink components and
nonregular files before opening content. Use one bounded regular-file reader
for result/index/log bytes and feed those bytes to schema/hash validation.
Return the validated bytes to consumers that need them; do not re-open an
unchecked path. Limits must fail unconfirmed, never hash only a prefix or
silently truncate a log while claiming complete retention.

Switch focused producer, repeat detection, summaries, metrics and carried/
recovery projections together. Keep readable `label`, `command`, `exit_code`,
`duration_seconds`, `observed_at`, `fingerprint`, `log` fields or compatible
projections; absent terminal fields are safe to display. Such fields alone
never authenticate proof. A copied summary is historical/unconfirmed even if
its fingerprint matches. Only a validated record in its actual owning context
may describe observed proof; that does not grant reuse in a new run.

First internal checkpoint is before enabling the new producer format. Retain
behavioral RED, field-to-reader inventory, tested shared schema/reader size,
elapsed time and remaining full integration/tests/docs/review/floor estimate.
Shared core above 190 added production/schema lines or more than 12 elapsed
minutes invalidates the proposed envelope. Stop earlier if measured plus
remaining work projects above 300 lines/30 minutes or needs new authority;
report NO-GO/replan, do not raise limits, delay the checkpoint or ship core
alone. Do not proceed into 03B2 inside this card.

## Delivery Budget

- primary_invariant: Every focused current-success claim uses intact terminal run-bound proof across all affected focused readers.
- expected_wall_minutes: 30
- production_owners: 1
- runtime_contours: 0
- estimated_product_files: 2
- estimated_production_loc: 280

## Budget Notes

Candidate range 220-280 added production/schema lines: schema 60-75, shared
safe decoder/validator/retention helpers 95-115, focused producer and compatible
projections 65-90. Tests/docs count as reviewed work and elapsed effort, not as
hidden free work or a reason to minify schema/count net deletions.
27-30 minutes includes approximately 3 behavioral RED, 9 shared core,
5 complete integration, 5 negative/compatibility cases and 5-8 docs/checks/
independent review/configured floor. This estimate has little margin and is
not measured delivery evidence or permission. The first checkpoint above is
mandatory; report a replan if the full verification allowance cannot fit.

## Canonical Specs

- `openspec/specs/changerail-consumer-wiring/spec.md`

## Verify

Planned locators below do not claim tests exist or pass. Keep real temporary
Git repositories, payload hashing, controlled subprocesses, record/log I/O and
schema/digest validators. Fake model/network/publication boundaries only;
narrow injected storage faults and outside-read sentinels may exercise failure
paths, never replace the validator, payload comparison or subprocess under test.

```json
{
  "schema": "qa-mcp.card-evidence.v1",
  "conditions": [
    {"condition":"C1","seam":"run_evidence terminal result and caller exit","precondition":"real run/card fixture with stable, silent, zero-exit tracked-payload mutation, nonzero, signal, missing-owner, spawn and interruption cases","action":"invoke the existing focused entrypoint with real controlled children and inspect actual outcome plus before/after payload","expected":"stable control succeeds; drift and incomplete execution fail to the caller while retaining actual observed exit or explicit unknown; missing owner prevents spawn","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_focused_check_terminal_outcomes"},"stage":"implementation"},
    {"condition":"C2","seam":"shared schema/reader and terminal-after-log retention","precondition":"genuinely produced running/terminal records, valid empty log and parameterized malformed/schema/log/storage-fault variants","action":"validate the actual producer record and corrupt versions, fields, recursive decoded keys, number/date types, log bytes and writes","expected":"complete stable proof passes its own schema; every invalid/incomplete variant refuses and failed retention preserves the actual process result without success","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_focused_check_contract_and_retention"},"stage":"implementation"},
    {"condition":"C3","seam":"focused summaries/metrics/recovery/review safe consumption","precondition":"real valid receipt plus foreign run/card/invocation/lane/argv, stale payload and unsafe record/index/log paths with outside-read sentinels","action":"pass produced and corrupted records through every affected real consumer","expected":"only current owning proof is authoritative; unsafe paths are refused before any outside read; metrics are compatible and no loaded command executes","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_focused_check_consumers_and_safe_reads"},"stage":"implementation"},
    {"condition":"C4","seam":"end-to-end focused repeat and reader composition","precondition":"counted real child, complete intact proof and missing/tampered/running variants with saved old bytes","action":"exercise producer to schema to caller to repeat to summaries to metrics to carried/recovery projection for stable and drift cases","expected":"valid repeat refuses with retained reference and no child; invalid proof is not reused; old bytes survive and no composition exception is hidden by mocks","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_focused_check_composed_reuse"},"stage":"implementation"},
    {"condition":"C5","seam":"legacy/carried classification and untouched configured/repair boundary","precondition":"exact historical fixture, copied summaries, new current attempt and existing configured/repair controls","action":"read old evidence and run current focused plus existing configured/repair fixture paths","expected":"history is readable/unconfirmed without cross-run upgrade; retained history/accounting stay byte-identical and configured/repair contracts do not change","method":{"kind":"test","target":"tests/test_local_changerail_delivery.py::test_focused_check_legacy_and_lane_boundaries"},"stage":"implementation"},
    {"condition":"C6","seam":"final scoped diff and authority ownership","precondition":"final card Result/Log, focused evidence and current role/finalizer guards","action":"inspect final diff and relevant existing guard results against excluded surfaces and contract limitations","expected":"no added execution/adoption/publication authority, condition mapping, single-flight or configured-lane proof claim; offline completion remains checks/report","method":{"kind":"inspection","target":"scripts/changerail/local_delivery.py"},"stage":"review"}
  ],
  "risks": [
    {"kinds":["input_safety"],"applies":true,"decision":"One closed schema with recursive duplicate-key rejection and component-safe record/index/log reads before content access.","conditions":["C2","C3"]},
    {"kinds":["mutation","restart"],"applies":true,"decision":"Pre-launch identity, actual outcomes, unique attempts and terminal-after-log publication reject drift/incomplete proof without altering historical recovery eligibility.","conditions":["C1","C2","C4","C5"]},
    {"kinds":["concurrency"],"applies":true,"decision":"Exclusive attempt allocation prevents overwrite; unresolved records never imply success. Single-flight and parent-loss handling remain 03C, not promised here.","conditions":["C2","C6"]},
    {"kinds":["publication"],"applies":true,"decision":"Changed evidence projections grant no publisher/finalizer/role authority; configured floor remains unchanged in this slice.","conditions":["C5","C6"]},
    {"kinds":["external_effects"],"applies":true,"decision":"Only existing authorized argv execution is retained; test children are offline/owned and loaded evidence/plan text cannot execute.","conditions":["C1","C3","C6"]}
  ]
}
```

Required matrix includes escaped duplicate keys at nested levels, boolean exits,
bad UTC dates, negative duration, spawn/interruption, log-write/completion-write
faults after a known exit, running-only, silent-empty, missing/tampered/truncated
logs, wrong identity/current payload, traversal/absolute/symlink-ancestor/leaf
and nonregular record/index/log paths. An unchanged valid control accompanies
each invalid class. Assert outside-read refusal order, not just final refusal.

- First RED must reach a real zero-exit payload mutation and assert wrapper failure before new schema/field assertions; retain the failing behavioral result. A schema-name failure is not this regression.
- Focused final command: `uv run pytest -q tests/test_local_changerail_delivery.py -k focused_check`. It must collect every declared test plus parameterized controls; no empty selection counts as success.
- Run relevant existing metrics/recovery/review/configured/repair guards after integration; finalize exact existing selectors from the field-to-reader inventory before edits. Existing mocked producer fixtures are not proof of this card's composed chain.
- `git diff --check` and `./bin/openspec validate --specs --strict --no-interactive`.
- After final Result/Log edits, retain focused evidence. In measured delivery the outer runner owns fast pre-review checks, independent review and one frozen-payload floor after GO: `uv run pytest -q -ra -m "not live" --cov=qa_mcp --cov-report=term-missing --cov-fail-under=60`, `uv run python -m compileall -q src tests`, strict specs. An authorized ordinary offline fix follows its checks/report boundary and does not fabricate handoff or rerun unchanged evidence gratuitously.

## Related

- `openspec/board/5.canceled/chrl-fix-03b-retain-verifiable-check-results.md`
- `openspec/board/5.canceled/chrl-fix-03b2-retain-configured-verification-proof.md`
- `docs/development/local-changerail-delivery.md`

## Result

Ordinary operator-authorized offline implementation completed in the occupied
checkout, without a measured run context or delivery/admission claim. This
Result/Log supersedes the historical planning-stage "not implemented" wording;
the card remains in backlog and 03A's literal done dependency is not fabricated.

- C1: the actual focused argv producer binds owning identity and before-payload before launch; real zero-exit drift now fails to the caller while preserving exit zero. Stable/silent, nonzero/signal, spawn, missing-owner, interruption and retention-failure cases have controlled subprocess fixtures.
- C2: one closed 72-line schema and safe reader, exclusive attempts and terminal-after-log retention; malformed/duplicate-key/type/date/log/path/storage controls cover the shared contract, including genuine running/terminal records and silent logs.
- C3/C4: repeat, summaries, metrics and carried recovery/review projections use the same proof validator or explicitly historical/unconfirmed display. A real producer-to-review-context chain covers stable/drift, intact repeat refusal, invalid-log new attempts and original-byte preservation. No model review is impersonated by context generation.
- C5: legacy observations remain readable/unconfirmed; damaged proof retains safely typed display fields without becoming current authority. Configured/repair functions, exact recovery eligibility and accounting logic remain unchanged; real general-shell changed-payload success and existing repair guards are checked.
- C6: inspection is an offline scoped-diff/AST/preservation audit plus existing guard tests, not an independent measured GO. No condition-binding implementation, configured-floor proof, single-flight, finalizer/pilot enablement or publication was added.

First checkpoint at 2026-09-06T14:45:54Z, before producer activation: 190 shared
production/schema additions, 326 elapsed seconds, behavioral RED (1 failure /
1 stable control) and 30 passing primitive cases. Retained checkpoint inventory
and exact results are under `.runtime/changerail/offline-fix03b1-XaZrq6/`.
Later full candidate harness passed 338 tests; that count precedes the final
display-only compatibility adjustment and is not final-payload proof.
Final focused/supporting/static results and exact preservation/size audit are
retained after these Result/Log edits in that directory's
`after-interruption-fix/final-check.json`; the earlier `final-check.json`
remains evidence of the preceding payload, not the final amended one.
The ordinary offline report is completion evidence only for this authorized
delta; no runner admission, fresh review verdict, final coverage floor, done
transition, handoff, commit or push is claimed. 03B2 remains unimplemented.

The first independent offline review returned `not_accepted`: C1/C4/C5/C6
passed, C2 was incomplete and C3 failed. Its immutable assessment and F1-F3
remain in `.runtime/changerail/offline-review-fix03b1-0zwAqa/assessment.json`;
the earlier implementation claims above are not an acceptance verdict.

The separately authorized F1-F3 repair replaces preliminary owner reads in
metrics, recovery/checkpoint helpers and review context with the existing safe
reader, including subsequent reads of the same owner/carried index. Malformed
or unsafe metadata refuses locally; incomplete metrics metadata reports a
controlled error, while missing legacy recovery plans keep their old policy.
Decoder depth failure becomes the reader's existing refusal; mixed valid and
unconfirmed command observations no longer fail metrics sorting. Real
leaf/ancestor/FIFO owner cases cover metrics, current/previous recovery and
review; the deep-record case covers summaries, metrics and repeat without
executing loaded command text. Silent zero-byte log and record/owner/carried
index FIFO controls observe refusal before content read. A narrow in-memory
S_ISREG mutant must trip each read-order assertion; it never edits product code.

Repair checkpoint: 19 added/14 removed production lines, 274 cumulative added
production/schema lines against the original pre-03B1 snapshot (no net-deletion
discount); 92 amended focused/affected-metrics tests passed before these final
Result/Log edits. Five existing metrics cases now bind their temporary root;
accounting assertions remain unchanged. Final frozen-payload checks, exact
deltas, preserved failed candidates and the 3598-path protection audit are in
`.runtime/changerail/offline-repair-fix03b1-2ioWJR/`. A fresh separately counted
delta reassessment is still required; no acceptance is asserted here. The
original implementation (1447.8 s), first review (574.5 s), repair and re-review
are cumulative work, not a completed 30-minute measured delivery or budget reset.

## Next

No further work in qa-mcp. Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.

## Change 1: `chrl-fix-03b1-deliver-complete-focused-proof`

### Why

The rejected producer/schema switch was neither self-validating nor compatible
with real consumers; a broad passing count missed that composition.

### Goal

Deliver one usable focused proof boundary including every affected reader.

### Scope

Only this card's shared primitives, focused integration, tests and contracts.

### Ordered Tasks

1. Preserve the authorized baseline and inventory each written/read field through producer, repeat, summaries, metrics, recovery and review. Pin genuine run/card fixtures and exact existing guard selectors. Reproduce zero-exit drift behavior before asserting any new schema field; retain RED plus stable/silent controls.
2. Build/test the sole closed schema and bounded safe reader/retention primitives without enabling a new producer format. Prove actual-format running/terminal schema composition and malformed/path/fault controls. CHECKPOINT: record added production/schema lines, elapsed time and remaining full delivery estimate; core >190 lines or >12 minutes, or projected >300/30, means stop and replan. This checkpoint alone cannot be shipped.
3. Integrate the focused producer AND repeat/current summaries/metrics/carried/recovery readers together. Pass actual process outcome separately from wrapper verdict, preserve readable fields and legacy classification, leave configured/repair behavior untouched. Run the full real composed chain, not the mocked floor producer.
4. Complete C1-C5 fault/identity/history matrices and C6 scope/guard inspection preparation. CHECKPOINT: compare actual complete scope/size/time and verification allowance to the original budget; no moving consumer work into 03B2 or raising limits.
5. Update focused canonical contract/runbook and this Result/Log, retain final focused evidence and checks against the final payload. Use only the separately authorized completion boundary; do not proceed into 03B2, the stopped pilot or publication.

### Acceptance

- C1-C6 have concrete declared observations and disclosed boundaries; no focused reader is left on an incompatible new format and no configured-proof completion is claimed.

### Depends On

- none

## Log

- 2026-09-06T14:18:25Z Created the operator-authorized board-only successor A with complete focused producer/consumer scope, behavioral regression matrix, ordered Tasks/Verify and a 30-minute/280-line candidate envelope plus early 190-line/12-minute stop. Parent C1-C6 remain intact; no implementation/admission or publication ran.
- 2026-09-06T14:57:48Z Ordinary offline implementation: reached behavioral RED before schema assertions, passed the pre-activation 190-line/326-second checkpoint, then integrated the complete focused producer/consumer boundary. Added real process/schema/hash/log/metrics/recovery/review-context and fault tests; updated focused contract/runbook without touching configured proof or authority. Candidate 338-test harness passed before the final display compatibility adjustment; final post-Result/Log checks and exact inherited-work preservation are retained separately. No measured delivery, model review, handoff, pilot, board move or publication ran.
- 2026-09-06T15:02:03Z First frozen-payload offline checks passed (52 focused, 286 supporting, compilation, 70 specs and wiring; 258 production/schema additions, 1295.5 seconds). Final inspection then added explicit KeyboardInterrupt handling for terminal/failure-record writes, preserving the observed exit in diagnostics when storage remains unwritable. Retain the earlier successful evidence unchanged and reverify the amended payload after this Log entry; no authority or configured-lane changes.
- 2026-09-06T15:42:00Z Separately authorized offline F1-F3 repair: retained first review NO-acceptance and exact before-state, reproduced owner-read/depth failures, repaired the local safe-consumer boundary and added guard-sensitive nonregular evidence. Amended focused/affected-metrics candidate: 92 passed. Freeze these Result/Log edits before final focused/supporting/static checks and one fresh counted offline delta review. Keep backlog, old evidence, stopped pilot, configured lane and publication authority unchanged; no runner GO/floor/handoff or 03B2 implementation.

## Cancellation

2026-09-09T18:38:55.554861+00:00 — Canceled by explicit operator instruction: this repository consumes only the executable ChangeRail distribution. ChangeRail development, repair and tests belong to its source repository. Cancellation is not implementation or acceptance proof.
